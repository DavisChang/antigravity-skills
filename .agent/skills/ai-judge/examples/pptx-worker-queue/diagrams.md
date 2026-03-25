# Technical Diagrams — PPTX Worker Queue on AWS EKS

## 1. Overview: Scheduled Path vs Manual Rerun

```mermaid
flowchart TB
  subgraph schedule["Scheduled Path"]
    EB[EventBridge Scheduler]
    API_S[Scheduler Target: Internal API or Lambda]
    EB --> API_S
    API_S --> CREATE1["Create Job Record\nDynamoDB jobs / job_runs"]
    CREATE1 --> SEND1["Send SQS Message\nwith job_id / run_id"]
  end

  subgraph manual["Manual Rerun (No duplicate scheduling)"]
    U[User / Ops]
    API_M[Job API Gateway]
    U --> API_M
    API_M --> CREATE2["Create new job_runs row\nnew run_id"]
    CREATE2 --> SEND2["Send SQS"]
  end

  SEND1 --> Q[(SQS Standard)]
  SEND2 --> Q

  Q --> KEDA[KEDA ScaledObject\nbased on ApproximateNumberOfMessages]
  KEDA --> WK[EKS Worker Deployment]

  WK --> PROC["Read S3 Input\nConvert PPTX\nWrite S3 Output"]
  PROC --> DDB[(DynamoDB\nUpdate jobs / job_runs)]
  PROC --> S3[(S3 Input/Output)]

  WK -.->|Failed| RETRY{Retriable?}
  RETRY -->|Yes| Q
  RETRY -->|No / Limit Exceeded| DLQ[(SQS DLQ)]
  DLQ --> OPS[Manual Review / Fix Code]
  OPS --> API_M
```

---

## 2. Sequence Diagram: Single Run (Includes Visibility and State)

```mermaid
sequenceDiagram
  autonumber
  participant EB as EventBridge Scheduler
  participant API as Job Service API
  participant DDB as DynamoDB
  participant SQS as SQS Standard
  participant W as EKS Worker
  participant S3 as S3

  EB->>API: Trigger "Create and Enqueue" (or via Lambda)
  API->>DDB: Put jobs + job_runs / status=pending
  API->>SQS: SendMessage {job_id, run_id, ...}
  SQS-->>W: ReceiveMessage (visibility timeout)
  W->>DDB: Update job_runs / status=running
  W->>S3: GetObject Input PPTX
  W->>W: Conversion Processing
  W->>S3: PutObject Output
  W->>DDB: Update job_runs / status=succeeded + artifact refs
  W->>SQS: DeleteMessage

  alt Process failed and retriable
    W->>DDB: Record attempt / error_code
    Note over W,SQS: Message returns to queue after visibility timeout expires\nor worker actively drops visibility (re-enqueue upon visibility expiration)
  else Failed and limit reached, enters DLQ
    W->>DDB: status=failed
    Note over SQS,DLQ: SQS moves to DLQ based on maxReceiveCount policy
  end
```

---

## 3. Failure, Retry, DLQ, Rerun after Code Fix

```mermaid
flowchart LR
  A[Worker Processing Failed] --> B{Retry Count\nUnder Limit?}
  B -->|Yes| C[Exponential Backoff\nExtend visibility\nWait for re-enqueue]
  C --> Q[(SQS)]
  B -->|No| D[(DLQ)]
  D --> E[Alert / Manual]
  E --> F[Fix Code / Fix Data]
  F --> G[API Manual Rerun]
  G --> H["Create job_runs\nnew run_id\nrerun_of_run_id = old run_id"]
  H --> Q
```

**Semantics Note:** rerun = new `run_id`; old run is kept in `job_runs` for auditing;  
Schedules are not re-triggered by reruns; new runs are only created via API.

---

## 4. Deployment and Identity (IRSA)

```mermaid
flowchart TB
  subgraph EKS["EKS Cluster"]
    subgraph worker["Namespace: pptx-worker"]
      POD[Pod: Worker]
      SA["ServiceAccount\n(IRSA annotation)"]
      POD --> SA
    end
    KEDA_CTL[KEDA Controller\nNamespace: keda]
    NP[NetworkPolicy\nOptional]
    KEDA_CTL -->|HPA / Scale| POD
  end

  SA -->|AssumeRoleWithWebIdentity| IAM[IAM Role]
  IAM --> SQS_R["SQS:\nReceiveMessage\nDeleteMessage\nChangeMessageVisibility"]
  IAM --> S3_R["S3:\nGetObject inputs\nPutObject outputs"]
  IAM --> DDB_R["DynamoDB:\nGetItem / PutItem / UpdateItem\njobs, job_runs"]
  IAM --> SM["Secrets Manager:\nGetSecretValue"]

  subgraph ext["AWS Managed Services"]
    SQS_Q[(SQS Standard + DLQ)]
    DDB[(DynamoDB)]
    S3[(S3)]
    EB[EventBridge Scheduler]
    SM_S[Secrets Manager]
  end

  EB --> API_L[Job API / Lambda]
  API_L --> DDB
  API_L --> SQS_Q
  SQS_Q --> KEDA_CTL
```

---

## 5. Job State Machine

```mermaid
stateDiagram-v2
  [*] --> pending : API creates job_runs\nSQS sends message

  pending --> running : Worker ReceiveMessage\nDDB ConditionUpdate

  running --> succeeded : Conversion completed\nS3 write success\nDDB updated

  running --> failed : Processing failed\nRetry limit exceeded

  running --> pending : Visibility timeout expires\nReturns to SQS (auto-retry)

  failed --> pending : Manual rerun\nNew run_id

  succeeded --> [*]
  failed --> dead : Enters DLQ\nManual intervention
  dead --> pending : Rerun after code fix\nNew run_id
```

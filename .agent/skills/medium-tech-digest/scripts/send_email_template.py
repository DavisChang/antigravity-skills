import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

def send_digest_email(sender_email, sender_password, recipient_email, subject, body_markdown):
    """
    Sends a styled HTML email with the digest content.
    """
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = recipient_email
    msg['Subject'] = subject

    # Simple Markdown to HTML conversion (or just send as text if preferred)
    # For a real agent script, consider using a library like 'markdown' if available,
    # or just wrap in <pre> tags for simplicity in this template.
    html_content = f"""
    <html>
      <body>
        <h2>Weekly Tech Digest</h2>
        <div style="font-family: sans-serif;">
          {body_markdown.replace(chr(10), '<br>')}
        </div>
      </body>
    </html>
    """

    msg.attach(MIMEText(html_content, 'html'))

    try:
        # Example for Gmail (requires App Password)
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(sender_email, sender_password)
            server.send_message(msg)
        print("Email sent successfully!")
    except Exception as e:
        print(f"Failed to send email: {e}")

if __name__ == "__main__":
    # Example Usage
    # In a real scenario, the agent would fill these in or prompt the user.
    SENDER = os.getenv("EMAIL_USER")
    PASSWORD = os.getenv("EMAIL_PASS") # App Password
    RECIPIENT = "user@example.com"
    
    SAMPLE_CONTENT = """
    # Top AI Articles
    1. **GPT-5 Rumors** - Analysis of leaks...
    2. **React + AI** - Building a chatbot...
    """

    if not SENDER or not PASSWORD:
        print("Please set EMAIL_USER and EMAIL_PASS environment variables.")
    else:
        send_digest_email(SENDER, PASSWORD, RECIPIENT, "Your Weekly Tech Digest", SAMPLE_CONTENT)

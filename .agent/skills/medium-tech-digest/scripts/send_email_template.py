"""
Medium Tech Digest — Email Sender

Reads a digest.md file and sends it as a styled HTML email via SMTP.

Usage:
    python send_email_template.py --digest path/to/digest.md --to recipient@example.com

Environment variables (preferred over CLI flags for credentials):
    EMAIL_USER      — sender email address
    EMAIL_PASS      — app password (Gmail: https://support.google.com/accounts/answer/185833)
    EMAIL_RECIPIENT — fallback recipient if --to is not provided

Supported SMTP providers (set via --provider):
    gmail   (default) — smtp.gmail.com:465
    outlook           — smtp.office365.com:587
    custom            — requires --smtp-host and --smtp-port
"""

import argparse
import os
import re
import smtplib
import sys
from datetime import date
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path


# ---------------------------------------------------------------------------
# Markdown → HTML (lightweight, no external deps)
# ---------------------------------------------------------------------------

def markdown_to_html(md: str) -> str:
    """Convert a subset of Markdown to HTML for email rendering."""
    lines = md.splitlines()
    html_lines = []
    in_code_block = False

    for line in lines:
        # Fenced code blocks
        if line.strip().startswith("```"):
            if in_code_block:
                html_lines.append("</code></pre>")
                in_code_block = False
            else:
                html_lines.append("<pre><code>")
                in_code_block = True
            continue

        if in_code_block:
            html_lines.append(_escape(line))
            continue

        # ATX headings
        h_match = re.match(r"^(#{1,6})\s+(.*)", line)
        if h_match:
            level = len(h_match.group(1))
            content = _inline(h_match.group(2))
            html_lines.append(f"<h{level}>{content}</h{level}>")
            continue

        # Horizontal rules
        if re.match(r"^-{3,}$", line.strip()):
            html_lines.append("<hr>")
            continue

        # Blockquotes
        if line.startswith("> "):
            html_lines.append(f"<blockquote>{_inline(line[2:])}</blockquote>")
            continue

        # Empty line → paragraph break
        if line.strip() == "":
            html_lines.append("<br>")
            continue

        html_lines.append(f"<p>{_inline(line)}</p>")

    return "\n".join(html_lines)


def _escape(text: str) -> str:
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _inline(text: str) -> str:
    """Process inline Markdown: bold, italic, inline code, links."""
    # Inline code
    text = re.sub(r"`([^`]+)`", r"<code>\1</code>", text)
    # Bold
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    # Italic
    text = re.sub(r"\*(.+?)\*", r"<em>\1</em>", text)
    # Links
    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', text)
    return text


# ---------------------------------------------------------------------------
# HTML email template
# ---------------------------------------------------------------------------

EMAIL_TEMPLATE = """\
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{subject}</title>
<style>
  body {{
    margin: 0; padding: 0;
    background-color: #f4f4f7;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
    color: #2d2d2d;
  }}
  .wrapper {{
    max-width: 680px;
    margin: 32px auto;
    background: #ffffff;
    border-radius: 8px;
    overflow: hidden;
    box-shadow: 0 2px 8px rgba(0,0,0,0.08);
  }}
  .header {{
    background: #1a1a2e;
    padding: 32px 40px;
    color: #ffffff;
  }}
  .header h1 {{
    margin: 0;
    font-size: 22px;
    font-weight: 700;
    letter-spacing: -0.3px;
  }}
  .header p {{
    margin: 6px 0 0;
    font-size: 13px;
    color: #a0a0c0;
  }}
  .content {{
    padding: 32px 40px;
    line-height: 1.7;
    font-size: 15px;
  }}
  .content h2 {{
    font-size: 18px;
    font-weight: 700;
    color: #1a1a2e;
    border-bottom: 2px solid #e8e8f0;
    padding-bottom: 6px;
    margin-top: 36px;
  }}
  .content h3 {{
    font-size: 15px;
    font-weight: 600;
    color: #333;
    margin-bottom: 4px;
  }}
  .content a {{
    color: #4a6cf7;
    text-decoration: none;
  }}
  .content a:hover {{
    text-decoration: underline;
  }}
  .content blockquote {{
    margin: 4px 0 12px;
    padding: 4px 0;
    color: #777;
    font-size: 13px;
    font-style: italic;
    border: none;
  }}
  .content strong {{
    color: #1a1a2e;
  }}
  .content code {{
    background: #f0f0f5;
    padding: 2px 6px;
    border-radius: 4px;
    font-size: 13px;
    font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace;
  }}
  .content pre {{
    background: #f0f0f5;
    padding: 16px;
    border-radius: 6px;
    overflow-x: auto;
    font-size: 13px;
  }}
  .content hr {{
    border: none;
    border-top: 1px solid #e8e8f0;
    margin: 32px 0;
  }}
  .footer {{
    background: #f9f9fc;
    padding: 20px 40px;
    font-size: 12px;
    color: #999;
    text-align: center;
    border-top: 1px solid #e8e8f0;
  }}
</style>
</head>
<body>
  <div class="wrapper">
    <div class="header">
      <h1>📰 Medium Tech Digest</h1>
      <p>Weekly roundup · {date}</p>
    </div>
    <div class="content">
      {body}
    </div>
    <div class="footer">
      This digest was generated by the Antigravity Agent.<br>
      Articles sourced from <a href="https://medium.com">Medium.com</a>.
    </div>
  </div>
</body>
</html>
"""


# ---------------------------------------------------------------------------
# SMTP providers
# ---------------------------------------------------------------------------

SMTP_PROVIDERS = {
    "gmail": {"host": "smtp.gmail.com", "port": 465, "use_ssl": True},
    "outlook": {"host": "smtp.office365.com", "port": 587, "use_ssl": False},
}


# ---------------------------------------------------------------------------
# Core send function
# ---------------------------------------------------------------------------

def send_digest_email(
    sender: str,
    password: str,
    recipient: str,
    subject: str,
    digest_path: str,
    provider: str = "gmail",
    smtp_host: str = None,
    smtp_port: int = None,
) -> None:
    digest_content = Path(digest_path).read_text(encoding="utf-8")
    body_html = markdown_to_html(digest_content)

    html_email = EMAIL_TEMPLATE.format(
        subject=subject,
        date=date.today().strftime("%B %d, %Y"),
        body=body_html,
    )

    msg = MIMEMultipart("alternative")
    msg["From"] = sender
    msg["To"] = recipient
    msg["Subject"] = subject
    msg.attach(MIMEText(digest_content, "plain", "utf-8"))
    msg.attach(MIMEText(html_email, "html", "utf-8"))

    cfg = SMTP_PROVIDERS.get(provider)
    host = smtp_host or (cfg["host"] if cfg else None)
    port = smtp_port or (cfg["port"] if cfg else None)
    use_ssl = cfg["use_ssl"] if cfg else False

    if not host or not port:
        raise ValueError(
            f"Unknown provider '{provider}'. Use --smtp-host and --smtp-port for custom SMTP."
        )

    print(f"Connecting to {host}:{port} ({'SSL' if use_ssl else 'STARTTLS'})...")
    try:
        if use_ssl:
            with smtplib.SMTP_SSL(host, port) as server:
                server.login(sender, password)
                server.send_message(msg)
        else:
            with smtplib.SMTP(host, port) as server:
                server.ehlo()
                server.starttls()
                server.login(sender, password)
                server.send_message(msg)
        print(f"Email sent successfully to {recipient}.")
    except smtplib.SMTPAuthenticationError:
        print("Authentication failed. Check EMAIL_USER / EMAIL_PASS.", file=sys.stderr)
        sys.exit(1)
    except Exception as exc:
        print(f"Failed to send email: {exc}", file=sys.stderr)
        sys.exit(1)


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Send a Medium Tech Digest as a styled HTML email."
    )
    parser.add_argument(
        "--digest",
        default="digest.md",
        help="Path to the digest Markdown file (default: digest.md)",
    )
    parser.add_argument(
        "--to",
        dest="recipient",
        default=os.getenv("EMAIL_RECIPIENT"),
        help="Recipient email address (or set EMAIL_RECIPIENT env var)",
    )
    parser.add_argument(
        "--subject",
        default=f"Medium Tech Digest — {date.today().strftime('%Y-%m-%d')}",
        help="Email subject line",
    )
    parser.add_argument(
        "--provider",
        choices=list(SMTP_PROVIDERS.keys()) + ["custom"],
        default="gmail",
        help="SMTP provider (default: gmail)",
    )
    parser.add_argument("--smtp-host", help="Custom SMTP host (for --provider custom)")
    parser.add_argument("--smtp-port", type=int, help="Custom SMTP port")
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    sender = os.getenv("EMAIL_USER")
    password = os.getenv("EMAIL_PASS")

    if not sender or not password:
        print(
            "Error: EMAIL_USER and EMAIL_PASS environment variables must be set.",
            file=sys.stderr,
        )
        sys.exit(1)

    if not args.recipient:
        print(
            "Error: Recipient not specified. Use --to or set EMAIL_RECIPIENT env var.",
            file=sys.stderr,
        )
        sys.exit(1)

    if not Path(args.digest).exists():
        print(f"Error: Digest file not found: {args.digest}", file=sys.stderr)
        sys.exit(1)

    send_digest_email(
        sender=sender,
        password=password,
        recipient=args.recipient,
        subject=args.subject,
        digest_path=args.digest,
        provider=args.provider,
        smtp_host=args.smtp_host,
        smtp_port=args.smtp_port,
    )


if __name__ == "__main__":
    main()

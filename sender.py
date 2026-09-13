import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from config import GMAIL_USER, GMAIL_APP_PASSWORD, RECIPIENT_EMAIL, SMTP_HOST, SMTP_PORT

def send_email(subject: str, html_content: str, plain_text_content: str, recipient: str | None = None) -> bool:
    """
    Sends an email using Gmail SMTP and an App Password.
    Returns True on success, False or raises Exception on failure.
    """
    to_addr = recipient or RECIPIENT_EMAIL
    
    if not GMAIL_USER or not GMAIL_APP_PASSWORD:
        raise ValueError(
            "Missing Gmail credentials! Please set GMAIL_USER and GMAIL_APP_PASSWORD."
        )
    if not to_addr:
        raise ValueError("Missing recipient email address! Please set RECIPIENT_EMAIL.")

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = f"Daily News Digest <{GMAIL_USER}>"
    msg["To"] = to_addr

    # Attach plain text first, then HTML (email clients prefer the last attached format)
    part_text = MIMEText(plain_text_content, "plain", "utf-8")
    part_html = MIMEText(html_content, "html", "utf-8")

    msg.attach(part_text)
    msg.attach(part_html)

    print(f"📧 Connecting to {SMTP_HOST}:{SMTP_PORT} via SSL...")
    try:
        with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT, timeout=20) as server:
            server.login(GMAIL_USER, GMAIL_APP_PASSWORD.replace(" ", ""))
            server.send_message(msg)
        print(f"✅ Email successfully delivered to {to_addr}!")
        return True
    except smtplib.SMTPAuthenticationError:
        print("❌ Gmail Authentication Error: Please ensure you are using a 16-character App Password (not your normal Google account password).")
        raise
    except Exception as e:
        print(f"❌ Failed to send email: {e}")
        raise

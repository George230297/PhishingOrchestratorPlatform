import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.models.infrastructure import SendingNode

class EmailSender:
    async def send_email(self, node: SendingNode, to_email: str, subject: str, html_content: str) -> bool:
        message = MIMEMultipart("alternative")
        message["Subject"] = subject
        message["From"] = f"Security Alert <noreply@{node.smtp_host}>"
        message["To"] = to_email

        part = MIMEText(html_content, "html")
        message.attach(part)

        try:
            # Note: Assuming standard SMTP for this template.
            # In production, handle SSL/TLS and auth based on node credentials.
            await aiosmtplib.send(
                message,
                hostname=str(node.ip_address) if node.ip_address else node.smtp_host,
                port=587,
                start_tls=True,
                # username=..., password=... 
            )
            return True
        except Exception as e:
            print(f"Error sending email via node {node.id}: {e}")
            return False

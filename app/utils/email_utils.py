import aiosmtplib
from email.message import EmailMessage
from app.core.config import get_settings

settings = get_settings()

async def send_email_async(to_email: str, subject: str, body: str, html: str | None = None):
    msg = EmailMessage()
    msg["To"] = to_email
    msg["Subject"] = subject
    if html:
        msg.set_content(body)
        msg.add_alternative(html, subtype="html")
    else:
        msg.set_content(body)

    await aiosmtplib.send(
        msg,
        hostname=settings.SMTP_HOST,
        port=int(settings.SMTP_PORT),
        username=settings.SMTP_USER,
        password=settings.SERVER_PASSWORD,
        start_tls=True,
        sender=settings.SMTP_FROM
    )
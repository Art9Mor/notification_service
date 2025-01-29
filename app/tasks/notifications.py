import asyncio
from app.core.celery import celery_app
from app.db.base import get_db
from app.db.models import NotificationLogs
from app.core.config import settings
import httpx
import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


async def send_email(recipient: str, message: str):
    """
    Асинхронная функция для отправки email.
    """
    try:
        msg = MIMEMultipart()
        msg['From'] = settings.EMAIL_USER
        msg['To'] = recipient
        msg['Subject'] = 'Уведомление'
        msg.attach(MIMEText(message, 'plain'))

        async with aiosmtplib.SMTP(hostname=settings.EMAIL_SERVER, port=settings.EMAIL_PORT) as server:
            await server.starttls()
            await server.login(settings.EMAIL_USER, settings.EMAIL_PASSWORD)
            await server.sendmail(settings.EMAIL_USER, recipient, msg.as_string())
            print(f"Email отправлен на {recipient}")
    except Exception as e:
        print(f"Ошибка отправки email на {recipient}: {e}")


async def send_telegram_message(recipient: str, message: str):
    """
    Асинхронная функция для отправки сообщения в Telegram.
    """
    try:
        url = f"{settings.TELEGRAM_API_URL}?chat_id={recipient}&text={message}"
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            if response.status_code == 200:
                print(f"Telegram-сообщение отправлено на {recipient}")
            else:
                print(f"Ошибка отправки Telegram-сообщения на {recipient}")
    except Exception as e:
        print(f"Ошибка отправки Telegram-сообщения на {recipient}: {e}")


async def process_notification(message: str, recipients: list[str], notification_id: int):
    """
    Асинхронная обработка уведомлений (отправка через email или Telegram).
    """
    async with get_db() as db:
        for recipient in recipients:
            status = "успешно"
            try:
                if recipient.isdigit():
                    await send_telegram_message(recipient, message)
                else:
                    await send_email(recipient, message)
            except Exception:
                status = "ошибка"
            finally:
                log = NotificationLogs(notification_id=notification_id, status=status)
                db.add(log)
                await db.commit()


@celery_app.task
def send_notification_task(message: str, recipients: list[str], notification_id: int) -> None:
    """
    Задача Celery для отправки уведомлений через email или Telegram.
    """
    asyncio.run(process_notification(message, recipients, notification_id))

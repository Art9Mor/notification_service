from app.core.celery import celery_app
from app.db.base import get_db
from sqlalchemy.orm import Session
from app.db.models import NotificationLogs

def send_notification_task(message: str, recipients: list[str], notification_id: int) -> None:
    """
    Задача Celery для отправки уведомлений через email или Telegram.
    """
    db: Session = next(get_db())
    for recipient in recipients:
        status = "успешно"
        try:
            if recipient.isdigit():
                print(f"Отправка Telegram-сообщения на {recipient}: {message}")
            else:
                print(f"Отправка Email на {recipient}: {message}")
        except Exception:
            status = "ошибка"
        finally:
            log = NotificationLogs(notification_id=notification_id, status=status)
            db.add(log)
            db.commit()
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, EmailStr, validator
from typing import List, Union
from sqlalchemy.orm import Session
from app.db.models import Notification, NotificationLogs
from app.tasks.notifications import send_notification_task
from app.db.base import get_db
import re

router = APIRouter()

class NotificationRequest(BaseModel):
    """
    Схема для запроса на отправку уведомления.
    """
    message: str
    recipient: Union[str, List[str]]
    delay: int

    @validator('recipient', each_item=True)
    def validate_recipient(cls, v):
        if isinstance(v, str):
            if '@' in v:
                if not re.match(r"[^@]+@[^@]+\.[^@]+", v):
                    raise ValueError("Некорректный email")
            elif not v.isdigit():
                raise ValueError("Номер Telegram должен быть числом")
        return v

    @validator('delay')
    def validate_delay(cls, v):
        """
        Проверка на допустимые значения для задержки.
        """
        if v not in [0, 1, 2]:
            raise ValueError("Задержка должна быть 0, 1 или 2")
        return v

def delay_to_seconds(delay: int) -> int:
    """
    Преобразует значение задержки в секунды:
    0 - немедленно, 1 - 1 час, 2 - 1 день.
    """
    if delay == 0:
        return 0
    elif delay == 1:
        return 3600
    elif delay == 2:
        return 86400

@router.post("/notify/")
async def notify(request: NotificationRequest, db: Session = Depends(get_db)) -> dict:
    """
    Обрабатывает запрос на отправку уведомления и добавляет его в базу данных.
    """
    if isinstance(request.recipient, str):
        recipients = [request.recipient]
    else:
        recipients = request.recipient

    notification = Notification(
        message=request.message,
        recipient=", ".join(recipients),
        delay=request.delay
    )
    db.add(notification)
    db.commit()
    db.refresh(notification)

    delay_in_seconds = delay_to_seconds(request.delay)

    send_notification_task.apply_async((request.message, recipients, notification.id), countdown=delay_in_seconds)

    return {"status": "уведомление запланировано", "id": notification.id}

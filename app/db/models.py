from sqlalchemy import Column, Integer, String, DateTime, Text
from datetime import datetime
from base import Base

class Notification(Base):
    """
    Модель для хранения уведомления
    """
    __tablename__ = 'notifications'
    id = Column(Integer, primary_key=True, index=True)
    message = Column(Text, nullable=False)
    recipient = Column(String(150), nullable=False)
    delay = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    status = Column(String(50), default='в ожидании')

class NotificationLogs(Base):
    """
    Модель для хранения логов отправки уведомлений.

    """
    __tablename__ = 'notification_logs'
    id = Column(Integer, primary_key=True, index=True)
    notification_id = Column(Integer, nullable=False)
    status = Column(String(50), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)

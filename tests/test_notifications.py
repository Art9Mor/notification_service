import pytest
import asyncio
from unittest.mock import patch, MagicMock
from app.core.celery import celery_app
from app.core.config import settings
from app.tasks.notifications import send_email, send_telegram_message, process_notification


@pytest.mark.asyncio
async def test_send_email_success():
    with patch('aiosmtplib.SMTP') as mock_smtp:
        mock_smtp_instance = MagicMock()
        mock_smtp.return_value = mock_smtp_instance
        mock_smtp_instance.starttls.return_value = asyncio.Future()
        mock_smtp_instance.starttls.return_value.set_result(None)
        mock_smtp_instance.login.return_value = asyncio.Future()
        mock_smtp_instance.login.return_value.set_result(None)
        mock_smtp_instance.sendmail.return_value = asyncio.Future()
        mock_smtp_instance.sendmail.return_value.set_result(None)

        await send_email("test@example.com", "Test message")

        mock_smtp_instance.sendmail.assert_called_once_with(settings.EMAIL_USER, "test@example.com", any)


@pytest.mark.asyncio
async def test_send_telegram_message_success():
    with patch('httpx.AsyncClient.get') as mock_get:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_get.return_value = asyncio.Future()
        mock_get.return_value.set_result(mock_response)

        await send_telegram_message("123456", "Test message")

        mock_get.assert_called_once_with(
            f"{settings.TELEGRAM_API_URL}?chat_id=123456789&text=Test message"
        )


@pytest.mark.asyncio
async def test_process_notification_success():
    with patch('app.notifications.send_email') as mock_send_email, \
            patch('app.notifications.send_telegram_message') as mock_send_telegram_message, \
            patch('app.db.base.get_db') as mock_get_db:
        mock_send_email.return_value = asyncio.Future()
        mock_send_email.return_value.set_result(None)
        mock_send_telegram_message.return_value = asyncio.Future()
        mock_send_telegram_message.return_value.set_result(None)

        mock_db = MagicMock()
        mock_get_db.return_value.__aenter__.return_value = mock_db

        message = "Test message"
        recipients = ["test@example.com", "12345"]
        notification_id = 1

        await process_notification(message, recipients, notification_id)

        mock_send_email.assert_called_once_with("test@example.com", "Test message")
        mock_send_telegram_message.assert_called_once_with("1234", "Test message")

        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()


@pytest.mark.asyncio
async def test_send_notification_task():
    with patch('app.notifications.process_notification') as mock_process_notification:
        mock_process_notification.return_value = asyncio.Future()
        mock_process_notification.return_value.set_result(None)

        message = "Test message"
        recipients = ["test@example.com", "123456"]
        notification_id = 1

        await celery_app.send_notification_task(message, recipients, notification_id)

        mock_process_notification.assert_called_once_with(message, recipients, notification_id)

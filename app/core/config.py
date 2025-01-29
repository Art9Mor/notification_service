import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    """
    Класс для хранения настроек приложения.
    """
    DATABASE_URL = os.getenv('DATABASE_Url', 'sqllite:///./notifications.db')
    CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0')
    CELERY_BACKEND_URL = os.getenv('CELERY_BACKEND_URL', 'redis://localhost:6379/0')

settings = Settings()

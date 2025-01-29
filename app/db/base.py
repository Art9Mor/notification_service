from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

Base = declarative_base()
engine = create_async_engine(settings.DATABASE_URL, echo=True)
SessionLocal = sessionmaker(bind=engine,
                            class_=AsyncSession,
                            expire_on_commit=False
                            )


async def get_db():
    """
    Асинхронный контекст менеджера для работы с базой данных.
    """
    async with SessionLocal() as db:
        yield db

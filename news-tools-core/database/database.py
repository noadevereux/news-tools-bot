from datetime import datetime, timedelta

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from config import MYSQL_USER, MYSQL_PASSWORD, MYSQL_DATABASE, MYSQL_HOST, MYSQL_PORT

SQLALCHEMY_DATABASE_URL = f"mysql+aiomysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}"
engine = create_async_engine(SQLALCHEMY_DATABASE_URL, pool_recycle=21_600)
SessionLocal = async_sessionmaker(
    autocommit=False, autoflush=False, bind=engine, expire_on_commit=False
)


class SessionManager:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, "session"):
            self.session = None
            self.last_session_refresh = datetime.now()

    async def __aenter__(self) -> AsyncSession:
        if self.session is None or (datetime.now() - self.last_session_refresh) > timedelta(hours=1):
            if self.session is not None:
                await self.session.close()
            self.session = SessionLocal()
            self.last_session_refresh = datetime.now()
        return self.session

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass

    async def startup(self):
        self.session = SessionLocal()

    async def shutdown(self):
        if self.session is not None:
            await self.session.close()

import sqlite3
from typing import AsyncGenerator
from os import path, makedirs

from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import sessionmaker, Session
from contextlib import asynccontextmanager
from app.models import Base
from app.core.settings import settings

DATABASE_URL = settings.DATABASE_URL

class Database:
    def __init__(self):
        self.create_db_if_necessary()

        # Sync engine
        self.engine = create_engine(
            f"sqlite+pysqlite:///{settings.DATABASE_URL}", echo=True, future=True
        )
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)

        # Async engine
        self.async_engine = create_async_engine(
            f"sqlite+aiosqlite:///{settings.DATABASE_URL}", echo=True
        )
        self.AsyncSessionLocal = async_sessionmaker(
            self.async_engine,
            expire_on_commit=False
        )

    def init_db(self):
        Base.metadata.create_all(bind=self.engine)

    def fetch_session(self):
        session = self.SessionLocal()
        try:
            yield session
        finally:
            session.close()

    @asynccontextmanager
    async def get_async_session(self) -> AsyncSession:
        async with self.AsyncSessionLocal() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise

    def create_db_if_necessary(self):
        db_dir = path.dirname(settings.DATABASE_URL)
        if not path.exists(settings.DATABASE_URL):
            if not path.exists(db_dir):
                makedirs(db_dir, exist_ok=True)
            open(settings.DATABASE_URL, "a").close()


db = Database()

async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with db.get_async_session() as session:
        yield session

import contextlib
from typing import AsyncGenerator, AsyncIterator, Annotated
from os import path, makedirs

from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncSession,
    async_sessionmaker,
    async_scoped_session,
    AsyncConnection,
)
from sqlalchemy.sql import text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import NullPool
from contextlib import asynccontextmanager
from asyncio import current_task
from fastapi import Depends
from app.models import Base
from app.core.settings import settings

DATABASE_URL = settings.DATABASE_URL


class SqliteDatabase:
    def __init__(self):
        self.create_db_if_necessary()
        self._sync_engine = create_engine(
            f"sqlite:///{DATABASE_URL}",
            echo=True,
        )
        self.engine = create_async_engine(
            f"sqlite+aiosqlite:///{DATABASE_URL}",
            echo=True,
            connect_args={"check_same_thread": False},
            poolclass=NullPool,
        )
        self.session_maker = async_sessionmaker(
            autocommit=False, autoflush=False, bind=self.engine, expire_on_commit=False
        )
        self.session = async_scoped_session(self.session_maker, scopefunc=current_task)

    def init_db(self):
        Base.metadata.create_all(bind=self._sync_engine)

    async def close_db(self):
        if self.engine is None:
            raise Exception("DatabaseSessionManager is not initialized")
        await self.engine.dispose()

    @staticmethod
    def create_db_if_necessary():
        db_dir = path.dirname(settings.DATABASE_URL)
        if not path.exists(settings.DATABASE_URL):
            if not path.exists(db_dir):
                makedirs(db_dir, exist_ok=True)
            open(settings.DATABASE_URL, "a").close()


db = SqliteDatabase()


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with db.session() as session:
        try:
            yield session
        finally:
            await session.close()


DatabaseSessionDependency = Annotated[AsyncSession, Depends(get_session)]

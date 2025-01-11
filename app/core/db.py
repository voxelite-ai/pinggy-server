import sqlite3

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import Base
from app.core.settings import settings

DATABASE_URL = settings.DATABASE_URL

def health() -> bool:
    try:
        conn = create_connection()
        conn.execute("SELECT 1")
        conn.close()
        return True
    except sqlite3.Error:
        return False

def create_connection() -> sqlite3.Connection:
    connection = sqlite3.connect(settings.DATABASE_URL)
    return connection

class Database:
    def __init__(self):
        self.engine = create_engine(f"sqlite:///{settings.DATABASE_URL}")
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)

    def init_db(self):
        Base.metadata.create_all(bind=self.engine)

    def fetch_session(self):
        session = self.SessionLocal()
        try:
            yield session
        finally:
            session.close()

db = Database()
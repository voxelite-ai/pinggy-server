from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()


class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///pinggy.db"
    PINGGY_TOKEN: str | None = None


settings = Settings()

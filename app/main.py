from contextlib import asynccontextmanager
from fastapi import FastAPI

from app.api.v1 import router as api_router
from app.core.db import health as db_health, db
from app.api.health import router as health_router


@asynccontextmanager
async def lifespan(_: FastAPI):
    if not db_health():
        raise Exception("Database is not healthy")
    db.init_db()
    yield

app = FastAPI(name="pinggy-server", lifespan=lifespan, redoc_url=None)

app.include_router(api_router, prefix="/api")
app.include_router(health_router)
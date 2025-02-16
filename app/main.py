from contextlib import asynccontextmanager
from app.core.log import logger

from uvicorn import Config
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from fastapi import FastAPI, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1 import router as api_router, fetch_all
from app.core.db import db, get_session, DatabaseSessionDependency
from app.api.health import router as health_router
from app import crud


@asynccontextmanager
async def lifespan(app: FastAPI):
    db.init_db()
    scheduler.start()
    scheduler.add_job(prune_tunnels_job, IntervalTrigger(minutes=10))
    await prune_tunnels_job()
    yield
    scheduler.shutdown()

app = FastAPI(name="pinggy-server", lifespan=lifespan)
scheduler = AsyncIOScheduler()

logger.info("App is starting up")

app.include_router(api_router, prefix="/api")
app.include_router(health_router)

async def prune_tunnels_job():
    async for session in get_session():
        await prune_tunnels(session)

async def prune_tunnels(session: DatabaseSessionDependency) -> None:
    active_tunnels = await crud.find_active_tunnels(session)
    for tunnel in active_tunnels:
        await crud.delete_tunnel(session, tunnel.id)

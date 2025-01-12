from contextlib import asynccontextmanager
from fastapi import FastAPI
from psutil import pid_exists

from app.api.v1 import router as api_router
from app.core.db import health as db_health, db
from app.api.health import router as health_router
from app import crud
from fastapi_utilities import repeat_every


@asynccontextmanager
async def lifespan(app: FastAPI):
    if not db_health():
        raise Exception("Database is not healthy")
    db.init_db()

    @repeat_every(seconds=600)
    def prune_tunnels() -> None:
        for tunnel in crud.find_active_tunnels(db):
            if not pid_exists(tunnel.pid):
                crud.delete_tunnel(db, tunnel.id)

    app.add_event_handler("startup", prune_tunnels)

    yield


app = FastAPI(name="pinggy-server", lifespan=lifespan, redoc_url=None)

app.include_router(api_router, prefix="/api")
app.include_router(health_router)

from builtins import list

from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel
import re

from app.crud import (
    delete_tunnel,
    get_tunnel,
    get_tunnels,
)
from app.core.db import DatabaseSessionDependency
from app.core.log import logger
from app.models import Tunnel, TunnelStatus
from app.pinggy import create_tunnel as create_pinggy_tunnel, terminate_tunnel

router = APIRouter(tags=["v1"])

class TunnelCreateRequest(BaseModel):
    hostname: str
    port: int

class TunnelResponse(BaseModel):
    id: int
    status: TunnelStatus
    hostname: str
    port: int
    http_url: str
    https_url: str

class TunnelsResponse(BaseModel):
    tunnels: list[TunnelResponse]


@router.get("/tunnels", response_model=TunnelsResponse)
async def fetch_all(session: DatabaseSessionDependency):
    tunnels = await get_tunnels(session)
    return TunnelsResponse(tunnels=[TunnelResponse(id=tunnel.id, status=tunnel.status, hostname=tunnel.hostname, port=tunnel.port, http_url=tunnel.http_url, https_url=tunnel.https_url) for tunnel in tunnels])


@router.post("/tunnels", response_model=TunnelResponse, status_code=status.HTTP_201_CREATED)
async def create(request: TunnelCreateRequest, session: DatabaseSessionDependency):
    logger.debug(f"Received request to create tunnel: {request}")

    async with session.begin():
        if not request.hostname or not re.match(
            r"^[a-zA-Z0-9.]{1,30}$", request.hostname
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid hostname"
            )
        if not (1 <= request.port <= 65535):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid port"
            )

        tunnel = Tunnel(
            status=TunnelStatus.CREATED, hostname=request.hostname, port=request.port
        )
        logger.debug(f"Tunnel created: {tunnel}")

        try:
            pid, http_url, https_url = create_pinggy_tunnel(
                f"{request.hostname}:{request.port}"
            )
            tunnel.status = TunnelStatus.RUNNING
            tunnel.http_url = http_url
            tunnel.https_url = https_url
            tunnel.pid = pid
        except RuntimeError as e:
            tunnel.status = TunnelStatus.FAILED
            tunnel.status_detail = str(e)

        session.add(tunnel)
        await session.flush()

        logger.debug(f"Tunnel updated: {tunnel}")

        return TunnelResponse(
            id=tunnel.id,
            status=tunnel.status,
            hostname=tunnel.hostname,
            port=tunnel.port,
            http_url=tunnel.http_url,
            https_url=tunnel.https_url,
        )


@router.get("/tunnels/{tunnel_id}", response_model=TunnelResponse)
async def fetch(tunnel_id: int, session: DatabaseSessionDependency):
    tunnel = await get_tunnel(session, tunnel_id)
    if not tunnel:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tunnel not found")
    return TunnelResponse(id=tunnel.id, status=tunnel.status, hostname=tunnel.hostname, port=tunnel.port, http_url=tunnel.http_url, https_url=tunnel.https_url)


@router.delete("/tunnels/{tunnel_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete(tunnel_id: int, session: DatabaseSessionDependency):
    tunnel = await get_tunnel(session, tunnel_id)
    if not tunnel:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tunnel not found")

    try:
        terminate_tunnel(tunnel.pid)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

    await delete_tunnel(session, tunnel_id)
    return

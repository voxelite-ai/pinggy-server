from builtins import list
from typing import Type

from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel
import re

from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import delete_tunnel, get_tunnel, create_tunnel, get_tunnels
from app.core.db import db, get_session
from app.models import Tunnel, TunnelStatus
from app.pinggy import create_tunnel as create_pinggy_tunnel, terminate_tunnel

router = APIRouter(prefix="/v1", tags=["v1"])

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
async def fetch_all(db: AsyncSession = Depends(get_session)):
    tunnels = await get_tunnels(db)
    return TunnelsResponse(tunnels=[TunnelResponse(id=tunnel.id, status=tunnel.status, hostname=tunnel.hostname, port=tunnel.port, http_url=tunnel.http_url, https_url=tunnel.https_url) for tunnel in tunnels])

@router.post("/tunnels", response_model=TunnelResponse, status_code=status.HTTP_201_CREATED)
async def create(request: TunnelCreateRequest, db: AsyncSession = Depends(get_session)):
    if not request.hostname or not re.match(r'^[a-zA-Z0-9.]{1,30}$', request.hostname):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid hostname")
    if not (1 <= request.port <= 65535):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid port")

    try:
        pid, http_url, https_url = create_pinggy_tunnel(f"{request.hostname}:{request.port}")
    except RuntimeError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

    tunnel = Tunnel(pid=pid, status=TunnelStatus.RUNNING, hostname=request.hostname, port=request.port, http_url=http_url, https_url=https_url)
    tunnel = await create_tunnel(db, tunnel)

    return TunnelResponse(id=tunnel.id, status=tunnel.status, hostname=tunnel.hostname, port=tunnel.port, http_url=tunnel.http_url, https_url=tunnel.https_url)

@router.get("/tunnels/{tunnel_id}", response_model=TunnelResponse)
async def fetch(tunnel_id: int, db: AsyncSession = Depends(get_session)):
    tunnel = await get_tunnel(db, tunnel_id)
    if not tunnel:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tunnel not found")
    return TunnelResponse(id=tunnel.id, status=tunnel.status, hostname=tunnel.hostname, port=tunnel.port, http_url=tunnel.http_url, https_url=tunnel.https_url)

@router.delete("/tunnels/{tunnel_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete(tunnel_id: int, db: AsyncSession = Depends(get_session)):
    tunnel = await get_tunnel(db, tunnel_id)
    if not tunnel:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tunnel not found")

    try:
        terminate_tunnel(tunnel.pid)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

    await delete_tunnel(db, tunnel_id)
    return
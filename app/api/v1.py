from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel
import re

from sqlalchemy.orm import Session

from app.crud import delete_tunnel, get_tunnel, create_tunnel
from app.core.db import db
from app.models import Tunnel, TunnelStatus
from app.pinggy import create_tunnel as create_pinggy_tunnel, terminate_tunnel

router = APIRouter(prefix="/v1", tags=["v1"])

class TunnelCreateRequest(BaseModel):
    hostname: str
    port: int

class TunnelResponse(BaseModel):
    id: int
    public_url: str

def get_db():
    yield from db.fetch_session()

@router.get("/tunnels/{tunnel_id}", response_model=TunnelResponse)
async def fetch(tunnel_id: int, db: Session = Depends(get_db)):
    tunnel = get_tunnel(db, tunnel_id)
    if not tunnel:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tunnel not found")
    return TunnelResponse(id=tunnel.id, public_url=tunnel.public_url)

@router.post("/tunnels", response_model=TunnelResponse, status_code=status.HTTP_201_CREATED)
async def create(request: TunnelCreateRequest, db: Session = Depends(get_db)):
    if not request.hostname or not re.match(r'^[a-zA-Z.]{1,30}$', request.hostname):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid hostname")
    if not (1 <= request.port <= 65535):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid port")

    try:
        pid, public_url = create_pinggy_tunnel(f"http://{request.hostname}:{request.port}")
    except RuntimeError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

    tunnel = Tunnel(pid=pid, status=TunnelStatus.RUNNING, hostname=request.hostname, port=request.port, public_url=public_url)
    tunnel = create_tunnel(db, tunnel)

    return TunnelResponse(id=tunnel.id, public_url=public_url)

@router.delete("/tunnels/{tunnel_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete(tunnel_id: int, db: Session = Depends(get_db)):
    tunnel = get_tunnel(db, tunnel_id)
    if not tunnel:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tunnel not found")

    try:
        terminate_tunnel(tunnel.pid)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

    delete_tunnel(db, tunnel_id)
    return
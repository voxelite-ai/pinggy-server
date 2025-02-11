from typing import Optional, List, Type, Any, Coroutine, Sequence
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Tunnel, TunnelStatus

async def get_tunnel(db: AsyncSession, tunnel_id: int) -> Optional[Tunnel]:
    stmt = select(Tunnel).filter(Tunnel.id == tunnel_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()

async def get_tunnels(db: AsyncSession) -> Sequence[Tunnel]:
    stmt = select(Tunnel)
    result = await db.execute(stmt)
    return result.scalars().all()

async def create_tunnel(db: AsyncSession, tunnel: Tunnel) -> Tunnel:
    db.add(tunnel)
    await db.commit()
    await db.refresh(tunnel)
    return tunnel

async def delete_tunnel(db: AsyncSession, tunnel_id: int) -> bool:
    stmt = select(Tunnel).filter(Tunnel.id == tunnel_id)
    result = await db.execute(stmt)
    tunnel = result.scalar_one_or_none()
    if tunnel:
        tunnel.pid = None
        tunnel.status = TunnelStatus.EXITED
        await db.commit()
        return True
    return False

async def find_active_tunnels(db: AsyncSession) -> Sequence[Tunnel]:
    stmt = select(Tunnel).filter(Tunnel.status == TunnelStatus.RUNNING)
    result = await db.execute(stmt)
    return result.scalars().all()
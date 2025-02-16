from typing import Optional, List, Type, Any, Coroutine, Sequence
from fastapi import Depends
from sqlalchemy.orm import Session
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import TimeoutError
from contextlib import asynccontextmanager
from app.models import Tunnel, TunnelStatus
from app.core.log import logger
from app.core.db import get_session, DatabaseSessionDependency


async def get_tunnel(
        session: DatabaseSessionDependency, tunnel_id: int
) -> Optional[Tunnel]:
    if tunnel_id is None:
        return None
    logger.debug(f"Fetching tunnel with id {tunnel_id}")
    stmt = select(Tunnel).filter(Tunnel.id == tunnel_id)
    result = await session.execute(stmt)
    return result.scalar_one_or_none()

async def get_tunnels(session: DatabaseSessionDependency) -> Sequence[Tunnel]:
    logger.debug("Fetching all tunnels")
    stmt = select(Tunnel)
    result = await session.execute(stmt)
    return result.scalars().all()


async def create_tunnel(session: DatabaseSessionDependency, tunnel: Tunnel) -> Tunnel:
    logger.debug("Creating tunnel...")
    session.add(tunnel)
    await session.commit()
    await session.refresh(tunnel)
    return tunnel


async def delete_tunnel(db: AsyncSession, tunnel_id: int) -> bool:
    logger.debug(f"Deleting tunnel with id {tunnel_id}")
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
    logger.debug("Finding active tunnels")
    stmt = select(Tunnel).filter(Tunnel.status == TunnelStatus.RUNNING)
    result = await db.execute(stmt)
    return result.scalars().all()

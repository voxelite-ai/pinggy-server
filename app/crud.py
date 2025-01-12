from typing import Optional
from sqlalchemy.orm import Session
from app.models import Tunnel, TunnelStatus

def get_tunnel(db: Session, tunnel_id: int) -> Optional[Tunnel]:
    return db.query(Tunnel).filter(Tunnel.id == tunnel_id).first()

def create_tunnel(db: Session, tunnel: Tunnel) -> Tunnel:
    db.add(tunnel)
    db.commit()
    db.refresh(tunnel)
    return tunnel

def delete_tunnel(db: Session, tunnel_id: int) -> bool:
    tunnel = db.query(Tunnel).filter(Tunnel.id == tunnel_id).first()
    if tunnel:
        tunnel.pid = None
        tunnel.status = TunnelStatus.EXITED
        db.commit()
        return True
    return False


def find_active_tunnels(db: Session) -> list[Tunnel]:
    return db.query(Tunnel).filter(Tunnel.status == TunnelStatus.RUNNING).all()

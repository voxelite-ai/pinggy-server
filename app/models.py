import uuid
from typing import Optional

from pydantic import BaseModel

from enum import Enum

class TunnelStatus(Enum):
    RUNNING = "RUNNING"
    EXITED = "EXITED"

class Tunnel(BaseModel):
    id: Optional[int] = None
    pid: Optional[int] = None
    status: TunnelStatus
    hostname: str
    port: int
    public_url: str
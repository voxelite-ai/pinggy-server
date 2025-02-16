from sqlalchemy import Column, Integer, String, Enum
from sqlalchemy.orm import declarative_base
from enum import Enum as PyEnum

Base = declarative_base()

class TunnelStatus(PyEnum):
    CREATED = "CREATED"
    RUNNING = "RUNNING"
    EXITED = "EXITED"
    FAILED = "FAILED"

class Tunnel(Base):
    __tablename__ = 'tunnels'

    id = Column(Integer, primary_key=True, autoincrement=True)
    pid = Column(Integer)
    status = Column(Enum(TunnelStatus), nullable=False)
    status_details = Column(String)
    hostname = Column(String, nullable=False)
    port = Column(Integer, nullable=False)
    http_url = Column(String)
    https_url = Column(String)

    def __repr__(self):
        return (
            f"Tunnel(id={self.id}, pid={self.pid}, status={self.status}, "
            f"status_details={self.status_details}, hostname={self.hostname}, "
            f"port={self.port}, http_url={self.http_url}, https_url={self.https_url})"
        )


from sqlalchemy import Column, Integer, String, Enum
from sqlalchemy.ext.declarative import declarative_base
from enum import Enum as PyEnum

Base = declarative_base()

class TunnelStatus(PyEnum):
    RUNNING = "RUNNING"
    EXITED = "EXITED"

class Tunnel(Base):
    __tablename__ = 'tunnels'

    id = Column(Integer, primary_key=True, autoincrement=True)
    pid = Column(Integer)
    status = Column(Enum(TunnelStatus), nullable=False)
    hostname = Column(String, nullable=False)
    port = Column(Integer, nullable=False)
    public_url = Column(String, nullable=False)
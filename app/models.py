from sqlalchemy import Column, Integer, String, Enum
from sqlalchemy.orm import declarative_base
from enum import Enum as PyEnum

Base = declarative_base()

class TunnelStatus(PyEnum):
    CREATED = "CREATED"
    RUNNING = "RUNNING"
    EXITED = "EXITED"
    FAILURE = "FAILURE"

class Tunnel(Base):
    __tablename__ = 'tunnels'

    id = Column(Integer, primary_key=True, autoincrement=True)
    pid = Column(Integer)
    status = Column(Enum(TunnelStatus), nullable=False)
    status_details = Column(String)
    hostname = Column(String, nullable=False)
    port = Column(Integer, nullable=False)
    http_url = Column(String, nullable=False)
    https_url = Column(String, nullable=False)

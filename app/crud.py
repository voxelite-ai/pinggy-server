import sqlite3
from typing import Optional, Dict

from app.models import Tunnel, TunnelStatus
from app.settings import settings

def health() -> bool:
    try:
        conn = create_connection()
        conn.execute("SELECT 1")
        conn.close()
        return True
    except sqlite3.Error:
        return False

def create_connection() -> sqlite3.Connection:
    connection = sqlite3.connect(settings.DATABASE_URL)
    return connection

def init_db(conn: sqlite3.Connection):
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS tunnels (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pid INTEGER,
            status TEXT NOT NULL,
            hostname TEXT NOT NULL,
            port INTEGER NOT NULL,
            public_url TEXT NOT NULL
        )
        """
    )
    conn.commit()
    conn.close()

def select_tunnel(conn: sqlite3.Connection, tunnel_id: int) -> Optional[Tunnel]:
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT id, pid, status, hostname, port, public_url
        FROM tunnels
        WHERE id = ?
        """,
        (tunnel_id,)
    )
    row = cursor.fetchone()
    if row:
        return Tunnel(id=row[0], pid=row[1], status=row[2], hostname=row[3], port=row[4], public_url=row[5])
    return None

def insert_tunnel(conn: sqlite3.Connection, tunnel: Tunnel) -> int:
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO tunnels (pid, status, hostname, port, public_url)
        VALUES (?, ?, ?, ?, ?)
        """,
        (tunnel.pid, TunnelStatus.RUNNING.name, tunnel.hostname, tunnel.port, tunnel.public_url)
    )
    conn.commit()
    return cursor.lastrowid

def delete_tunnel(conn: sqlite3.Connection, tunnel_id: int) -> bool:
    cursor = conn.cursor()
    cursor.execute(
        """
        UPDATE tunnels
        SET pid = ?, status = ?
        WHERE id = ?
        """,
        (None, TunnelStatus.EXITED.name, tunnel_id)
    )
    conn.commit()
    return cursor.rowcount > 0
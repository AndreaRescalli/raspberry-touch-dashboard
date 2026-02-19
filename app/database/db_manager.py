import sqlite3
from pathlib import Path
from datetime import datetime

DB_PATH = Path.home() / "touchui" / "metrics.db"

class DBManager:
    def __init__(self):
        self.conn = sqlite3.connect(DB_PATH)
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS metrics(
              ts TEXT PRIMARY KEY,
              cpu REAL,
              ram REAL,
              temp REAL,
              up_kb REAL,
              down_kb REAL
            )
        """)
        self.conn.commit()

    def insert(self, cpu, ram, temp, up_kb, down_kb):
        ts = datetime.now().isoformat(timespec="seconds")
        self.conn.execute(
            "INSERT OR REPLACE INTO metrics(ts,cpu,ram,temp,up_kb,down_kb) VALUES (?,?,?,?,?,?)",
            (ts, cpu, ram, temp, up_kb, down_kb),
        )
        self.conn.commit()

    def last_n(self, n=600):
        cur = self.conn.cursor()
        cur.execute("SELECT ts,cpu,ram,temp,up_kb,down_kb FROM metrics ORDER BY ts DESC LIMIT ?", (n,))
        rows = cur.fetchall()
        rows.reverse()
        return rows
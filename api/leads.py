"""
Lead storage — SQLite.
"""
import sqlite3
import json
from pathlib import Path
from datetime import datetime

DB_PATH = Path(__file__).parent.parent / "leads.db"


def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS leads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            email TEXT,
            phone TEXT,
            brief TEXT,
            source TEXT DEFAULT 'whatsapp',
            created_at TEXT
        )
    """)
    conn.commit()
    conn.close()


def save_lead(data: dict):
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "INSERT INTO leads (name, email, phone, brief, source, created_at) VALUES (?, ?, ?, ?, ?, ?)",
        (
            data.get("name", ""),
            data.get("email", ""),
            data.get("phone", ""),
            data.get("brief", ""),
            data.get("source", "whatsapp"),
            datetime.now().isoformat(),
        ),
    )
    conn.commit()
    conn.close()


def get_all_leads() -> list[dict]:
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute("SELECT * FROM leads ORDER BY created_at DESC").fetchall()
    conn.close()
    return [
        {"id": r[0], "name": r[1], "email": r[2], "phone": r[3],
         "brief": r[4], "source": r[5], "created_at": r[6]}
        for r in rows
    ]

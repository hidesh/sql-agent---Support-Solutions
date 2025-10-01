import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "example.db"


def get_connection():
    """Åbn en forbindelse til SQLite databasen."""
    return sqlite3.connect(DB_PATH)


def run_query(query: str, params: tuple = ()):
    """Kør en SELECT query og returner resultater som liste af dicts."""
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute(query, params)
    rows = cur.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def run_action(query: str, params: tuple = ()):
    """Kør en INSERT/UPDATE/DELETE query."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(query, params)
    conn.commit()
    conn.close()

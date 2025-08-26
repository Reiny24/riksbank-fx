import sqlite3
from typing import List, Optional, Dict

# Consts
DB_NAME = "series.db"
HISTORY_LIMIT = 3  # number of historical records to keep


def init_db() -> None:
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Main series table
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS series (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            seriesId TEXT NOT NULL UNIQUE,
            date TEXT,
            latest_value FLOAT
        )
    """
    )

    # History table
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS series_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            seriesId TEXT NOT NULL,
            date TEXT,
            value FLOAT,
            recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """
    )

    conn.commit()
    conn.close()


def insert_series(series_ids: List[str]) -> None:
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    for sid in series_ids:
        try:
            cursor.execute("INSERT OR IGNORE INTO series (seriesId) VALUES (?)", (sid,))
        except Exception as e:
            print(f"Skipping {sid}, error: {e}")
    conn.commit()
    conn.close()


def get_all_series() -> List[Dict]:
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM series")
    rows = cursor.fetchall()
    conn.close()
    return [
        {"id": r[0], "seriesId": r[1], "date": r[2], "latest_value": r[3]} for r in rows
    ]


def get_series_history(seriesId: Optional[str] = None) -> List[Dict]:
    """
    Fetch historical records from series_history table.
    If seriesId is provided, fetch only for that series; otherwise fetch all history.
    Returns a list of dicts.
    """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    if seriesId:
        cursor.execute(
            "SELECT * FROM series_history WHERE seriesId = ? ORDER BY recorded_at DESC",
            (seriesId,),
        )
    else:
        cursor.execute(
            "SELECT * FROM series_history ORDER BY seriesId, recorded_at DESC"
        )

    rows = cursor.fetchall()
    conn.close()

    return [
        {"id": r[0], "seriesId": r[1], "date": r[2], "value": r[3], "recorded_at": r[4]}
        for r in rows
    ]


def update_series_latest(seriesId: str, date: str, value: float) -> None:
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Insert the new value into history
    cursor.execute(
        "INSERT INTO series_history (seriesId, date, value) VALUES (?, ?, ?)",
        (seriesId, date, value),
    )

    # Keep only the latest HISTORY_LIMIT records per series
    cursor.execute(
        f"""
        DELETE FROM series_history
        WHERE id NOT IN (
            SELECT id FROM series_history
            WHERE seriesId = ?
            ORDER BY recorded_at DESC
            LIMIT ?
        ) AND seriesId = ?
    """,
        (seriesId, HISTORY_LIMIT, seriesId),
    )

    # Update the main table
    cursor.execute(
        "UPDATE series SET date = ?, latest_value = ? WHERE seriesId = ?",
        (date, value, seriesId),
    )
    conn.commit()
    conn.close()

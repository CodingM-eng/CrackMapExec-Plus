"""History Engine: Local execution metadata store without secret persistence."""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from cmeplus.config.loader import ConfigLoader
from cmeplus.core.results import ResultSet


@dataclass
class HistoryEntry:
    """Represents historical execution metadata."""
    id: int
    job_id: str
    timestamp: str
    protocol: str
    targets_count: int
    success_count: int
    failed_count: int
    duration: float
    status: str


class HistoryManager:
    """Manages SQLite-backed local execution metadata history."""

    def __init__(self, db_path: Path | None = None) -> None:
        if db_path is None:
            config_dir = ConfigLoader.ensure_config_dir()
            self.db_path = config_dir / "history.db"
        else:
            self.db_path = db_path
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        return sqlite3.connect(str(self.db_path))

    def _init_db(self) -> None:
        with self._get_connection() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS job_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    job_id TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    protocol TEXT NOT NULL,
                    targets_count INTEGER NOT NULL,
                    success_count INTEGER NOT NULL,
                    failed_count INTEGER NOT NULL,
                    duration REAL NOT NULL,
                    status TEXT NOT NULL
                )
                """
            )
            conn.commit()

    def record_job(self, result_set: ResultSet) -> None:
        """Persist execution metadata. Explicitly contains NO credentials or secrets."""
        now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        with self._get_connection() as conn:
            conn.execute(
                """
                INSERT INTO job_history (
                    job_id, timestamp, protocol, targets_count,
                    success_count, failed_count, duration, status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    result_set.job_id or "job",
                    now_iso,
                    result_set.protocol.upper(),
                    result_set.total,
                    result_set.success_count,
                    result_set.failed_count + result_set.unavailable_count,
                    round(result_set.total_duration, 2),
                    result_set.summary_status.value.upper(),
                ),
            )
            conn.commit()

    def get_recent(self, limit: int = 15) -> list[HistoryEntry]:
        """Fetch the most recent execution history entries."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT id, job_id, timestamp, protocol, targets_count,
                       success_count, failed_count, duration, status
                FROM job_history
                ORDER BY id DESC
                LIMIT ?
                """,
                (limit,),
            )
            rows = cursor.fetchall()
            return [
                HistoryEntry(
                    id=row[0],
                    job_id=row[1],
                    timestamp=row[2],
                    protocol=row[3],
                    targets_count=row[4],
                    success_count=row[5],
                    failed_count=row[6],
                    duration=row[7],
                    status=row[8],
                )
                for row in rows
            ]

    def clear(self) -> None:
        """Clear all history entries."""
        with self._get_connection() as conn:
            conn.execute("DELETE FROM job_history")
            conn.commit()

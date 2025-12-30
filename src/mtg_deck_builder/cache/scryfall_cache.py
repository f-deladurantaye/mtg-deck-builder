"""SQLite cache for Scryfall API responses.

Purpose: stability + offline builds
- Stores: query, page, response JSON, fetched_at
- Supports: read-through, offline mode
"""

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional


class ScryfallCache:
    """SQLite-based cache for Scryfall API responses."""

    def __init__(self, db_path: Path | str = "scryfall_cache.db"):
        """Initialize the cache database."""
        self.db_path = Path(db_path)
        self._init_db()

    def _init_db(self) -> None:
        """Create the cache table if it doesn't exist."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS cache (
                    query TEXT NOT NULL,
                    page INTEGER NOT NULL DEFAULT 1,
                    response_json TEXT NOT NULL,
                    fetched_at TIMESTAMP NOT NULL,
                    PRIMARY KEY (query, page)
                )
                """
            )
            conn.commit()

    def get(self, query: str, page: int = 1) -> Optional[dict[str, Any]]:
        """Retrieve a cached response."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                "SELECT response_json FROM cache WHERE query = ? AND page = ?",
                (query, page),
            )
            row = cursor.fetchone()
            if row:
                return json.loads(row["response_json"])
            return None

    def set(self, query: str, response: dict[str, Any], page: int = 1) -> None:
        """Store a response in the cache."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO cache (query, page, response_json, fetched_at)
                VALUES (?, ?, ?, ?)
                """,
                (
                    query,
                    page,
                    json.dumps(response),
                    datetime.now(timezone.utc).isoformat(),
                ),
            )
            conn.commit()

    def clear(self) -> None:
        """Clear all cached entries."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM cache")
            conn.commit()

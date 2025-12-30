"""DuckDB card index for fast deterministic filtering and evaluation."""

import duckdb
from pathlib import Path
from typing import Any


class CardIndex:
    """DuckDB-based card index for fast queries."""

    def __init__(self, db_path: Path | str = ":memory:"):
        """Initialize the DuckDB connection."""
        self.conn = duckdb.connect(str(db_path))
        self._init_tables()

    def _init_tables(self) -> None:
        """Create the cards and card_features tables."""
        # Cards table (normalised, engine-facing)
        self.conn.execute(
            """
            CREATE TABLE IF NOT EXISTS cards (
                scryfall_id VARCHAR PRIMARY KEY,
                name VARCHAR NOT NULL,
                mana_cost VARCHAR,
                cmc INTEGER NOT NULL,
                type_line VARCHAR NOT NULL,
                oracle_text TEXT,
                colors ARRAY<VARCHAR>,
                color_identity ARRAY<VARCHAR>,
                rarity VARCHAR,
                commander_legal BOOLEAN NOT NULL,
                power VARCHAR,
                toughness VARCHAR,
                keywords ARRAY<VARCHAR>,
                produced_mana ARRAY<VARCHAR>
            )
            """
        )

        # Card features table (derived features)
        self.conn.execute(
            """
            CREATE TABLE IF NOT EXISTS card_features (
                scryfall_id VARCHAR PRIMARY KEY,
                produces_mana BOOLEAN NOT NULL DEFAULT FALSE,
                draws_cards BOOLEAN NOT NULL DEFAULT FALSE,
                removes_creature BOOLEAN NOT NULL DEFAULT FALSE,
                removes_noncreature BOOLEAN NOT NULL DEFAULT FALSE,
                is_board_wipe BOOLEAN NOT NULL DEFAULT FALSE,
                is_tutor BOOLEAN NOT NULL DEFAULT FALSE,
                creates_tokens BOOLEAN NOT NULL DEFAULT FALSE,
                is_finisher BOOLEAN NOT NULL DEFAULT FALSE,
                protects_board BOOLEAN NOT NULL DEFAULT FALSE,
                recurs_from_graveyard BOOLEAN NOT NULL DEFAULT FALSE,
                is_land_only BOOLEAN NOT NULL DEFAULT FALSE,
                FOREIGN KEY (scryfall_id) REFERENCES cards(scryfall_id)
            )
            """
        )

        self.conn.commit()

    def insert_card(self, card: dict[str, Any]) -> None:
        """Insert a normalised card into the index."""
        # Delete existing card if present, then insert (simple upsert for v1)
        self.conn.execute(
            "DELETE FROM cards WHERE scryfall_id = ?",
            (card["scryfall_id"],),
        )
        self.conn.execute(
            """
            INSERT INTO cards (
                scryfall_id, name, mana_cost, cmc, type_line, oracle_text,
                colors, color_identity, rarity, commander_legal,
                power, toughness, keywords, produced_mana
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                card["scryfall_id"],
                card["name"],
                card["mana_cost"],
                card["cmc"],
                card["type_line"],
                card["oracle_text"],
                card["colors"],
                card["color_identity"],
                card["rarity"],
                card["commander_legal"],
                card["power"],
                card["toughness"],
                card["keywords"],
                card["produced_mana"],
            ),
        )

    def insert_features(self, scryfall_id: str, features: dict[str, bool]) -> None:
        """Insert card features into the index."""
        # Delete existing features if present, then insert (simple upsert for v1)
        self.conn.execute(
            "DELETE FROM card_features WHERE scryfall_id = ?",
            (scryfall_id,),
        )
        self.conn.execute(
            """
            INSERT INTO card_features (
                scryfall_id, produces_mana, draws_cards, removes_creature,
                removes_noncreature, is_board_wipe, is_tutor, creates_tokens,
                is_finisher, protects_board, recurs_from_graveyard, is_land_only
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                scryfall_id,
                features.get("produces_mana", False),
                features.get("draws_cards", False),
                features.get("removes_creature", False),
                features.get("removes_noncreature", False),
                features.get("is_board_wipe", False),
                features.get("is_tutor", False),
                features.get("creates_tokens", False),
                features.get("is_finisher", False),
                features.get("protects_board", False),
                features.get("recurs_from_graveyard", False),
                features.get("is_land_only", False),
            ),
        )

    def query_cards(
        self,
        color_identity: list[str] | None = None,
        commander_legal: bool = True,
        **kwargs: Any,
    ) -> list[dict[str, Any]]:
        """Query cards with filters."""
        query = "SELECT * FROM cards WHERE 1=1"
        params: list[Any] = []

        if commander_legal:
            query += " AND commander_legal = ?"
            params.append(True)

        if color_identity:
            # Filter by color identity (card's color_identity must be subset of provided)
            query += " AND array_length(color_identity) <= ?"
            params.append(len(color_identity))
            # This is a simplified check; full implementation would check subset

        result = self.conn.execute(query, params).fetchall()
        columns = [desc[0] for desc in self.conn.description]
        return [dict(zip(columns, row)) for row in result]

    def close(self) -> None:
        """Close the database connection."""
        self.conn.close()

"""Tests for card index."""

from mtg_deck_builder.data.card_index import CardIndex


class TestCardIndex:
    """Test DuckDB card index operations."""

    def test_init_creates_tables(self, temp_db_path):
        """Test that initialization creates the required tables."""
        index = CardIndex(temp_db_path)

        # Check tables exist
        result = index.conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in result.fetchall()]

        assert "cards" in tables
        assert "card_features" in tables

    def test_insert_and_query_card(self, temp_db_path):
        """Test inserting and querying a card."""
        index = CardIndex(temp_db_path)

        card = {
            "scryfall_id": "test-123",
            "name": "Test Card",
            "mana_cost": "{1}{W}",
            "cmc": 2,
            "type_line": "Creature — Human",
            "oracle_text": "First strike",
            "colors": ["W"],
            "color_identity": ["W"],
            "rarity": "common",
            "commander_legal": True,
            "power": "2",
            "toughness": "2",
            "keywords": ["First strike"],
            "produced_mana": [],
        }

        index.insert_card(card)

        # Query the card back
        result = index.conn.execute(
            "SELECT * FROM cards WHERE scryfall_id = ?", ("test-123",)
        )
        row = result.fetchone()

        assert row is not None
        columns = [col[0] for col in result.description]
        retrieved_card = dict(zip(columns, row))

        assert retrieved_card["name"] == "Test Card"
        assert retrieved_card["colors"] == ["W"]
        assert retrieved_card["commander_legal"] is True

    def test_insert_features(self, temp_db_path):
        """Test inserting card features."""
        index = CardIndex(temp_db_path)

        # First insert a card
        card = {
            "scryfall_id": "test-123",
            "name": "Test Card",
            "mana_cost": "{W}",
            "cmc": 1,
            "type_line": "Instant",
            "oracle_text": "Draw a card.",
            "colors": ["W"],
            "color_identity": ["W"],
            "rarity": "common",
            "commander_legal": True,
            "power": None,
            "toughness": None,
            "keywords": [],
            "produced_mana": [],
        }
        index.insert_card(card)

        features = {
            "produces_mana": True,
            "draws_cards": False,
            "removes_creature": True,
            "removes_noncreature": False,
            "is_board_wipe": False,
            "is_tutor": False,
            "creates_tokens": False,
            "is_finisher": False,
            "protects_board": False,
            "recurs_from_graveyard": False,
            "is_land_only": False,
        }

        index.insert_features("test-123", features)

        # Query features back
        result = index.conn.execute(
            "SELECT * FROM card_features WHERE scryfall_id = ?", ("test-123",)
        )
        row = result.fetchone()

        assert row is not None
        columns = [col[0] for col in result.description]
        retrieved_features = dict(zip(columns, row))

        assert retrieved_features["produces_mana"] is True
        assert retrieved_features["draws_cards"] is False
        assert retrieved_features["removes_creature"] is True

    def test_query_by_color_identity(self, temp_db_path):
        """Test querying cards by color identity."""
        index = CardIndex(temp_db_path)

        # Insert test cards
        cards = [
            {
                "scryfall_id": "white-1",
                "name": "White Card",
                "mana_cost": "{W}",
                "cmc": 1,
                "type_line": "Instant",
                "oracle_text": "Draw a card.",
                "colors": ["W"],
                "color_identity": ["W"],
                "rarity": "common",
                "commander_legal": True,
                "power": None,
                "toughness": None,
                "keywords": [],
                "produced_mana": [],
            },
            {
                "scryfall_id": "blue-1",
                "name": "Blue Card",
                "mana_cost": "{U}",
                "cmc": 1,
                "type_line": "Instant",
                "oracle_text": "Draw a card.",
                "colors": ["U"],
                "color_identity": ["U"],
                "rarity": "common",
                "commander_legal": True,
                "power": None,
                "toughness": None,
                "keywords": [],
                "produced_mana": [],
            },
            {
                "scryfall_id": "multicolor-1",
                "name": "Multicolor Card",
                "mana_cost": "{W}{U}",
                "cmc": 2,
                "type_line": "Instant",
                "oracle_text": "Draw a card.",
                "colors": ["W", "U"],
                "color_identity": ["W", "U"],
                "rarity": "common",
                "commander_legal": True,
                "power": None,
                "toughness": None,
                "keywords": [],
                "produced_mana": [],
            },
        ]

        for card in cards:
            index.insert_card(card)

        # Query cards that match mono-white color identity
        query = """
        SELECT * FROM cards
        WHERE commander_legal = true
        AND color_identity <@ ARRAY['W']
        """
        result = index.conn.execute(query)
        rows = result.fetchall()

        # Should return white-1 only (mono-white cards for mono-white deck)
        scryfall_ids = [row[0] for row in rows]  # scryfall_id is first column
        assert "white-1" in scryfall_ids
        assert "multicolor-1" not in scryfall_ids
        assert "blue-1" not in scryfall_ids

    def test_query_lands(self, temp_db_path):
        """Test querying land cards."""
        index = CardIndex(temp_db_path)

        # Insert a land and a non-land
        cards = [
            {
                "scryfall_id": "land-1",
                "name": "Test Land",
                "mana_cost": "",
                "cmc": 0,
                "type_line": "Land",
                "oracle_text": "{T}: Add {W}.",
                "colors": [],
                "color_identity": ["W"],
                "rarity": "common",
                "commander_legal": True,
                "power": None,
                "toughness": None,
                "keywords": [],
                "produced_mana": ["W"],
            },
            {
                "scryfall_id": "spell-1",
                "name": "Test Spell",
                "mana_cost": "{1}{W}",
                "cmc": 2,
                "type_line": "Instant",
                "oracle_text": "Draw a card.",
                "colors": ["W"],
                "color_identity": ["W"],
                "rarity": "common",
                "commander_legal": True,
                "power": None,
                "toughness": None,
                "keywords": [],
                "produced_mana": [],
            },
        ]

        for card in cards:
            index.insert_card(card)

        # Insert features
        from mtg_deck_builder.features.extract import extract_features

        for card in cards:
            features = extract_features(card)
            index.insert_features(str(card["scryfall_id"]), features)

        # Query lands
        query = """
        SELECT c.* FROM cards c
        JOIN card_features cf ON c.scryfall_id = cf.scryfall_id
        WHERE cf.is_land_only = true
        AND c.commander_legal = true
        """
        result = index.conn.execute(query)
        rows = result.fetchall()

        assert len(rows) == 1
        columns = [col[0] for col in result.description]
        land = dict(zip(columns, rows[0]))
        assert land["name"] == "Test Land"

    def test_upsert_behavior(self, temp_db_path):
        """Test that inserting the same card twice works (upsert)."""
        index = CardIndex(temp_db_path)

        card = {
            "scryfall_id": "upsert-test",
            "name": "Upsert Card",
            "mana_cost": "{W}",
            "cmc": 1,
            "type_line": "Instant",
            "oracle_text": "Draw a card.",
            "colors": ["W"],
            "color_identity": ["W"],
            "rarity": "common",
            "commander_legal": True,
            "power": None,
            "toughness": None,
            "keywords": [],
            "produced_mana": [],
        }

        # Insert twice
        index.insert_card(card)
        index.insert_card(card)

        # Should only have one record
        result = index.conn.execute(
            "SELECT COUNT(*) FROM cards WHERE scryfall_id = ?", ("upsert-test",)
        )
        row = result.fetchone()
        assert row is not None
        count = row[0]
        assert count == 1

    def test_features_upsert(self, temp_db_path):
        """Test that inserting features twice works."""
        index = CardIndex(temp_db_path)

        # First insert a card
        card = {
            "scryfall_id": "test-features",
            "name": "Test Features Card",
            "mana_cost": "{U}",
            "cmc": 1,
            "type_line": "Instant",
            "oracle_text": "Draw a card.",
            "colors": ["U"],
            "color_identity": ["U"],
            "rarity": "common",
            "commander_legal": True,
            "power": None,
            "toughness": None,
            "keywords": [],
            "produced_mana": [],
        }
        index.insert_card(card)

        features = {
            "produces_mana": True,
            "draws_cards": False,
            "removes_creature": False,
            "removes_noncreature": False,
            "is_board_wipe": False,
            "is_tutor": False,
            "creates_tokens": False,
            "is_finisher": False,
            "protects_board": False,
            "recurs_from_graveyard": False,
            "is_land_only": False,
        }

        # Insert twice
        index.insert_features("test-features", features)
        index.insert_features("test-features", features)

        # Should only have one record
        result = index.conn.execute(
            "SELECT COUNT(*) FROM card_features WHERE scryfall_id = ?",
            ("test-features",),
        )
        row = result.fetchone()
        assert row is not None
        count = row[0]
        assert count == 1

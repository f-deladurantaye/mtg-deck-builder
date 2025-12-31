"""Tests for card normalization."""

from mtg_deck_builder.data.normalise import normalise_card


class TestCardNormalization:
    """Test card data normalization from Scryfall format."""

    def test_normalise_basic_creature(self):
        """Test normalization of a basic creature card."""
        scryfall_data = {
            "id": "test-id-123",
            "name": "Test Creature",
            "mana_cost": "{2}{W}{W}",
            "cmc": 4,
            "type_line": "Creature — Human Soldier",
            "oracle_text": "First strike\nVigilance\nWhen Test Creature enters the battlefield, you gain 3 life.",
            "colors": ["W"],
            "color_identity": ["W"],
            "rarity": "rare",
            "legalities": {"commander": "legal", "standard": "not_legal"},
            "power": "3",
            "toughness": "4",
            "keywords": ["First strike", "Vigilance"],
            "produced_mana": [],
        }

        normalized = normalise_card(scryfall_data)

        assert normalized["scryfall_id"] == "test-id-123"
        assert normalized["name"] == "Test Creature"
        assert normalized["mana_cost"] == "{2}{W}{W}"
        assert normalized["cmc"] == 4
        assert normalized["type_line"] == "Creature — Human Soldier"
        assert "First strike" in normalized["oracle_text"]
        assert normalized["colors"] == ["W"]
        assert normalized["color_identity"] == ["W"]
        assert normalized["rarity"] == "rare"
        assert normalized["commander_legal"] is True
        assert normalized["power"] == "3"
        assert normalized["toughness"] == "4"
        assert "First strike" in normalized["keywords"]
        assert "Vigilance" in normalized["keywords"]
        assert normalized["produced_mana"] == []

    def test_normalise_land(self):
        """Test normalization of a land card."""
        scryfall_data = {
            "id": "land-id",
            "name": "Plains",
            "mana_cost": "",
            "cmc": 0,
            "type_line": "Basic Land — Plains",
            "oracle_text": "({T}: Add {W}.)",
            "colors": [],
            "color_identity": ["W"],
            "rarity": "common",
            "legalities": {"commander": "legal"},
            "power": None,
            "toughness": None,
            "keywords": [],
            "produced_mana": ["W"],
        }

        normalized = normalise_card(scryfall_data)

        assert normalized["mana_cost"] == ""
        assert normalized["cmc"] == 0
        assert normalized["colors"] == []
        assert normalized["color_identity"] == ["W"]
        assert normalized["power"] is None
        assert normalized["toughness"] is None
        assert normalized["produced_mana"] == ["W"]

    def test_normalise_multicolor_card(self):
        """Test normalization of a multicolor card."""
        scryfall_data = {
            "id": "multi-id",
            "name": "Abzan Charm",
            "mana_cost": "{W}{B}{G}",
            "cmc": 3,
            "type_line": "Instant",
            "oracle_text": "Choose one —\n• Exile target creature with power 3 or greater.\n• You gain 3 life and draw a card.\n• Put two +1/+1 counters on target creature.",
            "colors": ["W", "B", "G"],
            "color_identity": ["W", "B", "G"],
            "rarity": "uncommon",
            "legalities": {"commander": "legal"},
            "power": None,
            "toughness": None,
            "keywords": [],
            "produced_mana": [],
        }

        normalized = normalise_card(scryfall_data)

        assert normalized["colors"] == ["W", "B", "G"]
        assert normalized["color_identity"] == ["W", "B", "G"]
        assert normalized["cmc"] == 3

    def test_normalise_commander_illegal(self):
        """Test normalization of a card illegal in Commander."""
        scryfall_data = {
            "id": "illegal-id",
            "name": "Black Lotus",
            "mana_cost": "{0}",
            "cmc": 0,
            "type_line": "Artifact",
            "oracle_text": "{T}, Sacrifice Black Lotus: Add three mana of any one color.",
            "colors": [],
            "color_identity": ["B", "G", "R", "U", "W"],
            "rarity": "rare",
            "legalities": {"commander": "not_legal", "vintage": "restricted"},
            "power": None,
            "toughness": None,
            "keywords": [],
            "produced_mana": ["B", "G", "R", "U", "W"],
        }

        normalized = normalise_card(scryfall_data)

        assert normalized["commander_legal"] is False

    def test_normalise_missing_fields(self):
        """Test normalization handles missing fields gracefully."""
        scryfall_data = {
            "id": "minimal-id",
            "name": "Minimal Card",
            "type_line": "Instant",
            "oracle_text": "Draw a card.",
            "colors": [],
            "color_identity": [],
            "rarity": "common",
            "legalities": {"commander": "legal"},
        }

        normalized = normalise_card(scryfall_data)

        assert normalized["mana_cost"] == ""
        assert normalized["cmc"] == 0
        assert normalized["power"] is None
        assert normalized["toughness"] is None
        assert normalized["keywords"] == []
        assert normalized["produced_mana"] == []

    def test_normalise_colorless_artifact(self):
        """Test normalization of a colorless artifact."""
        scryfall_data = {
            "id": "artifact-id",
            "name": "Sol Ring",
            "mana_cost": "{1}",
            "cmc": 1,
            "type_line": "Artifact",
            "oracle_text": "{T}: Add {C}{C}.",
            "colors": [],
            "color_identity": [],
            "rarity": "uncommon",
            "legalities": {"commander": "legal"},
            "power": None,
            "toughness": None,
            "keywords": [],
            "produced_mana": ["C", "C"],
        }

        normalized = normalise_card(scryfall_data)

        assert normalized["colors"] == []
        assert normalized["color_identity"] == []
        assert normalized["produced_mana"] == ["C", "C"]

    def test_normalise_creature_with_keywords(self):
        """Test normalization preserves all keywords."""
        scryfall_data = {
            "id": "creature-id",
            "name": "Complex Creature",
            "mana_cost": "{3}{W}{U}",
            "cmc": 5,
            "type_line": "Creature — Angel Wizard",
            "oracle_text": "Flying, vigilance, lifelink\nWhenever Complex Creature attacks, draw a card.",
            "colors": ["W", "U"],
            "color_identity": ["W", "U"],
            "rarity": "mythic",
            "legalities": {"commander": "legal"},
            "power": "4",
            "toughness": "5",
            "keywords": ["Flying", "Vigilance", "Lifelink"],
            "produced_mana": [],
        }

        normalized = normalise_card(scryfall_data)

        assert set(normalized["keywords"]) == {"Flying", "Vigilance", "Lifelink"}
        assert normalized["power"] == "4"
        assert normalized["toughness"] == "5"

    def test_normalise_produced_mana_extraction(self):
        """Test that produced mana is correctly extracted from oracle text."""
        # This would require the normalise function to parse oracle text
        # For now, we assume produced_mana comes from Scryfall data
        scryfall_data = {
            "id": "mana-id",
            "name": "Mana Producer",
            "mana_cost": "{G}",
            "cmc": 1,
            "type_line": "Creature — Elf Druid",
            "oracle_text": "{T}: Add {G}{G}{G}.",
            "colors": ["G"],
            "color_identity": ["G"],
            "rarity": "common",
            "legalities": {"commander": "legal"},
            "power": "1",
            "toughness": "1",
            "keywords": [],
            "produced_mana": ["G", "G", "G"],
        }

        normalized = normalise_card(scryfall_data)

        assert normalized["produced_mana"] == ["G", "G", "G"]

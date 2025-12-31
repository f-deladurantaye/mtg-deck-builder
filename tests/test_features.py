"""Tests for feature extraction."""

from mtg_deck_builder.features.extract import extract_features


class TestFeatureExtraction:
    """Test feature extraction from card data."""

    def test_extract_features_basic_instant(self, sample_scryfall_card):
        """Test feature extraction for a basic instant."""
        features = extract_features(sample_scryfall_card)

        assert features["produces_mana"] is False
        assert features["draws_cards"] is False
        assert features["removes_creature"] is False
        assert features["removes_noncreature"] is False
        assert features["is_board_wipe"] is False
        assert features["is_tutor"] is False
        assert features["creates_tokens"] is False
        assert features["is_finisher"] is False
        assert features["protects_board"] is False
        assert features["recurs_from_graveyard"] is False
        assert features["is_land_only"] is False

    def test_extract_features_mana_producer(self):
        """Test feature extraction for a mana-producing card."""
        card = {
            "id": "test-id",
            "name": "Birds of Paradise",
            "mana_cost": "{G}",
            "cmc": 1,
            "type_line": "Creature — Bird",
            "oracle_text": "Flying\n{T}: Add one mana of any color.",
            "colors": ["G"],
            "color_identity": ["G"],
            "rarity": "rare",
            "legalities": {"commander": "legal"},
            "power": "0",
            "toughness": "1",
            "keywords": ["Flying"],
            "produced_mana": ["W", "U", "B", "R", "G"],
        }

        features = extract_features(card)
        assert features["produces_mana"] is True
        assert features["is_land_only"] is False

    def test_extract_features_card_draw(self):
        """Test feature extraction for card draw."""
        card = {
            "id": "test-id",
            "name": "Brainstorm",
            "mana_cost": "{U}",
            "cmc": 1,
            "type_line": "Instant",
            "oracle_text": "Draw three cards, then put two cards from your hand on top of your library in any order.",
            "colors": ["U"],
            "color_identity": ["U"],
            "rarity": "common",
            "legalities": {"commander": "legal"},
            "power": None,
            "toughness": None,
            "keywords": [],
            "produced_mana": [],
        }

        features = extract_features(card)
        assert features["draws_cards"] is True

    def test_extract_features_creature_removal(self):
        """Test feature extraction for creature removal."""
        card = {
            "id": "test-id",
            "name": "Doom Blade",
            "mana_cost": "{1}{B}",
            "cmc": 2,
            "type_line": "Instant",
            "oracle_text": "Destroy target creature.",
            "colors": ["B"],
            "color_identity": ["B"],
            "rarity": "common",
            "legalities": {"commander": "legal"},
            "power": None,
            "toughness": None,
            "keywords": [],
            "produced_mana": [],
        }

        features = extract_features(card)
        assert features["removes_creature"] is True

    def test_extract_features_board_wipe(self):
        """Test feature extraction for board wipe."""
        card = {
            "id": "test-id",
            "name": "Wrath of God",
            "mana_cost": "{2}{W}{W}",
            "cmc": 4,
            "type_line": "Sorcery",
            "oracle_text": "Destroy all creatures. They can't be regenerated.",
            "colors": ["W"],
            "color_identity": ["W"],
            "rarity": "rare",
            "legalities": {"commander": "legal"},
            "power": None,
            "toughness": None,
            "keywords": [],
            "produced_mana": [],
        }

        features = extract_features(card)
        assert features["is_board_wipe"] is True

    def test_extract_features_tutor(self):
        """Test feature extraction for tutor effects."""
        card = {
            "id": "test-id",
            "name": "Demonic Tutor",
            "mana_cost": "{1}{B}",
            "cmc": 2,
            "type_line": "Sorcery",
            "oracle_text": "Search your library for a card, put that card into your hand, then shuffle.",
            "colors": ["B"],
            "color_identity": ["B"],
            "rarity": "uncommon",
            "legalities": {"commander": "legal"},
            "power": None,
            "toughness": None,
            "keywords": [],
            "produced_mana": [],
        }

        features = extract_features(card)
        assert features["is_tutor"] is True

    def test_extract_features_token_creation(self):
        """Test feature extraction for token creation."""
        card = {
            "id": "test-id",
            "name": "Saproling Migration",
            "mana_cost": "{2}{G}",
            "cmc": 3,
            "type_line": "Sorcery",
            "oracle_text": "Create two 1/1 green Saproling creature tokens.",
            "colors": ["G"],
            "color_identity": ["G"],
            "rarity": "common",
            "legalities": {"commander": "legal"},
            "power": None,
            "toughness": None,
            "keywords": [],
            "produced_mana": [],
        }

        features = extract_features(card)
        assert features["creates_tokens"] is True

    def test_extract_features_finisher(self):
        """Test feature extraction for finisher cards."""
        card = {
            "id": "test-id",
            "name": "Emrakul, the Aeons Torn",
            "mana_cost": "{15}",
            "cmc": 15,
            "type_line": "Legendary Creature — Eldrazi",
            "oracle_text": "This spell costs {1} less to cast for each card type among cards in all graveyards.\nWhen you cast this spell, take an extra turn after this one.\nFlying, protection from colored spells, annihilator 6\nWhen Emrakul, the Aeons Torn is put into a graveyard from anywhere, its owner shuffles their graveyard into their library.",
            "colors": [],
            "color_identity": ["B", "G", "R", "U", "W"],
            "rarity": "mythic",
            "legalities": {"commander": "legal"},
            "power": "15",
            "toughness": "15",
            "keywords": ["Flying", "Protection", "Annihilator"],
            "produced_mana": [],
        }

        features = extract_features(card)
        assert features["is_finisher"] is True  # High power creature

    def test_extract_features_protection(self):
        """Test feature extraction for board protection."""
        card = {
            "id": "test-id",
            "name": "Teferi's Protection",
            "mana_cost": "{2}{W}{U}",
            "cmc": 4,
            "type_line": "Instant",
            "oracle_text": "Until your next turn, your life total can't change, and you gain protection from everything. All permanents you control phase out. (While they're phased out, they're treated as though they don't exist. They phase in before you untap during your untap step.)\nExile Teferi's Protection.",
            "colors": ["W", "U"],
            "color_identity": ["W", "U"],
            "rarity": "rare",
            "legalities": {"commander": "legal"},
            "power": None,
            "toughness": None,
            "keywords": ["Protection"],
            "produced_mana": [],
        }

        features = extract_features(card)
        assert features["protects_board"] is True

    def test_extract_features_recur(self):
        """Test feature extraction for graveyard recursion."""
        card = {
            "id": "test-id",
            "name": "Reanimate",
            "mana_cost": "{B}",
            "cmc": 1,
            "type_line": "Sorcery",
            "oracle_text": "Put target creature card from a graveyard onto the battlefield under your control. You lose life equal to its mana value.",
            "colors": ["B"],
            "color_identity": ["B"],
            "rarity": "rare",
            "legalities": {"commander": "legal"},
            "power": None,
            "toughness": None,
            "keywords": [],
            "produced_mana": [],
        }

        features = extract_features(card)
        assert features["recurs_from_graveyard"] is True

    def test_extract_features_land(self):
        """Test feature extraction for lands."""
        card = {
            "id": "test-id",
            "name": "Forest",
            "mana_cost": "",
            "cmc": 0,
            "type_line": "Basic Land — Forest",
            "oracle_text": "({T}: Add {G}.)",
            "colors": [],
            "color_identity": ["G"],
            "rarity": "common",
            "legalities": {"commander": "legal"},
            "power": None,
            "toughness": None,
            "keywords": [],
            "produced_mana": ["G"],
        }

        features = extract_features(card)
        assert features["is_land_only"] is True
        assert features["produces_mana"] is True

    def test_extract_features_all_features_present(self, sample_scryfall_card):
        """Test that all expected features are present."""
        features = extract_features(sample_scryfall_card)

        expected_features = [
            "produces_mana",
            "draws_cards",
            "removes_creature",
            "removes_noncreature",
            "is_board_wipe",
            "is_tutor",
            "creates_tokens",
            "is_finisher",
            "protects_board",
            "recurs_from_graveyard",
            "is_land_only",
        ]

        for feature in expected_features:
            assert feature in features
            assert isinstance(features[feature], bool)

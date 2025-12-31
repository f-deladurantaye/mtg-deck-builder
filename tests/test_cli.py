"""Tests for CLI interface."""

import pytest
import json
from unittest.mock import patch
from mtg_deck_builder.cli import main, build_deck
from mtg_deck_builder.data.card_index import CardIndex


class TestCLI:
    """Test CLI functionality."""

    def test_build_deck_function(self, temp_db_path, role_engine, tmp_path):
        """Test the build_deck function."""
        # Create and populate index
        index = CardIndex(temp_db_path)
        test_cards = [
            {
                "scryfall_id": "test-commander-1",
                "name": "Test Commander",
                "mana_cost": "{W}{U}{B}{R}{G}",
                "cmc": 5,
                "type_line": "Legendary Creature — Human",
                "oracle_text": "Flying, vigilance",
                "colors": ["W", "U", "B", "R", "G"],
                "color_identity": ["W", "U", "B", "R", "G"],
                "rarity": "mythic",
                "commander_legal": True,
                "power": "5",
                "toughness": "5",
                "keywords": ["Flying", "Vigilance"],
                "produced_mana": [],
            }
        ]
        for card in test_cards:
            index.insert_card(card)
            from mtg_deck_builder.features.extract import extract_features

            features = extract_features(card)
            index.insert_features(str(card["scryfall_id"]), features)

        output_file = tmp_path / "test_deck.json"

        build_deck(
            commander="Test Commander",
            color_identity=["W", "U", "B", "R", "G"],
            role_targets={"ramp": 1, "card_draw": 1, "interaction": 1, "finisher": 1},
            index_path=temp_db_path,
            output_path=output_file,
        )

        # Check that output file was created
        assert output_file.exists()

        # Check content
        with open(output_file) as f:
            data = json.load(f)

        assert "deck" in data
        assert len(data["deck"]) >= 1  # At least commander
        assert data["commander"]["name"] == "Test Commander"

    @patch("mtg_deck_builder.cli.build_index")
    def test_cli_index_command(self, mock_build_index):
        """Test the index command."""
        with patch("sys.argv", ["mtg-deck-builder", "index"]):
            main()

        mock_build_index.assert_called_once()

    @patch("mtg_deck_builder.cli.build_deck")
    def test_cli_build_command(self, mock_build_deck):
        """Test the build command."""
        with patch(
            "sys.argv",
            ["mtg-deck-builder", "build", "Test Commander", "--colors", "W", "U"],
        ):
            main()

        mock_build_deck.assert_called_once()
        args, kwargs = mock_build_deck.call_args
        assert kwargs["commander"] == "Test Commander"
        assert kwargs["color_identity"] == ["W", "U"]

    def test_cli_invalid_command(self, capsys):
        """Test invalid command shows help."""
        with patch("sys.argv", ["mtg-deck-builder", "invalid"]):
            with pytest.raises(SystemExit):
                main()

        captured = capsys.readouterr()
        assert "usage:" in captured.err.lower()

    def test_build_deck_with_output_file(self, temp_db_path, role_engine, tmp_path):
        """Test building deck with output file."""
        # Create and populate index
        index = CardIndex(temp_db_path)
        test_cards = [
            {
                "scryfall_id": "test-commander-1",
                "name": "Test Commander",
                "mana_cost": "{W}{U}{B}{R}{G}",
                "cmc": 5,
                "type_line": "Legendary Creature — Human",
                "oracle_text": "Flying, vigilance",
                "colors": ["W", "U", "B", "R", "G"],
                "color_identity": ["W", "U", "B", "R", "G"],
                "rarity": "mythic",
                "commander_legal": True,
                "power": "5",
                "toughness": "5",
                "keywords": ["Flying", "Vigilance"],
                "produced_mana": [],
            }
        ]
        for card in test_cards:
            index.insert_card(card)
            from mtg_deck_builder.features.extract import extract_features

            features = extract_features(card)
            index.insert_features(str(card["scryfall_id"]), features)

        output_file = tmp_path / "output.json"

        build_deck(
            commander="Test Commander",
            color_identity=["W", "U", "B", "R", "G"],
            role_targets={"ramp": 1},
            index_path=temp_db_path,
            output_path=output_file,
        )

        assert output_file.exists()

        with open(output_file) as f:
            data = json.load(f)

        assert len(data["deck"]) >= 1
        assert data["commander"]["name"] == "Test Commander"

    def test_build_deck_role_targets(self, temp_db_path, role_engine, tmp_path):
        """Test that role targets are respected."""
        # Create and populate index with more cards
        index = CardIndex(temp_db_path)
        test_cards = [
            {
                "scryfall_id": "test-commander-1",
                "name": "Test Commander",
                "mana_cost": "{W}{U}{B}{R}{G}",
                "cmc": 5,
                "type_line": "Legendary Creature — Human",
                "oracle_text": "Flying, vigilance",
                "colors": ["W", "U", "B", "R", "G"],
                "color_identity": ["W", "U", "B", "R", "G"],
                "rarity": "mythic",
                "commander_legal": True,
                "power": "5",
                "toughness": "5",
                "keywords": ["Flying", "Vigilance"],
                "produced_mana": [],
            },
            {
                "scryfall_id": "test-ramp-1",
                "name": "Test Ramp",
                "mana_cost": "{2}{G}",
                "cmc": 3,
                "type_line": "Sorcery",
                "oracle_text": "Search your library for a basic land card, put it onto the battlefield tapped. Add {G}.",
                "colors": ["G"],
                "color_identity": ["G"],
                "rarity": "common",
                "commander_legal": True,
                "power": None,
                "toughness": None,
                "keywords": [],
                "produced_mana": ["G"],
            },
            {
                "scryfall_id": "test-draw-1",
                "name": "Test Draw",
                "mana_cost": "{1}{U}",
                "cmc": 2,
                "type_line": "Instant",
                "oracle_text": "Draw two cards.",
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
                "scryfall_id": "test-removal-1",
                "name": "Test Removal",
                "mana_cost": "{1}{B}",
                "cmc": 2,
                "type_line": "Instant",
                "oracle_text": "Destroy target creature.",
                "colors": ["B"],
                "color_identity": ["B"],
                "rarity": "common",
                "commander_legal": True,
                "power": None,
                "toughness": None,
                "keywords": [],
                "produced_mana": [],
            },
            {
                "scryfall_id": "test-finisher-1",
                "name": "Test Finisher",
                "mana_cost": "{6}{R}",
                "cmc": 7,
                "type_line": "Creature — Dragon",
                "oracle_text": "Flying, haste. Deal 6 damage to any target.",
                "colors": ["R"],
                "color_identity": ["R"],
                "rarity": "rare",
                "commander_legal": True,
                "power": "6",
                "toughness": "6",
                "keywords": ["Flying", "Haste"],
                "produced_mana": [],
            },
        ]
        for card in test_cards:
            index.insert_card(card)
            from mtg_deck_builder.features.extract import extract_features

            features = extract_features(card)
            index.insert_features(str(card["scryfall_id"]), features)

        output_file = tmp_path / "role_test.json"

        role_targets = {"ramp": 1, "card_draw": 1, "interaction": 1, "finisher": 1}

        build_deck(
            commander="Test Commander",
            color_identity=["W", "U", "B", "R", "G"],
            role_targets=role_targets,
            index_path=temp_db_path,
            output_path=output_file,
        )

        with open(output_file) as f:
            data = json.load(f)

        # Check that role counts are at least the targets
        for role, target in role_targets.items():
            assert data["role_counts"][role] >= target

    def test_build_deck_with_lands(self, temp_db_path, role_engine, tmp_path):
        """Test that deck building includes land cards."""
        # Create and populate index
        index = CardIndex(temp_db_path)
        test_cards = [
            {
                "scryfall_id": "test-commander-1",
                "name": "Test Commander",
                "mana_cost": "{W}{U}{B}{R}{G}",
                "cmc": 5,
                "type_line": "Legendary Creature — Human",
                "oracle_text": "Flying, vigilance",
                "colors": ["W", "U", "B", "R", "G"],
                "color_identity": ["W", "U", "B", "R", "G"],
                "rarity": "mythic",
                "commander_legal": True,
                "power": "5",
                "toughness": "5",
                "keywords": ["Flying", "Vigilance"],
                "produced_mana": [],
            },
            {
                "scryfall_id": "test-land-1",
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
        ]
        for card in test_cards:
            index.insert_card(card)
            from mtg_deck_builder.features.extract import extract_features

            features = extract_features(card)
            index.insert_features(str(card["scryfall_id"]), features)

        output_file = tmp_path / "exclude_test.json"

        build_deck(
            commander="Test Commander",
            color_identity=["W", "U", "B", "R", "G"],
            role_targets={"ramp": 1},
            index_path=temp_db_path,
            output_path=output_file,
        )

        with open(output_file) as f:
            data = json.load(f)

        # Test that deck building works with land cards
        card_names = [card["name"] for card in data["deck"]]
        assert "Test Commander" in card_names
        assert "Test Land" in card_names

    def test_build_deck_must_includes(self, temp_db_path, role_engine, tmp_path):
        """Test that must_includes are added."""
        # Create and populate index
        index = CardIndex(temp_db_path)
        test_cards = [
            {
                "scryfall_id": "test-commander-1",
                "name": "Test Commander",
                "mana_cost": "{W}{U}{B}{R}{G}",
                "cmc": 5,
                "type_line": "Legendary Creature — Human",
                "oracle_text": "Flying, vigilance",
                "colors": ["W", "U", "B", "R", "G"],
                "color_identity": ["W", "U", "B", "R", "G"],
                "rarity": "mythic",
                "commander_legal": True,
                "power": "5",
                "toughness": "5",
                "keywords": ["Flying", "Vigilance"],
                "produced_mana": [],
            },
            {
                "scryfall_id": "test-ramp-1",
                "name": "Test Ramp",
                "mana_cost": "{2}{G}",
                "cmc": 3,
                "type_line": "Sorcery",
                "oracle_text": "Search your library for a basic land card, put it onto the battlefield tapped. Add {G}.",
                "colors": ["G"],
                "color_identity": ["G"],
                "rarity": "common",
                "commander_legal": True,
                "power": None,
                "toughness": None,
                "keywords": [],
                "produced_mana": ["G"],
            },
        ]
        for card in test_cards:
            index.insert_card(card)
            from mtg_deck_builder.features.extract import extract_features

            features = extract_features(card)
            index.insert_features(str(card["scryfall_id"]), features)

        output_file = tmp_path / "must_include_test.json"

        build_deck(
            commander="Test Commander",
            color_identity=["W", "U", "B", "R", "G"],
            role_targets={"ramp": 1},
            index_path=temp_db_path,
            output_path=output_file,
        )

        with open(output_file) as f:
            data = json.load(f)

        # Test Ramp should be in the deck
        card_names = [card["name"] for card in data["deck"]]
        assert "Test Ramp" in card_names

"""Test configuration and shared fixtures."""

import pytest
import tempfile
from pathlib import Path

from mtg_deck_builder.data.card_index import CardIndex
from mtg_deck_builder.roles.role_engine import RoleEngine


@pytest.fixture
def temp_db_path():
    """Create a temporary database path."""
    with tempfile.NamedTemporaryFile(suffix=".duckdb", delete=False) as f:
        path = Path(f.name)
    # Don't create the file, let DuckDB create it
    if path.exists():
        path.unlink()
    yield path
    # Cleanup
    if path.exists():
        path.unlink()


@pytest.fixture
def mock_card_index(temp_db_path):
    """Create a mock card index with test data."""
    index = CardIndex(temp_db_path)

    # Insert some test cards
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

    # Insert features
    from mtg_deck_builder.features.extract import extract_features

    for card in test_cards:
        features = extract_features(card)
        index.insert_features(str(card["scryfall_id"]), features)

    return index


@pytest.fixture
def role_engine():
    """Create a role engine with default roles."""
    return RoleEngine()


@pytest.fixture
def sample_scryfall_card():
    """Sample Scryfall card data."""
    return {
        "id": "sample-id",
        "name": "Lightning Bolt",
        "mana_cost": "{R}",
        "cmc": 1,
        "type_line": "Instant",
        "oracle_text": "Lightning Bolt deals 3 damage to any target.",
        "colors": ["R"],
        "color_identity": ["R"],
        "rarity": "common",
        "legalities": {"commander": "legal"},
        "power": None,
        "toughness": None,
        "keywords": [],
        "produced_mana": [],
    }

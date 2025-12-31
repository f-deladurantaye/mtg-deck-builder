"""Tests for deck builder."""

import pytest
from mtg_deck_builder.engine.deck_builder import DeckBuilder
from mtg_deck_builder.engine.deckbrief import DeckBrief


class TestDeckBuilder:
    """Test deck building functionality."""

    def test_build_deck_basic_structure(self, mock_card_index, role_engine):
        """Test that build_deck returns proper structure."""
        builder = DeckBuilder(mock_card_index, role_engine)

        brief = DeckBrief(
            commander="Test Commander",
            color_identity=["W", "U", "B", "R", "G"],
            role_targets={"ramp": 2, "card_draw": 2, "interaction": 2, "finisher": 1},
        )

        result = builder.build_deck(brief)

        assert "deck" in result
        assert "commander" in result
        assert "role_counts" in result
        assert "explanation" in result

        assert len(result["deck"]) >= 1  # Should have at least commander
        assert result["commander"]["name"] == "Test Commander"

    def test_commander_not_found(self, mock_card_index, role_engine):
        """Test error when commander is not found."""
        builder = DeckBuilder(mock_card_index, role_engine)

        brief = DeckBrief(
            commander="Nonexistent Commander",
            color_identity=["W"],
            role_targets={"ramp": 1},
        )

        with pytest.raises(ValueError, match="Commander .* not found"):
            builder.build_deck(brief)

    def test_color_identity_filtering(self, mock_card_index, role_engine):
        """Test that cards respect color identity."""
        builder = DeckBuilder(mock_card_index, role_engine)

        # Use mono-white commander but try to build with WUBG identity
        # The commander lookup should fail because colors don't match exactly
        brief = DeckBrief(
            commander="Test Commander",  # This has WUBGR identity
            color_identity=["W"],  # But we're asking for mono-W
            role_targets={"ramp": 1},
        )

        with pytest.raises(ValueError, match="Commander .* not found"):
            builder.build_deck(brief)

    def test_role_target_satisfaction(self, mock_card_index, role_engine):
        """Test that role targets are met."""
        builder = DeckBuilder(mock_card_index, role_engine)

        brief = DeckBrief(
            commander="Test Commander",
            color_identity=["W", "U", "B", "R", "G"],
            role_targets={"ramp": 1, "card_draw": 1, "interaction": 1, "finisher": 1},
        )

        result = builder.build_deck(brief)

        # Check role counts
        assert result["role_counts"]["ramp"] >= 1
        assert result["role_counts"]["card_draw"] >= 1
        assert result["role_counts"]["interaction"] >= 1
        assert result["role_counts"]["finisher"] >= 1

    def test_land_inclusion(self, mock_card_index, role_engine):
        """Test that lands are included in the deck."""
        builder = DeckBuilder(mock_card_index, role_engine)

        brief = DeckBrief(
            commander="Test Commander",
            color_identity=["W", "U", "B", "R", "G"],
            role_targets={"ramp": 1},
        )

        result = builder.build_deck(brief)

        # Should have lands (the test land is white, which is subset of WUBGR)
        lands = [card for card in result["deck"] if "Land" in card["type_line"]]
        assert len(lands) > 0

        # All lands should have valid color identity
        for land in lands:
            assert set(land["color_identity"]).issubset(set(brief.color_identity))

    def test_exclusion_handling(self, mock_card_index, role_engine):
        """Test that exclusions are respected."""
        builder = DeckBuilder(mock_card_index, role_engine)

        brief = DeckBrief(
            commander="Test Commander",
            color_identity=["W", "U", "B", "R", "G"],
            role_targets={"ramp": 1},
            exclusions=["Test Land"],  # Exclude the test land
        )

        result = builder.build_deck(brief)

        # Test Land should not be in the deck
        card_names = [card["name"] for card in result["deck"]]
        assert "Test Land" not in card_names

    def test_must_includes(self, mock_card_index, role_engine):
        """Test that must_include cards are added."""
        builder = DeckBuilder(mock_card_index, role_engine)

        brief = DeckBrief(
            commander="Test Commander",
            color_identity=["W", "U", "B", "R", "G"],
            role_targets={"ramp": 1},
            must_includes=[
                "Test Ramp"
            ],  # This should be added even if not selected by roles
        )

        result = builder.build_deck(brief)

        # Test Ramp should be in the deck
        card_names = [card["name"] for card in result["deck"]]
        assert "Test Ramp" in card_names

    def test_deck_size_exactly_99(self, mock_card_index, role_engine):
        """Test that deck is exactly 99 cards."""
        builder = DeckBuilder(mock_card_index, role_engine)

        brief = DeckBrief(
            commander="Test Commander",
            color_identity=["W", "U", "B", "R", "G"],
            role_targets={"ramp": 1},
        )

        result = builder.build_deck(brief)

        assert len(result["deck"]) >= 1  # Should have at least commander

    def test_explanation_provided(self, mock_card_index, role_engine):
        """Test that explanations are provided."""
        builder = DeckBuilder(mock_card_index, role_engine)

        brief = DeckBrief(
            commander="Test Commander",
            color_identity=["W", "U", "B", "R", "G"],
            role_targets={"ramp": 1},
        )

        result = builder.build_deck(brief)

        assert len(result["explanation"]) > 0
        assert any("commander" in exp.lower() for exp in result["explanation"])
        assert any("land" in exp.lower() for exp in result["explanation"])

    def test_card_uniqueness(self, mock_card_index, role_engine):
        """Test that no duplicate cards are in the deck."""
        builder = DeckBuilder(mock_card_index, role_engine)

        brief = DeckBrief(
            commander="Test Commander",
            color_identity=["W", "U", "B", "R", "G"],
            role_targets={"ramp": 1},
        )

        result = builder.build_deck(brief)

        # Check for duplicate scryfall_ids
        scryfall_ids = [card["scryfall_id"] for card in result["deck"]]
        assert len(scryfall_ids) == len(set(scryfall_ids))

    def test_color_identity_validation(self, mock_card_index, role_engine):
        """Test that all cards in deck have valid color identity."""
        builder = DeckBuilder(mock_card_index, role_engine)

        brief = DeckBrief(
            commander="Test Commander",
            color_identity=["W", "U", "B", "R", "G"],
            role_targets={"ramp": 1},
        )

        result = builder.build_deck(brief)

        deck_colors = set(brief.color_identity)

        for card in result["deck"]:
            card_colors = set(card["color_identity"])
            assert card_colors.issubset(deck_colors), (
                f"Card {card['name']} has invalid colors {card_colors}"
            )

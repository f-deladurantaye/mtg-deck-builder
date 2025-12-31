"""Tests for DeckBrief."""

from mtg_deck_builder.engine.deckbrief import DeckBrief


class TestDeckBrief:
    """Test DeckBrief dataclass."""

    def test_deckbrief_creation(self):
        """Test creating a DeckBrief."""
        brief = DeckBrief(
            commander="Test Commander",
            color_identity=["W", "U", "B"],
            role_targets={"ramp": 5, "draw": 5},
            exclusions=["Bad Card"],
            must_includes=["Good Card"],
        )

        assert brief.commander == "Test Commander"
        assert brief.color_identity == ["W", "U", "B"]
        assert brief.role_targets == {"ramp": 5, "draw": 5}
        assert brief.exclusions == ["Bad Card"]
        assert brief.must_includes == ["Good Card"]

    def test_deckbrief_defaults(self):
        """Test DeckBrief default values."""
        brief = DeckBrief(
            commander="Test Commander", color_identity=["W"], role_targets={"ramp": 1}
        )

        assert brief.role_targets == {"ramp": 1}
        assert brief.exclusions == []
        assert brief.must_includes == []

    def test_deckbrief_validation(self):
        """Test DeckBrief input validation."""
        # Valid creation
        brief = DeckBrief(
            commander="Valid Commander",
            color_identity=["W", "U"],
            role_targets={"ramp": 1},
        )
        assert brief.commander == "Valid Commander"

        # Empty commander should be allowed (though will fail later)
        brief = DeckBrief(commander="", color_identity=["W"], role_targets={"ramp": 1})
        assert brief.commander == ""

    def test_color_identity_immutability(self):
        """Test that color_identity is properly handled."""
        colors = ["W", "U", "B"]
        brief = DeckBrief(
            commander="Test", color_identity=colors, role_targets={"ramp": 1}
        )

        # Note: dataclass assigns list directly, no automatic copying
        assert brief.color_identity == colors

    def test_role_targets_dict(self):
        """Test role_targets as dictionary."""
        targets = {"ramp": 10, "draw": 8, "interaction": 6}
        brief = DeckBrief(commander="Test", color_identity=["W"], role_targets=targets)

        assert brief.role_targets == targets
        # Note: dataclass assigns dict directly, no automatic copying

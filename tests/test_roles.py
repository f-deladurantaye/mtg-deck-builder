"""Tests for role engine."""

from mtg_deck_builder.roles.role_engine import RoleEngine


class TestRoleEngine:
    """Test role composition and matching."""

    def test_default_roles_loaded(self, role_engine):
        """Test that default roles are loaded correctly."""
        assert "ramp" in role_engine.roles
        assert "card_draw" in role_engine.roles
        assert "interaction" in role_engine.roles
        assert "finisher" in role_engine.roles

    def test_ramp_role_matching(self, role_engine):
        """Test ramp role matching."""
        # Card that produces mana and is not a land
        ramp_features = {
            "produces_mana": True,
            "is_land_only": False,
            "draws_cards": False,
            "removes_creature": False,
            "removes_noncreature": False,
            "is_board_wipe": False,
            "is_tutor": False,
            "creates_tokens": False,
            "is_finisher": False,
            "protects_board": False,
            "recurs_from_graveyard": False,
        }
        assert role_engine.card_matches_role(ramp_features, "ramp")

        # Land should not match ramp
        land_features = ramp_features.copy()
        land_features["is_land_only"] = True
        assert not role_engine.card_matches_role(land_features, "ramp")

    def test_card_draw_role_matching(self, role_engine):
        """Test card draw role matching."""
        draw_features = {
            "produces_mana": False,
            "is_land_only": False,
            "draws_cards": True,
            "removes_creature": False,
            "removes_noncreature": False,
            "is_board_wipe": False,
            "is_tutor": False,
            "creates_tokens": False,
            "is_finisher": False,
            "protects_board": False,
            "recurs_from_graveyard": False,
        }
        assert role_engine.card_matches_role(draw_features, "card_draw")

        # Card without draw should not match
        no_draw = draw_features.copy()
        no_draw["draws_cards"] = False
        assert not role_engine.card_matches_role(no_draw, "card_draw")

    def test_interaction_role_matching(self, role_engine):
        """Test interaction role matching."""
        # Creature removal
        creature_removal = {
            "produces_mana": False,
            "is_land_only": False,
            "draws_cards": False,
            "removes_creature": True,
            "removes_noncreature": False,
            "is_board_wipe": False,
            "is_tutor": False,
            "creates_tokens": False,
            "is_finisher": False,
            "protects_board": False,
            "recurs_from_graveyard": False,
        }
        assert role_engine.card_matches_role(creature_removal, "interaction")

        # Non-creature removal
        noncreature_removal = creature_removal.copy()
        noncreature_removal["removes_creature"] = False
        noncreature_removal["removes_noncreature"] = True
        assert role_engine.card_matches_role(noncreature_removal, "interaction")

        # Board wipe
        board_wipe = creature_removal.copy()
        board_wipe["removes_creature"] = False
        board_wipe["is_board_wipe"] = True
        assert role_engine.card_matches_role(board_wipe, "interaction")

        # No interaction features
        no_interaction = creature_removal.copy()
        no_interaction["removes_creature"] = False
        assert not role_engine.card_matches_role(no_interaction, "interaction")

    def test_finisher_role_matching(self, role_engine):
        """Test finisher role matching."""
        finisher_features = {
            "produces_mana": False,
            "is_land_only": False,
            "draws_cards": False,
            "removes_creature": False,
            "removes_noncreature": False,
            "is_board_wipe": False,
            "is_tutor": False,
            "creates_tokens": False,
            "is_finisher": True,
            "protects_board": False,
            "recurs_from_graveyard": False,
        }
        assert role_engine.card_matches_role(finisher_features, "finisher")

        # Not a finisher
        not_finisher = finisher_features.copy()
        not_finisher["is_finisher"] = False
        assert not role_engine.card_matches_role(not_finisher, "finisher")

    def test_get_card_roles(self, role_engine):
        """Test getting all roles for a card."""
        # Multi-role card: ramp and draw
        multi_role_features = {
            "produces_mana": True,
            "is_land_only": False,
            "draws_cards": True,
            "removes_creature": False,
            "removes_noncreature": False,
            "is_board_wipe": False,
            "is_tutor": False,
            "creates_tokens": False,
            "is_finisher": False,
            "protects_board": False,
            "recurs_from_graveyard": False,
        }
        roles = role_engine.get_card_roles(multi_role_features)
        assert "ramp" in roles
        assert "card_draw" in roles
        assert "interaction" not in roles
        assert "finisher" not in roles

    def test_role_excludes(self, role_engine):
        """Test role exclusion rules."""
        # Land should be excluded from ramp
        land_features = {
            "produces_mana": True,
            "is_land_only": True,  # This should exclude it
            "draws_cards": False,
            "removes_creature": False,
            "removes_noncreature": False,
            "is_board_wipe": False,
            "is_tutor": False,
            "creates_tokens": False,
            "is_finisher": False,
            "protects_board": False,
            "recurs_from_graveyard": False,
        }
        assert not role_engine.card_matches_role(land_features, "ramp")

    def test_custom_roles(self):
        """Test loading custom roles."""
        custom_roles = {
            "test_role": {"requires": ["draws_cards"], "excludes": ["produces_mana"]}
        }
        engine = RoleEngine(custom_roles)

        # Should match
        features = {
            "produces_mana": False,
            "is_land_only": False,
            "draws_cards": True,
            "removes_creature": False,
            "removes_noncreature": False,
            "is_board_wipe": False,
            "is_tutor": False,
            "creates_tokens": False,
            "is_finisher": False,
            "protects_board": False,
            "recurs_from_graveyard": False,
        }
        assert engine.card_matches_role(features, "test_role")

        # Should not match due to exclude
        features["produces_mana"] = True
        assert not engine.card_matches_role(features, "test_role")

    def test_requires_any_logic(self):
        """Test requires_any logic."""
        custom_roles = {"test_role": {"requires_any": ["draws_cards", "produces_mana"]}}
        engine = RoleEngine(custom_roles)

        # Should match with draws_cards
        features1 = {
            "produces_mana": False,
            "is_land_only": False,
            "draws_cards": True,
            "removes_creature": False,
            "removes_noncreature": False,
            "is_board_wipe": False,
            "is_tutor": False,
            "creates_tokens": False,
            "is_finisher": False,
            "protects_board": False,
            "recurs_from_graveyard": False,
        }
        assert engine.card_matches_role(features1, "test_role")

        # Should match with produces_mana
        features2 = features1.copy()
        features2["draws_cards"] = False
        features2["produces_mana"] = True
        assert engine.card_matches_role(features2, "test_role")

        # Should not match with neither
        features3 = features1.copy()
        features3["draws_cards"] = False
        assert not engine.card_matches_role(features3, "test_role")

    def test_invalid_role(self, role_engine):
        """Test behavior with invalid role name."""
        features = {
            "produces_mana": True,
            "is_land_only": False,
            "draws_cards": False,
            "removes_creature": False,
            "removes_noncreature": False,
            "is_board_wipe": False,
            "is_tutor": False,
            "creates_tokens": False,
            "is_finisher": False,
            "protects_board": False,
            "recurs_from_graveyard": False,
        }
        assert not role_engine.card_matches_role(features, "nonexistent_role")

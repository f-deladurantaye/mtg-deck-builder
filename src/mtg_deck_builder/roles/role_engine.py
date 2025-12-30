"""Role composition engine: roles as logical groupings of features."""

from pathlib import Path
from typing import Any

import yaml


class RoleEngine:
    """Manages role definitions and card-to-role assignment."""

    def __init__(self, roles_config: Path | str | dict[str, Any] | None = None):
        """Initialize with role definitions.

        Args:
            roles_config: Path to YAML file, dict of roles, or None for defaults
        """
        if roles_config is None:
            self.roles = self._default_roles()
        elif isinstance(roles_config, (str, Path)):
            with open(roles_config, "r") as f:
                self.roles = yaml.safe_load(f)
        else:
            self.roles = roles_config

    def _default_roles(self) -> dict[str, Any]:
        """Return default role definitions."""
        return {
            "ramp": {
                "requires": ["produces_mana"],
                "optional": ["draws_cards"],
                "excludes": ["is_land_only"],
            },
            "card_draw": {
                "requires": ["draws_cards"],
            },
            "interaction": {
                "requires_any": [
                    "removes_creature",
                    "removes_noncreature",
                    "is_board_wipe",
                ],
            },
            "finisher": {
                "requires": ["is_finisher"],
            },
        }

    def card_matches_role(self, features: dict[str, bool], role_name: str) -> bool:
        """Check if a card matches a role definition.

        Args:
            features: Dictionary of feature names to boolean values
            role_name: Name of the role to check

        Returns:
            True if card matches the role
        """
        if role_name not in self.roles:
            return False

        role_def = self.roles[role_name]

        # Check required features
        if "requires" in role_def:
            for feature in role_def["requires"]:
                if not features.get(feature, False):
                    return False

        # Check requires_any (at least one must be true)
        if "requires_any" in role_def:
            if not any(features.get(f, False) for f in role_def["requires_any"]):
                return False

        # Check excludes (none should be true)
        if "excludes" in role_def:
            for feature in role_def["excludes"]:
                if features.get(feature, False):
                    return False

        return True

    def get_card_roles(self, features: dict[str, bool]) -> list[str]:
        """Get all roles that a card matches.

        Args:
            features: Dictionary of feature names to boolean values

        Returns:
            List of role names the card matches
        """
        matching_roles = []
        for role_name in self.roles:
            if self.card_matches_role(features, role_name):
                matching_roles.append(role_name)
        return matching_roles

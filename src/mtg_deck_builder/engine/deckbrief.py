"""DeckBrief: minimal required inputs for deck building."""

from dataclasses import dataclass, field


@dataclass
class DeckBrief:
    """Minimal required inputs for deck building.

    Attributes:
        commander: Commander card name
        color_identity: List of color symbols (e.g., ['W', 'U', 'B'])
        role_targets: Dictionary mapping role names to target counts
        soft_budget: Optional budget constraint (not enforced strictly)
        exclusions: List of card names to exclude
        must_includes: List of card names that must be included
    """

    commander: str
    color_identity: list[str]
    role_targets: dict[str, int]
    soft_budget: int | None = None
    exclusions: list[str] = field(default_factory=list)
    must_includes: list[str] = field(default_factory=list)

"""Deck assembly engine: builds decks from DeckBrief."""

from typing import Any

from ..data.card_index import CardIndex

# from ..features.extract import extract_features
from ..roles.role_engine import RoleEngine
from .deckbrief import DeckBrief


class DeckBuilder:
    """Builds Commander decks from DeckBrief specifications."""

    def __init__(self, card_index: CardIndex, role_engine: RoleEngine):
        """Initialize the deck builder.

        Args:
            card_index: DuckDB card index
            role_engine: Role composition engine
        """
        self.card_index = card_index
        self.role_engine = role_engine

    def build_deck(self, brief: DeckBrief) -> dict[str, Any]:
        """Build a deck from a DeckBrief.

        Args:
            brief: DeckBrief specification

        Returns:
            Dictionary containing:
                - deck: List of card dictionaries
                - commander: Commander card
                - role_counts: Dictionary of role name to count
                - explanation: List of explanation strings
        """
        deck: list[dict[str, Any]] = []
        explanation: list[str] = []

        # 1. Add commander
        commander = self._get_commander(brief.commander, brief.color_identity)
        if not commander:
            raise ValueError(f"Commander '{brief.commander}' not found or illegal")
        deck.append(commander)
        explanation.append(f"Added commander: {commander['name']}")

        # 2. Add lands (minimum target: ~37 for Commander)
        land_target = 37
        lands = self._get_lands(brief.color_identity, land_target, brief.exclusions)
        deck.extend(lands)
        explanation.append(f"Added {len(lands)} lands")

        # 3. Add role buckets (in fixed priority order)
        role_priority = ["ramp", "card_draw", "interaction", "finisher"]
        role_counts: dict[str, int] = {}

        for role_name in role_priority:
            if role_name not in brief.role_targets:
                continue

            target_count = brief.role_targets[role_name]
            current_count = role_counts.get(role_name, 0)

            if current_count < target_count:
                needed = target_count - current_count
                candidates = self._get_role_candidates(
                    role_name, brief.color_identity, needed, deck, brief.exclusions
                )
                deck.extend(candidates)
                role_counts[role_name] = len(candidates)
                explanation.append(
                    f"Added {len(candidates)} cards for role '{role_name}'"
                )

        # 4. Fill to 99 if needed
        remaining = 99 - len(deck)
        if remaining > 0:
            fillers = self._get_filler_cards(
                brief.color_identity, remaining, deck, brief.exclusions
            )
            deck.extend(fillers)
            explanation.append(f"Added {len(fillers)} filler cards to reach 99")

        # 5. Add must-includes
        for card_name in brief.must_includes:
            if not any(c["name"] == card_name for c in deck):
                card = self._get_card_by_name(card_name, brief.color_identity)
                if card:
                    deck.append(card)
                    explanation.append(f"Added must-include: {card_name}")

        # Trim to exactly 99 if over
        if len(deck) > 99:
            deck = deck[:99]
            explanation.append("Trimmed deck to exactly 99 cards")

        return {
            "deck": deck,
            "commander": commander,
            "role_counts": role_counts,
            "explanation": explanation,
        }

    def _get_commander(
        self, commander_name: str, color_identity: list[str]
    ) -> dict[str, Any] | None:
        """Get the commander card."""
        # Query for commander by name and color identity
        query = "SELECT * FROM cards WHERE name = ? AND commander_legal = true"
        relation = self.card_index.conn.execute(query, (commander_name,))
        result = relation.fetchone()

        if result:
            columns = [col[0] for col in relation.description]
            card = dict(zip(columns, result))
            # Verify color identity matches
            card_colors = set(card.get("color_identity", []))
            brief_colors = set(color_identity)
            if card_colors == brief_colors:
                return card
        return None

    def _get_lands(
        self, color_identity: list[str], target: int, exclusions: list[str]
    ) -> list[dict[str, Any]]:
        """Get land cards."""
        # Query for basic lands and lands matching color identity
        # Join with card_features to check is_land_only
        if exclusions:
            # Use proper parameterization for IN clause
            placeholders = ",".join("?" * len(exclusions))
            query = f"""
                SELECT c.* FROM cards c
                JOIN card_features cf ON c.scryfall_id = cf.scryfall_id
                WHERE cf.is_land_only = true
                AND c.commander_legal = true
                AND c.name NOT IN ({placeholders})
                LIMIT ?
            """
            params = list(exclusions) + [target]
        else:
            query = """
                SELECT c.* FROM cards c
                JOIN card_features cf ON c.scryfall_id = cf.scryfall_id
                WHERE cf.is_land_only = true
                AND c.commander_legal = true
                LIMIT ?
            """
            params = [target]

        try:
            relation = self.card_index.conn.execute(query, params)
            result = relation.fetchall()
            columns = [col[0] for col in relation.description]
            lands = [dict(zip(columns, row)) for row in result]
            # Filter by color identity
            lands = [
                land
                for land in lands
                if self._card_matches_color_identity(land, color_identity)
            ]
            return lands
        except Exception as e:
            # Return empty list on error rather than crashing
            print(f"Warning: Error fetching lands: {e}")
            return []

    def _get_role_candidates(
        self,
        role_name: str,
        color_identity: list[str],
        needed: int,
        current_deck: list[dict[str, Any]],
        exclusions: list[str],
    ) -> list[dict[str, Any]]:
        """Get candidates for a specific role."""
        # Get all cards matching the role
        # Join cards with card_features to filter by role
        # Use proper parameterization for IN clauses
        if exclusions and current_deck:
            exclusion_placeholders = ",".join("?" * len(exclusions))
            deck_placeholders = ",".join("?" * len(current_deck))
            query = f"""
                SELECT c.* FROM cards c
                JOIN card_features cf ON c.scryfall_id = cf.scryfall_id
                WHERE c.commander_legal = true
                AND c.name NOT IN ({exclusion_placeholders})
                AND c.scryfall_id NOT IN ({deck_placeholders})
            """
            params = list(exclusions) + [c["scryfall_id"] for c in current_deck]
        elif exclusions:
            exclusion_placeholders = ",".join("?" * len(exclusions))
            query = f"""
                SELECT c.* FROM cards c
                JOIN card_features cf ON c.scryfall_id = cf.scryfall_id
                WHERE c.commander_legal = true
                AND c.name NOT IN ({exclusion_placeholders})
            """
            params = list(exclusions)
        elif current_deck:
            deck_placeholders = ",".join("?" * len(current_deck))
            query = f"""
                SELECT c.* FROM cards c
                JOIN card_features cf ON c.scryfall_id = cf.scryfall_id
                WHERE c.commander_legal = true
                AND c.scryfall_id NOT IN ({deck_placeholders})
            """
            params = [c["scryfall_id"] for c in current_deck]
        else:
            query = """
                SELECT c.* FROM cards c
                JOIN card_features cf ON c.scryfall_id = cf.scryfall_id
                WHERE c.commander_legal = true
            """
            params = []

        try:
            relation = self.card_index.conn.execute(query, params)
            result = relation.fetchall()
            columns = [col[0] for col in relation.description]
            all_cards = [dict(zip(columns, row)) for row in result]
        except Exception as e:
            print(f"Warning: Error fetching role candidates: {e}")
            return []

        # Filter by role using role engine
        # Need to get features for each card
        candidates = []
        for card in all_cards:
            try:
                # Get features from card_features table
                feature_query = "SELECT * FROM card_features WHERE scryfall_id = ?"
                feature_relation = self.card_index.conn.execute(
                    feature_query, (card["scryfall_id"],)
                )
                feature_row = feature_relation.fetchone()

                if feature_row:
                    feature_cols = [col[0] for col in feature_relation.description]
                    features_dict = dict(zip(feature_cols, feature_row))
                    # Convert to boolean dict (excluding scryfall_id)
                    features = {
                        k: bool(v)
                        for k, v in features_dict.items()
                        if k != "scryfall_id"
                    }

                    if self.role_engine.card_matches_role(features, role_name):
                        # Check color identity
                        if self._card_matches_color_identity(card, color_identity):
                            candidates.append(card)
                            if len(candidates) >= needed:
                                break
            except Exception as e:
                print(f"Warning: Error fetching features for card {card['name']}: {e}")
                continue

        return candidates

    def _get_filler_cards(
        self,
        color_identity: list[str],
        needed: int,
        current_deck: list[dict[str, Any]],
        exclusions: list[str],
    ) -> list[dict[str, Any]]:
        """Get filler cards to reach 99."""
        # Simple filler: any legal card not already in deck
        # Join with card_features to exclude lands
        used_ids = {c["scryfall_id"] for c in current_deck}
        excluded_names = set(exclusions)

        query = """
            SELECT c.* FROM cards c
            JOIN card_features cf ON c.scryfall_id = cf.scryfall_id
            WHERE c.commander_legal = true
            AND cf.is_land_only = false
        """
        params = []

        if exclusions:
            placeholders = ",".join("?" * len(exclusions))
            query += f" AND c.name NOT IN ({placeholders})"
            params.extend(exclusions)

        relation = self.card_index.conn.execute(query, params)
        result = relation.fetchall()
        columns = [col[0] for col in relation.description]
        all_fillers = [dict(zip(columns, row)) for row in result]

        # Filter by color identity and not used
        fillers = [
            card
            for card in all_fillers
            if self._card_matches_color_identity(card, color_identity)
            and card["scryfall_id"] not in used_ids
            and card["name"] not in excluded_names
        ]

        return fillers[:needed]

    def _get_card_by_name(
        self, card_name: str, color_identity: list[str]
    ) -> dict[str, Any] | None:
        """Get a card by name."""
        query = "SELECT * FROM cards WHERE name = ? AND commander_legal = true"
        relation = self.card_index.conn.execute(query, (card_name,))
        result = relation.fetchone()

        if result:
            columns = [col[0] for col in relation.description]
            card = dict(zip(columns, result))
            # Check color identity
            if self._card_matches_color_identity(card, color_identity):
                return card
        return None

    def _card_matches_color_identity(
        self, card: dict[str, Any], deck_color_identity: list[str]
    ) -> bool:
        """Check if a card's color identity is a subset of the deck's color identity."""
        card_ci = set(card.get("color_identity", []))
        deck_ci = set(deck_color_identity)
        return card_ci.issubset(deck_ci)

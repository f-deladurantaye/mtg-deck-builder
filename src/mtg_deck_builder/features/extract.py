"""Feature extraction: pure, deterministic functions.

Features are facts, not opinions.
"""

import re
from typing import Any


def extract_features(card: dict[str, Any]) -> dict[str, bool]:
    """Extract atomic features from a normalised card.

    Args:
        card: Normalised card dictionary

    Returns:
        Dictionary of feature names to boolean values
    """
    oracle_text = card.get("oracle_text", "").lower()
    type_line = card.get("type_line", "").lower()
    produced_mana = card.get("produced_mana", [])

    features = {
        "produces_mana": _produces_mana(card, produced_mana, oracle_text),
        "draws_cards": _draws_cards(oracle_text),
        "removes_creature": _removes_creature(oracle_text, type_line),
        "removes_noncreature": _removes_noncreature(oracle_text, type_line),
        "is_board_wipe": _is_board_wipe(oracle_text, type_line),
        "is_tutor": _is_tutor(oracle_text),
        "creates_tokens": _creates_tokens(oracle_text),
        "is_finisher": _is_finisher(oracle_text, type_line, card),
        "protects_board": _protects_board(oracle_text),
        "recurs_from_graveyard": _recurs_from_graveyard(oracle_text),
        "is_land_only": _is_land_only(type_line),
    }

    return features


def _produces_mana(
    card: dict[str, Any], produced_mana: list[str], oracle_text: str
) -> bool:
    """Check if card produces mana."""
    # If card has produced_mana field, it produces mana
    if produced_mana:
        return True

    # Check oracle text for mana production
    mana_patterns = [
        r"add \{[wubrgc]",
        r"adds? \{[wubrgc]",
        r"tap.*add.*mana",
        r"produces?.*mana",
    ]
    for pattern in mana_patterns:
        if re.search(pattern, oracle_text, re.IGNORECASE):
            return True

    return False


def _draws_cards(oracle_text: str) -> bool:
    """Check if card draws cards."""
    draw_patterns = [
        r"draw.*card",
        r"draws? \d+ card",
    ]
    for pattern in draw_patterns:
        if re.search(pattern, oracle_text, re.IGNORECASE):
            return True
    return False


def _removes_creature(oracle_text: str, type_line: str) -> bool:
    """Check if card removes creatures."""
    # Exclude board wipes (handled separately)
    if _is_board_wipe(oracle_text, type_line):
        return False

    removal_patterns = [
        r"destroy target creature",
        r"exile target creature",
        r"destroy.*creature",
        r"exile.*creature",
        r"deal.*damage.*creature",
    ]
    for pattern in removal_patterns:
        if re.search(pattern, oracle_text, re.IGNORECASE):
            return True
    return False


def _removes_noncreature(oracle_text: str, type_line: str) -> bool:
    """Check if card removes noncreature permanents."""
    removal_patterns = [
        r"destroy target (artifact|enchantment|planeswalker|land)",
        r"exile target (artifact|enchantment|planeswalker|land)",
        r"destroy.*(artifact|enchantment|planeswalker)",
    ]
    for pattern in removal_patterns:
        if re.search(pattern, oracle_text, re.IGNORECASE):
            return True
    return False


def _is_board_wipe(oracle_text: str, type_line: str) -> bool:
    """Check if card is a board wipe."""
    wipe_patterns = [
        r"destroy all (creatures|permanents)",
        r"exile all (creatures|permanents)",
        r"destroy each (creature|permanent)",
        r"all creatures get -x/-x",
        r"deal.*damage to each creature",
    ]
    for pattern in wipe_patterns:
        if re.search(pattern, oracle_text, re.IGNORECASE):
            return True
    return False


def _is_tutor(oracle_text: str) -> bool:
    """Check if card is a tutor (searches library)."""
    tutor_patterns = [
        r"search your library",
        r"search.*library.*card",
    ]
    for pattern in tutor_patterns:
        if re.search(pattern, oracle_text, re.IGNORECASE):
            return True
    return False


def _creates_tokens(oracle_text: str) -> bool:
    """Check if card creates tokens."""
    token_patterns = [
        r"create.*token",
        r"put.*token.*onto the battlefield",
    ]
    for pattern in token_patterns:
        if re.search(pattern, oracle_text, re.IGNORECASE):
            return True
    return False


def _is_finisher(oracle_text: str, type_line: str, card: dict[str, Any]) -> bool:
    """Check if card is a finisher (high damage/power, game-ending effect)."""
    # High power creatures (6+)
    power = card.get("power")
    if power:
        try:
            if int(power) >= 6:
                return True
        except (ValueError, TypeError):
            pass

    # Cards with "you win the game" or similar
    if re.search(r"win the game|you win", oracle_text, re.IGNORECASE):
        return True

    # High damage dealing
    if re.search(r"deal \d{2,} damage", oracle_text, re.IGNORECASE):
        return True

    return False


def _protects_board(oracle_text: str) -> bool:
    """Check if card protects the board (hexproof, indestructible, etc.)."""
    protection_patterns = [
        r"hexproof",
        r"indestructible",
        r"can't be destroyed",
        r"protection from",
    ]
    for pattern in protection_patterns:
        if re.search(pattern, oracle_text, re.IGNORECASE):
            return True
    return False


def _recurs_from_graveyard(oracle_text: str) -> bool:
    """Check if card recurs from graveyard."""
    recursion_patterns = [
        r"return.*from.*graveyard",
        r"return.*from.*yard",
        r"return target.*card.*from.*graveyard",
    ]
    for pattern in recursion_patterns:
        if re.search(pattern, oracle_text, re.IGNORECASE):
            return True
    return False


def _is_land_only(type_line: str) -> bool:
    """Check if card is land only (no other types)."""
    return "land" in type_line.lower() and not any(
        t in type_line.lower()
        for t in ["creature", "artifact", "enchantment", "planeswalker"]
    )

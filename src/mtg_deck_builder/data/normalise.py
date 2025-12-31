"""Card normalisation from Scryfall JSON to engine-facing format."""

from typing import Any


def normalise_card(scryfall_card: dict[str, Any]) -> dict[str, Any]:
    """Convert Scryfall card JSON to normalised format.

    Args:
        scryfall_card: Raw Scryfall card JSON

    Returns:
        Normalised card dictionary with engine-facing fields
    """
    # Extract core fields
    name = scryfall_card.get("name", "")
    mana_cost = scryfall_card.get("mana_cost", "")
    cmc = scryfall_card.get("cmc", 0)
    type_line = scryfall_card.get("type_line", "")
    oracle_text = scryfall_card.get("oracle_text", "")
    colors = scryfall_card.get("colors", [])
    color_identity = scryfall_card.get("color_identity", [])
    rarity = scryfall_card.get("rarity", "")
    scryfall_id = scryfall_card.get("id", "")
    legalities = scryfall_card.get("legalities", {})
    commander_legal = legalities.get("commander", "not_legal") == "legal"

    # Extract power/toughness for creatures
    power = scryfall_card.get("power")
    toughness = scryfall_card.get("toughness")

    # Extract keywords
    keywords = scryfall_card.get("keywords", [])

    # Extract produced mana (from mana_produced field if available, or parse oracle text)
    produced_mana = _extract_produced_mana(scryfall_card)

    return {
        "scryfall_id": scryfall_id,
        "name": name,
        "mana_cost": mana_cost,
        "cmc": cmc,
        "type_line": type_line,
        "oracle_text": oracle_text,
        "colors": colors,
        "color_identity": color_identity,
        "rarity": rarity,
        "commander_legal": commander_legal,
        "power": power,
        "toughness": toughness,
        "keywords": keywords,
        "produced_mana": produced_mana,
        # Store raw JSON for feature extraction
        "raw_json": scryfall_card,
    }


def _extract_produced_mana(card: dict[str, Any]) -> list[str]:
    """Extract mana symbols produced by this card.

    Returns list of mana symbols like ['W', 'U', 'B', 'R', 'G', 'C'].
    """
    # Check if card has produced_mana field (for lands)
    if "produced_mana" in card:
        return card["produced_mana"]

    # For other cards, we'll parse oracle text in feature extraction
    # For now, return empty list
    return []

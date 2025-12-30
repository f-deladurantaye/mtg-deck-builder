"""CLI entry point for MTG Deck Builder."""

import json
from pathlib import Path

from .cache.scryfall_cache import ScryfallCache
from .cache.scryfall_client import ScryfallClient
from .data.card_index import CardIndex
from .data.normalise import normalise_card
from .engine.deck_builder import DeckBuilder
from .engine.deckbrief import DeckBrief
from .features.extract import extract_features
from .roles.role_engine import RoleEngine


def build_index(
    cache_path: Path = Path("scryfall_cache.db"),
    index_path: Path = Path("card_index.duckdb"),
    query: str = "is:commander",
) -> CardIndex:
    """Build the card index from Scryfall data.

    Args:
        cache_path: Path to SQLite cache
        index_path: Path to DuckDB index
        query: Scryfall search query

    Returns:
        Populated CardIndex
    """
    print(f"Building card index from Scryfall (query: {query})...")

    # Initialize components
    cache = ScryfallCache(cache_path)
    client = ScryfallClient(cache)
    index = CardIndex(index_path)

    # Fetch cards
    print("Fetching cards from Scryfall API...")
    cards = client.get_all_cards(query, use_cache=True)
    print(f"Fetched {len(cards)} cards")

    # Normalise and index
    print("Normalising and indexing cards...")
    # role_engine = RoleEngine()

    for i, card_json in enumerate(cards):
        if (i + 1) % 100 == 0:
            print(f"  Processed {i + 1}/{len(cards)} cards...")

        # Normalise card
        card = normalise_card(card_json)

        # Extract features
        features = extract_features(card)

        # Insert into index
        index.insert_card(card)
        index.insert_features(card["scryfall_id"], features)

    index.conn.commit()
    print(f"Index built: {len(cards)} cards indexed")

    return index


def build_deck(
    commander: str,
    color_identity: list[str],
    role_targets: dict[str, int],
    index_path: Path = Path("card_index.duckdb"),
    output_path: Path | None = None,
) -> dict:
    """Build a deck from specifications.

    Args:
        commander: Commander name
        color_identity: List of color symbols
        role_targets: Dictionary of role name to target count
        index_path: Path to DuckDB index
        output_path: Optional path to save deck JSON

    Returns:
        Deck build result dictionary
    """
    print(f"Building deck with commander: {commander}")

    # Initialize components
    index = CardIndex(index_path)
    role_engine = RoleEngine()
    builder = DeckBuilder(index, role_engine)

    # Create DeckBrief
    brief = DeckBrief(
        commander=commander,
        color_identity=color_identity,
        role_targets=role_targets,
    )

    # Build deck
    result = builder.build_deck(brief)

    # Print results
    print(f"\nDeck built: {len(result['deck'])} cards")
    print(f"Commander: {result['commander']['name']}")
    print("\nRole counts:")
    for role, count in result["role_counts"].items():
        print(f"  {role}: {count}")

    print("\nExplanation:")
    for line in result["explanation"]:
        print(f"  {line}")

    # Save if requested
    if output_path:
        with open(output_path, "w") as f:
            json.dump(result, f, indent=2, default=str)
        print(f"\nDeck saved to {output_path}")

    return result


def main() -> None:
    """Main CLI entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="MTG Commander Deck Builder")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # Build index command
    index_parser = subparsers.add_parser("index", help="Build card index")
    index_parser.add_argument(
        "--cache", type=Path, default=Path("scryfall_cache.db"), help="Cache path"
    )
    index_parser.add_argument(
        "--index", type=Path, default=Path("card_index.duckdb"), help="Index path"
    )
    index_parser.add_argument(
        "--query",
        type=str,
        default="is:commander",
        help="Scryfall search query",
    )

    # Build deck command
    deck_parser = subparsers.add_parser("build", help="Build a deck")
    deck_parser.add_argument("commander", help="Commander name")
    deck_parser.add_argument(
        "--colors",
        nargs="+",
        required=True,
        help="Color identity (e.g., W U B)",
    )
    deck_parser.add_argument("--ramp", type=int, default=10, help="Target ramp count")
    deck_parser.add_argument(
        "--draw", type=int, default=10, help="Target card draw count"
    )
    deck_parser.add_argument(
        "--interaction", type=int, default=8, help="Target interaction count"
    )
    deck_parser.add_argument(
        "--finisher", type=int, default=3, help="Target finisher count"
    )
    deck_parser.add_argument(
        "--index", type=Path, default=Path("card_index.duckdb"), help="Index path"
    )
    deck_parser.add_argument("--output", type=Path, help="Output JSON path")

    args = parser.parse_args()

    if args.command == "index":
        build_index(cache_path=args.cache, index_path=args.index, query=args.query)
    elif args.command == "build":
        role_targets = {
            "ramp": args.ramp,
            "card_draw": args.draw,
            "interaction": args.interaction,
            "finisher": args.finisher,
        }
        build_deck(
            commander=args.commander,
            color_identity=args.colors,
            role_targets=role_targets,
            index_path=args.index,
            output_path=args.output,
        )
    else:
        parser.print_help()


if __name__ == "__main__":
    main()

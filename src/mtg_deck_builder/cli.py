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
    query: str = "game:paper is:commander-legal",
) -> CardIndex:
    """Build the card index from Scryfall data.

    Args:
        cache_path: Path to SQLite cache
        index_path: Path to DuckDB index
        query: Scryfall search query

    Returns:
        Populated CardIndex

    Raises:
        SystemExit: If index building fails
    """
    print(f"Building card index from Scryfall (query: {query})...")

    try:
        # Initialize components
        cache = ScryfallCache(cache_path)
        client = ScryfallClient(cache)
        index = CardIndex(index_path)

        # Fetch cards
        print("Fetching cards from Scryfall API...")
        try:
            cards = client.get_all_cards(query, use_cache=True)
        except Exception as e:
            print(f"Error: Failed to fetch cards from Scryfall API: {e}")
            print("This might be a network issue or invalid query. Try again later.")
            raise SystemExit(1)

        if not cards:
            print("Warning: No cards found for query. Index will be empty.")
            return index

        print(f"Fetched {len(cards)} cards")

        # Normalise and index
        print("Normalising and indexing cards...")
        error_count = 0

        for i, card_json in enumerate(cards):
            if (i + 1) % 100 == 0:
                print(f"  Processed {i + 1}/{len(cards)} cards...")

            try:
                # Normalise card
                card = normalise_card(card_json)

                # Skip if missing required fields
                if not card.get("scryfall_id") or not card.get("name"):
                    output_path = Path("output/missing_required_fields.json")
                    if not output_path.exists():
                        output_path.parent.mkdir(parents=True, exist_ok=True)
                        output_path.touch()
                    with open(output_path, "a") as f:
                        json.dump(card_json, f, indent=2)

                    error_count += 1
                    continue

                # Extract features
                features = extract_features(card)

                # Insert into index
                index.insert_card(card)
                index.insert_features(card["scryfall_id"], features)
            except Exception as e:
                error_count += 1
                if error_count <= 5:  # Only print first few errors
                    print(f"  Warning: Error processing card {i + 1}: {e}")

                output_path = Path("output/error_cards.json")
                if not output_path.exists():
                    output_path.parent.mkdir(parents=True, exist_ok=True)
                    output_path.touch()
                with open(output_path, "a") as f:
                    json.dump(card_json, f, indent=2)

        index.conn.commit()
        print(f"Index built: {len(cards) - error_count} cards indexed")
        if error_count > 0:
            print(f"  ({error_count} cards skipped due to errors)")

        return index
    except Exception as e:
        print(f"Error: Failed to build index: {e}")
        raise SystemExit(1)


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

    Raises:
        SystemExit: If deck building fails
    """
    print(f"Building deck with commander: {commander}")

    try:
        # Check if index exists
        if not index_path.exists():
            print(f"Error: Index file not found at {index_path}")
            print("Please run 'index' command first to build the card index.")
            raise SystemExit(1)

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
        try:
            result = builder.build_deck(brief)
        except ValueError as e:
            print(f"Error: {e}")
            raise SystemExit(1)
        except Exception as e:
            print(f"Error: Failed to build deck: {e}")
            raise SystemExit(1)

        # Validate deck size
        deck_size = len(result["deck"])
        if deck_size != 99:
            print(f"Warning: Deck has {deck_size} cards, expected 99")

        # Print results
        print(f"\nDeck built: {deck_size} cards")
        print(f"Commander: {result['commander']['name']}")
        print("\nRole counts:")
        for role, count in result["role_counts"].items():
            print(f"  {role}: {count}")

        print("\nExplanation:")
        for line in result["explanation"]:
            print(f"  {line}")

        # Save if requested
        if output_path:
            try:
                with open(output_path, "w") as f:
                    json.dump(result, f, indent=2, default=str)
                print(f"\nDeck saved to {output_path}")
            except Exception as e:
                print(f"Warning: Failed to save deck to {output_path}: {e}")

        return result
    except SystemExit:
        raise
    except Exception as e:
        print(f"Error: Unexpected error during deck building: {e}")
        raise SystemExit(1)


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
        # default="game:paper is:commander",
        default="game:paper is:commander-legal",
        help="Scryfall search query (default: all commander-legal cards)",
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

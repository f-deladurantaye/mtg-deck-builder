# MTG Commander Deck Builder

A deterministic, explainable Commander deck builder that generates legal 99-card decks based on role-based composition.

## Features

- **Deterministic**: Given the same card index, produces the same deck
- **Explainable**: Shows why each card was added
- **Offline-capable**: Uses local SQLite cache and DuckDB index
- **Role-based**: Cards are assigned to roles based on atomic features

## Installation

```bash
# Install dependencies
uv sync

# Install the package
uv pip install -e .
```

## Usage

### 1. Build the Card Index

First, build the card index from Scryfall data:

```bash
mtg-deck-builder index --query "is:commander"
```

This will:

- Fetch cards from Scryfall API (with caching)
- Normalise and extract features
- Build a DuckDB index

Options:

- `--cache PATH`: Path to SQLite cache (default: `scryfall_cache.db`)
- `--index PATH`: Path to DuckDB index (default: `card_index.duckdb`)
- `--query QUERY`: Scryfall search query (default: `is:commander`)

### 2. Build a Deck

Build a deck with a commander and role targets:

```bash
mtg-deck-builder build "Atraxa, Praetors' Voice" \
    --colors W U B G \
    --ramp 10 \
    --draw 10 \
    --interaction 8 \
    --finisher 3 \
    --output deck.json
```

Options:

- `commander`: Commander card name
- `--colors`: Color identity (space-separated: W U B R G)
- `--ramp`: Target ramp count (default: 10)
- `--draw`: Target card draw count (default: 10)
- `--interaction`: Target interaction count (default: 8)
- `--finisher`: Target finisher count (default: 3)
- `--index PATH`: Path to DuckDB index (default: `card_index.duckdb`)
- `--output PATH`: Optional JSON output path

## Architecture

### Core Components

1. **SQLite Cache** (`cache/`): Caches Scryfall API responses for offline use
2. **Card Normalisation** (`data/normalise.py`): Converts Scryfall JSON to engine format
3. **DuckDB Index** (`data/card_index.py`): Fast queryable card database
4. **Feature Extraction** (`features/`): Extracts atomic features from cards
5. **Role Engine** (`roles/`): Composes roles from features
6. **Deck Builder** (`engine/`): Assembles decks from DeckBrief specifications

### Role System

Roles are compositions of features, not hard-coded labels:

- **ramp**: Requires `produces_mana`, excludes `is_land_only`
- **card_draw**: Requires `draws_cards`
- **interaction**: Requires any of `removes_creature`, `removes_noncreature`, `is_board_wipe`
- **finisher**: Requires `is_finisher`

## Development

```bash
# Run linter
ruff check src/

# Run type checker
ty check src/
```

## Project Status

This is **V1** - "It Works and I Trust It". The focus is on:

- ✅ Legal 99-card Commander decks
- ✅ Deterministic generation
- ✅ Explainable decisions
- ✅ Offline capability

See `docs/plan.md` for the full roadmap.

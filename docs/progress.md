# Implementation Progress

This document tracks the implementation progress of the MTG Commander Deck Builder project.

Last updated: 2024-12-29

## Overview

Following the plan in `plan.md`, we're implementing Phase 1 (Hard Core) components that cannot be skipped.

## Phase 1 — Hard Core (Critical Path)

### ✅ 1. SQLite Cache
**Status**: Complete  
**Files**: 
- `src/mtg_deck_builder/cache/scryfall_cache.py`
- `src/mtg_deck_builder/cache/scryfall_client.py`

**Implementation**:
- SQLite-based cache for Scryfall API responses
- Stores: query, page, response JSON, fetched_at
- Supports read-through caching and offline mode
- ScryfallClient wraps API calls with automatic caching

**Notes**: Basic implementation complete. Ready for testing with real API calls.

---

### ✅ 2. Card Normalisation
**Status**: Complete  
**Files**: 
- `src/mtg_deck_builder/data/normalise.py`

**Implementation**:
- Converts Scryfall JSON to engine-facing format
- Extracts core fields: name, mana_cost, cmc, type_line, oracle_text, colors, color_identity, rarity, commander_legal
- Handles power/toughness, keywords, produced_mana
- Stores raw JSON for feature extraction

**Notes**: Normalisation logic implemented. May need refinement based on actual Scryfall data structure.

---

### ✅ 3. DuckDB Card Index
**Status**: Complete  
**Files**: 
- `src/mtg_deck_builder/data/card_index.py`

**Implementation**:
- DuckDB-based card index for fast queries
- Two tables: `cards` (normalised) and `card_features` (derived features)
- Supports insert/upsert operations
- Query methods for filtering by color identity, legality, etc.

**Notes**: 
- Uses delete-then-insert for upserts (simple approach for v1)
- Array types for colors, keywords, produced_mana
- May need optimization for large datasets

---

### ✅ 4. Feature Extraction
**Status**: Complete  
**Files**: 
- `src/mtg_deck_builder/features/extract.py`

**Implementation**:
- 11 atomic features implemented:
  - `produces_mana`
  - `draws_cards`
  - `removes_creature`
  - `removes_noncreature`
  - `is_board_wipe`
  - `is_tutor`
  - `creates_tokens`
  - `is_finisher`
  - `protects_board`
  - `recurs_from_graveyard`
  - `is_land_only`
- Pure, deterministic functions
- Regex-based pattern matching on oracle text

**Notes**: 
- Feature extraction is basic but functional
- May need refinement based on edge cases
- No scoring logic (as per plan)

---

### ✅ 5. Role Composition
**Status**: Complete  
**Files**: 
- `src/mtg_deck_builder/roles/role_engine.py`

**Implementation**:
- Roles as compositions of features (not hard-coded labels)
- Default roles:
  - `ramp`: requires `produces_mana`, excludes `is_land_only`
  - `card_draw`: requires `draws_cards`
  - `interaction`: requires_any of `removes_creature`, `removes_noncreature`, `is_board_wipe`
  - `finisher`: requires `is_finisher`
- Supports YAML-based role definitions
- Boolean membership (one card can match multiple roles)

**Notes**: 
- Default roles match plan specification
- YAML loading implemented but not tested with external files
- Role matching logic is deterministic

---

### ✅ 6. Simple Deck Assembly
**Status**: Complete  
**Files**: 
- `src/mtg_deck_builder/engine/deck_builder.py`
- `src/mtg_deck_builder/engine/deckbrief.py`

**Implementation**:
- DeckBrief dataclass for minimal inputs
- DeckBuilder class assembles 99-card decks
- Assembly order:
  1. Commander
  2. Lands (~37 minimum)
  3. Role buckets (ramp, draw, interaction, finisher)
  4. Fill to 99
- Explains why each card was added
- Respects color identity and commander legality

**Notes**: 
- Basic assembly logic complete
- No advanced pruning in v1 (as per plan)
- No synergy scoring in v1 (as per plan)
- May need refinement for edge cases (e.g., not enough cards for roles)

---

## Additional Components

### ✅ CLI Interface
**Status**: Complete  
**Files**: 
- `src/mtg_deck_builder/cli.py`

**Implementation**:
- Two commands: `index` and `build`
- `index`: Build card index from Scryfall
- `build`: Build a deck from specifications
- Command-line argument parsing
- JSON output support

**Notes**: Basic CLI functional. May need UX improvements.

---

### ✅ Project Setup
**Status**: Complete  
**Files**: 
- `pyproject.toml`
- `README.md`
- `.gitignore`

**Implementation**:
- Dependencies: duckdb, requests, pyyaml
- CLI entry point configured
- README with usage instructions
- .gitignore for database files

**Notes**: Project structure ready for development and testing.

---

## Testing Status

**Status**: Not Started

**Needed**:
- Unit tests for feature extraction
- Integration tests for deck building
- Test fixtures with real Scryfall card data
- Validation of deck legality

---

## Known Issues / TODOs

1. **Color Identity Filtering**: ✅ **FIXED** - Implemented proper subset checking in Python after SQL queries
2. **Land Selection**: Basic land selection - may need better logic for color identity matching (e.g., prioritize lands that match deck colors)
3. **Feature Extraction**: Regex patterns may miss edge cases - needs testing with real cards
4. **Index Query**: Default query should index all commander-legal cards, not just commanders. Updated to `game:paper is:commander-legal` but needs testing with full dataset.

---

## Recent Fixes (2024-12-30)

1. **Fixed DuckDB Array Syntax**: Changed from `ARRAY<VARCHAR>` to `VARCHAR[]` for DuckDB compatibility
2. **Fixed DuckDB Cursor Description**: Updated all queries to access `.description` from relation objects, not connection
3. **Fixed SQL IN Clause Parameterization**: Properly parameterized all SQL queries with IN clauses
4. **Added Error Handling**: Added comprehensive error handling throughout CLI and deck builder
5. **Tested Index Building**: Successfully tested with Scryfall API (30,859 cards indexed)
6. **Tested Deck Building**: Successfully built 99-card decks with proper color identity filtering
7. **Fixed Color Identity Filtering**: Added Python-based subset checking for all card selection methods
8. **Fixed Filler Card Selection**: Rewrote _get_filler_cards to avoid DuckDB IN clause limitations with many parameters

---

## Next Steps

### Immediate (Before V1 Release)
1. ✅ **Test Full Index Build**: Run index build with `game:paper is:commander-legal` query to get all cards (not just commanders)
2. ✅ **Validate Deck Legality**: Verify built decks are actually legal (99 cards, color identity matches, etc.)
3. **Test Land Selection**: Verify lands are properly selected when full card database is indexed
4. ✅ **Edge Case Testing**: Test with various commanders and color combinations

### Phase 2 (Post-V1)
- Scoring refinement
- Deterministic pruning
- Evaluation harness

### Phase 3 (Future)
- LLM integration
- Rich UI
- Advanced observability

---

## Version History

### 2024-12-30 - Bug Fixes and Testing
- ✅ Fixed DuckDB array syntax (ARRAY<VARCHAR> → VARCHAR[])
- ✅ Fixed DuckDB cursor description access (use relation.description, not conn.description)
- ✅ Fixed SQL IN clause parameterization (proper placeholder handling)
- ✅ Added comprehensive error handling throughout CLI and deck builder
- ✅ Tested index building with Scryfall API (11,186 cards)
- ✅ Tested deck building with real commander (Atraxa)
- ✅ Updated default index query to get all commander-legal cards
- Ready for full integration testing

### 2024-12-29 - Initial Implementation
- ✅ All Phase 1 components implemented
- ✅ CLI interface created
- ✅ Project structure and documentation complete
- Ready for testing phase


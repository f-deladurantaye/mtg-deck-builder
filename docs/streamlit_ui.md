# Streamlit UI Documentation

## Overview

The Streamlit UI provides a web-based interface for testing the MTG Commander Deck Builder. It is designed as a minimal, temporary solution to facilitate testing and will be replaced by a production UI in the future.

## Features

### Index Building

- Checks for the existence of `card_index.duckdb`
- Provides a button to build the card index from Scryfall data if it doesn't exist
- Displays progress during index building

### Deck Building

- **Commander Selection**: Separate section above the form with search and autocomplete
- **Commander Display**: Shows selected commander name and auto-filled color identity
- **Color Identity**: Multi-select dropdown auto-filled from selected commander (can be modified)
- **Role Targets**: Number inputs for setting target counts:
  - Ramp (default: 10)
  - Card Draw (default: 10)
  - Interaction (default: 8)
  - Finisher (default: 3)

### Results Display

- **Deck Summary**: Commander name, deck size, and total cards
- **Role Counts**: Actual counts of cards in each role
- **Explanation**: Step-by-step reasoning for deck construction
- **Deck List**: Optional display of the full 99-card deck with proper card counts (toggle with checkbox)
- **Persistent Results**: Deck results remain visible across interactions

## Autocomplete

The commander selection uses the `streamlit-searchbox` component for integrated autocomplete functionality:

- **Search Box Component**: Single search box with built-in autocomplete dropdown
- **Real-time Suggestions**: Shows commander-legal cards whose names match your input
- **Database Queries**: Queries the DuckDB card index for matching commander names
- **Direct Selection**: Click suggestions to select commanders instantly
- **Auto-fill Colors**: Color identity is automatically populated when a commander is selected
- **Manual Override**: Colors can still be modified after selection
- **Custom Names**: Can still type custom commander names (colors must be set manually)

## Usage

1. **Start the UI**:

   ```bash
   make ui
   ```

2. **Build Index** (if needed):

   - Click "Build Card Index" if the index doesn't exist
   - Wait for the index to build (may take several minutes)

3. **Select Commander**:

   - Type in the search box (minimum 2 characters)
   - Select from the dropdown suggestions
   - Commander name and color identity will be auto-filled

4. **Adjust Parameters** (optional):

   - Modify color identity if needed
   - Adjust role targets as desired

5. **Build a Deck**:
   - Click "Build Deck" in the form below
   - Review results and explanation
   - Use "Show Deck List" checkbox to toggle full deck view
   - Click "Download Deck JSON" to save to `./decks/` directory

## Technical Details

### Dependencies

- Streamlit (added to dev dependencies)
- All core MTG Deck Builder modules

### Architecture

The UI is completely independent from the core logic:

- Imports `build_index` and `build_deck` from `mtg_deck_builder.cli`
- Does not modify any core engine code
- Uses the same validation and error handling as the CLI

### Limitations

- Minimal styling and UX (by design)
- No advanced features like deck editing or multiple deck comparison
- Console output from core functions may not display optimally in the web interface
- Designed for testing, not production use

## Future Plans

This UI will be replaced by a more robust, production-ready interface that includes:

- Better UX/UI design
- Advanced deck editing capabilities
- User accounts and deck saving
- Integration with external MTG resources
- Mobile responsiveness

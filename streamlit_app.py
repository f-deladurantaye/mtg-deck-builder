"""Minimal Streamlit UI for MTG Deck Builder testing."""

import json
import streamlit as st
from pathlib import Path
from streamlit_searchbox import st_searchbox

# Import core modules
from mtg_deck_builder.cli import build_index, build_deck
from mtg_deck_builder.data.card_index import CardIndex


def get_commander_info(commander_name: str) -> dict[str, list[str]] | None:
    """Get commander color identity from the card index."""
    if not commander_name:
        return None

    try:
        index = CardIndex("card_index.duckdb")
        query = (
            "SELECT color_identity FROM cards WHERE name = ? AND commander_legal = true"
        )
        relation = index.conn.execute(query, (commander_name,))
        result = relation.fetchone()
        index.close()

        if result:
            return {"color_identity": result[0] or []}
        return None
    except Exception:
        return None


def get_commander_suggestions(query: str, limit: int = 10) -> list[str]:
    """Get commander name suggestions from the card index."""
    if not query or len(query) < 2:
        return []

    try:
        index = CardIndex("card_index.duckdb")
        # Query for commander-legal cards whose names start with the query
        sql_query = """
        SELECT name FROM cards
        WHERE commander_legal = true
        AND LOWER(name) LIKE LOWER(?)
        ORDER BY name
        LIMIT ?
        """
        relation = index.conn.execute(sql_query, (f"{query}%", limit))
        results = relation.fetchall()
        index.close()
        return [row[0] for row in results]
    except Exception:
        return []


def check_and_build_index() -> bool:
    """Check if index exists and handle building if needed. Returns True if index exists."""
    index_path = Path("card_index.duckdb")
    if not index_path.exists():
        st.warning("Card index not found. Please build the index first.")

        if st.button("Build Card Index"):
            with st.spinner("Building card index... This may take a few minutes."):
                try:
                    build_index()
                    st.success("Card index built successfully!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Failed to build index: {e}")
        return False

    st.success("Card index found.")
    return True


def initialize_session_state():
    """Initialize session state for commander selection."""
    if "selected_commander" not in st.session_state:
        st.session_state.selected_commander = ""
    if "commander_colors" not in st.session_state:
        st.session_state.commander_colors = []
    if "deck_result" not in st.session_state:
        st.session_state.deck_result = None
    if "deck_commander" not in st.session_state:
        st.session_state.deck_commander = ""
    if "commander_query" not in st.session_state:
        st.session_state.commander_query = ""


def render_commander_selection():
    """Render the commander selection UI and return the selected commander."""
    st.header("Select Commander")

    def search_commanders(search_term: str) -> list[str]:
        """Search function for streamlit-searchbox."""
        if not search_term or len(search_term) < 2:
            return []
        return get_commander_suggestions(search_term)

    selected_commander = st_searchbox(
        search_function=search_commanders,
        placeholder="Start typing a commander name...",
        label="Search for Commander",
        key="commander_searchbox",
    )

    # Handle commander selection
    if selected_commander and selected_commander != st.session_state.selected_commander:
        st.session_state.selected_commander = selected_commander
        commander_info = get_commander_info(selected_commander)
        if commander_info:
            st.session_state.commander_colors = commander_info["color_identity"]

    # Display selected commander and colors
    if st.session_state.selected_commander:
        st.success(f"Selected Commander: **{st.session_state.selected_commander}**")
        if st.session_state.commander_colors:
            st.info(
                f"Color Identity: **{' '.join(sorted(st.session_state.commander_colors))}**"
            )
    elif selected_commander and len(selected_commander) >= 2:
        st.info(
            "Using custom commander name (color identity will need to be set manually)"
        )

    return selected_commander or st.session_state.selected_commander


def render_deck_building_form():
    """Render the deck building form and return form data."""
    st.header("Build a Deck")

    with st.form("deck_form"):
        # Use session state values, but allow manual override
        commander = st.text_input(
            "Commander Name",
            value=st.session_state.selected_commander,
            help="Commander name (auto-filled from selection above)",
        )

        colors = st.multiselect(
            "Color Identity",
            ["W", "U", "B", "R", "G"],
            default=st.session_state.commander_colors,
            help="Auto-filled from selected commander, but can be modified",
        )

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            ramp = st.number_input("Ramp", min_value=0, value=10)

        with col2:
            draw = st.number_input("Card Draw", min_value=0, value=10)

        with col3:
            interaction = st.number_input("Interaction", min_value=0, value=8)

        with col4:
            finisher = st.number_input("Finisher", min_value=0, value=3)

        submitted = st.form_submit_button("Build Deck")

    role_targets = {
        "ramp": ramp,
        "card_draw": draw,
        "interaction": interaction,
        "finisher": finisher,
    }

    return submitted, commander, colors, role_targets


def validate_deck_inputs(commander: str, colors: list[str]) -> bool:
    """Validate deck building inputs. Returns True if valid."""
    if not commander:
        st.error("Please enter a commander name.")
        return False

    if not colors:
        st.error("Please select at least one color.")
        return False

    return True


def render_deck_results(result: dict):
    """Render the deck building results."""
    st.success("Deck built successfully!")

    # Display results
    st.subheader("Deck Summary")
    st.write(f"**Commander:** {result['commander']['name']}")
    st.write(f"**Deck Size:** {len(result['deck'])} cards")

    st.subheader("Role Counts")
    for role, count in result["role_counts"].items():
        st.write(f"**{role}:** {count}")

    st.subheader("Explanation")
    for line in result["explanation"]:
        st.write(f"- {line}")

    # Show deck list
    if st.checkbox("Show Deck List"):
        st.subheader("Deck List")
        # Count occurrences of each card
        card_counts = {}
        for card in result["deck"]:
            card_name = card["name"]
            card_counts[card_name] = card_counts.get(card_name, 0) + 1

        # Sort by count descending, then alphabetically
        sorted_cards = sorted(card_counts.items(), key=lambda x: (-x[1], x[0]))

        deck_lines = []
        for card_name, count in sorted_cards:
            deck_lines.append(f"{count}x {card_name}")

        st.code("\n".join(deck_lines))


def handle_deck_download(result: dict, commander: str):
    """Handle deck download functionality."""
    deck_json = json.dumps(result, indent=2, default=str)

    if st.button("Download Deck JSON"):
        # Create decks directory if it doesn't exist
        decks_dir = Path("decks")
        decks_dir.mkdir(exist_ok=True)

        # Save locally
        local_filename = f"{commander.replace(' ', '_')}.json"
        # Replace special characters to make filename safe
        safe_filename = "".join(
            c for c in local_filename if c.isalnum() or c in ("_", "-", ".")
        ).rstrip()
        local_path = decks_dir / safe_filename
        with open(local_path, "w") as f:
            f.write(deck_json)

        st.success(f"Deck saved locally to: `{local_path}`")


def main():
    """Main Streamlit app."""
    st.title("MTG Deck Builder - Testing UI")

    if not check_and_build_index():
        return

    initialize_session_state()

    render_commander_selection()

    submitted, commander, colors, role_targets = render_deck_building_form()

    if submitted:
        if not validate_deck_inputs(commander, colors):
            return

        with st.spinner("Building deck..."):
            try:
                result = build_deck(
                    commander=commander,
                    color_identity=colors,
                    role_targets=role_targets,
                )

                # Store result in session state for persistence
                st.session_state.deck_result = result
                st.session_state.deck_commander = commander

            except Exception as e:
                st.error(f"Failed to build deck: {e}")

    # Show deck results if we have a result (persists across reruns)
    if st.session_state.deck_result:
        render_deck_results(st.session_state.deck_result)

    # Show download button if we have a result (persists across reruns)
    if st.session_state.deck_result and st.session_state.deck_commander:
        handle_deck_download(
            st.session_state.deck_result, st.session_state.deck_commander
        )


if __name__ == "__main__":
    main()

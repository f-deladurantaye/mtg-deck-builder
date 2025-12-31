.PHONY: fmt lint fix type test all ui

RUN := uv run

SRC_DIR := src/
TEST_DIR := tests/
UI_SCRIPT := streamlit_app.py

fmt:
	$(RUN) ruff format $(SRC_DIR) $(TEST_DIR) $(UI_SCRIPT)

lint:
	$(RUN) ruff check $(SRC_DIR) $(TEST_DIR) $(UI_SCRIPT)

fix:
	$(RUN) ruff check --fix $(SRC_DIR) $(TEST_DIR) $(UI_SCRIPT)

type:
	$(RUN) ty check $(SRC_DIR) $(TEST_DIR) $(UI_SCRIPT)

test:
	$(RUN) pytest

ui:
	$(RUN) streamlit run streamlit_app.py

all: fmt lint type test

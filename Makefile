.PHONY: fmt lint fix type test all

RUN := uv run

SRC_DIR := src/
TEST_DIR := tests/

fmt:
	$(RUN) ruff format $(SRC_DIR) $(TEST_DIR)

lint:
	$(RUN) ruff check $(SRC_DIR) $(TEST_DIR)

fix:
	$(RUN) ruff check --fix $(SRC_DIR) $(TEST_DIR)

type:
	$(RUN) ty check $(SRC_DIR) $(TEST_DIR)

test:
	$(RUN) pytest

all: fmt lint type test

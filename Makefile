.PHONY: fmt lint fix type test all

SRC_DIR := src/
TEST_DIR := tests/

fmt:
	uv run ruff format $(SRC_DIR)

lint:
	uv run ruff check $(SRC_DIR)

fix:
	uv run ruff check --fix $(SRC_DIR)

type:
	uv run ty check $(SRC_DIR)

test:
	uv run pytest

all: fmt lint type test

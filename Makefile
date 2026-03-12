VENV := .venv
PYTHON := $(VENV)/bin/python3
UV := uv
SRC := src
PROG := __main__.py

help:
	@echo "Available commands:"
	@echo "  make install     - Install dependencies"
	@echo "  make run         - Run the application"
	@echo "  make test        - Run tests"
	@echo "  make clean       - Clean temporary files"
	@echo "  make debug       - Run the application in debug mode"
	@echo "  make lint        - Run linters and type checkers"
	@echo "  make lint-strict - Run linters and type checkers in strict mode"

install:
	@$(UV) sync

run:
	@$(UV) run $(PYTHON) -m $(SRC)

runm:
	@$(UV) run $(PYTHON) -m $(SRC) \
	--functions_definition data2/input/functions_definition.json \
	--input data2/input/function_calling_tests.json \

debug:
	$(PYTHON) -m pdb $(SRC)/$(PROG)

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete

clean-all: clean
	rm -rf $(VENV)

lint:
	$(UV) run $(PYTHON) -m flake8 src/*.py
	$(UV) run $(PYTHON) -m mypy src/*.py \
	--warn-return-any \
	--warn-unused-ignores \
	--ignore-missing-imports \
	--disallow-untyped-defs \
	--check-untyped-defs \

lint-strict:
	$(UV) run $(PYTHON) -m flake8 src/*.py
	$(UV) run $(PYTHON) -m mypy src/*.py --strict

.PHONY: help install run test clean debug lint lint-strict

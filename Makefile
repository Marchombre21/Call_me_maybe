VENV := .venv
PYTHON := $(VENV)/bin/python3
POETRY := $(VENV)/bin/poetry
PIP := $(VENV)/bin/pip
UV := uv

# help:
# 	@echo "Available commands:"
# 	@echo "  make install     - Install dependencies"
# 	@echo "  make run         - Run the application"
# 	@echo "  make test        - Run tests"
# 	@echo "  make clean       - Clean temporary files"
# 	@echo "  make debug       - Run the application in debug mode"
# 	@echo "  make lint        - Run linters and type checkers"
# 	@echo "  make lint-strict - Run linters and type checkers in strict mode"
# 	@echo "  make keybind     - Show available keybinds while running the program"

install:
	@$(UV) sync

run:
	@$(UV) run python3 -m src\
	--functions_definition data/input/functions_definition.json\
	--input data/input/function_calling_tests.json\
	--output data/output/function_calls.json

debug:
	$(PYTHON) -m pdb src.call_me_maybe

test:
	$(PYTHON) -m pytest -v

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete

clean-all: clean
	rm -rf $(VENV)

lint:
	python3 -m flake8 .
	python3 -m mypy . \
	--warn-return-any \
	--warn-unused-ignores \
	--ignore-missing-imports \
	--disallow-untyped-defs \
	--check-untyped-defs \

lint-strict:
	python3 -m flake8 .
	python3 -m mypy . --strict

.PHONY: help install run test clean debug lint lint-strict

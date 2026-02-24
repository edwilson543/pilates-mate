# Installation.

.PHONY:install
install:
	uv sync --locked
	uv pip install -e .

# Application.
.PHONY:api
api:
	uv run uvicorn pilates.interfaces.api.app:app --port=8000

# Static analysis.

local_ci: lint test

.PHONY:test
test:
	uv run pytest .

lint: check mypy lint_imports

.PHONY:mypy
mypy:
	uv run mypy .

.PHONY:format
format:
	uv run ruff format .
	uv run ruff check . --fix

.PHONY:check
check:
	uv run ruff format . --check
	uv run ruff check .

.PHONY:lint_imports
lint_imports:
	uv run lint-imports

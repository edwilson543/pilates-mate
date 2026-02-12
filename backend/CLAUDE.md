This is the Python and FastAPI backend for the Pilates lesson planning application. 

# Architecture

The backend follows a layered architecture:
- Interfaces
  - Entrypoints into the code, for now just a FastAPI server
- Config
  - Defines the configuration of the application
  - For example the implementations of ABCs defined in the domain to use
- Application
  - Contains functions that orchestrate domain logic
  - Can only be called from the interfaces layer
- Data
  - Implements abstract repositories defined in the domain
  - Connects the application to data persistence technologies (currently just a JSON file)

**Layer Dependencies:**
The `import-linter` enforces strict layering (configured in `pyproject.toml`):
- main → interfaces → config → application → data → domain
- Each layer can only import from layers below it
- Prevents circular dependencies and coupling

# Key patterns

## Async everywhere
All application code is async. Use `async def` and `await` throughout.
- `application/generate_plan.py` is async
- `CompletionClient.get_completion()` is async
- FastAPI routes that use these are async
- Tests use `@pytest.mark.asyncio`

## Dependency injection via config.py
Get implementations from `config.py`, never instantiate directly.
- `config.get_completion_client()` → returns OpenAI client
- `config.get_lesson_planning_repository()` → returns JSON repository
- Used in `interfaces/api/routers.py` and CLI
- Tests override via `pytest.MonkeyPatch`

## Abstract base classes (ABCs)
Define abstractions in domain layer:
- `domain/vendors/_base.py` → `CompletionClient` ABC with `OutputT` TypeVar
- `domain/lesson_planning/_repository.py` → `Repository` ABC

## Private module naming
Implementation modules prefixed with underscore:
- `_models.py`, `_repository.py`, `_render.py`
- Public API exported via `__init__.py`
- Signals internal implementation vs. public interface

# Testing
After each commit, all tests should pass.
Run the tests using `make test`.

## Test factories
Use factories for generating test data:
- Factories in `testing/helpers/` → `ExerciseFactory`, `LessonPlanFactory`
- Only specify fields relevant to the test

# Test fakes
Use fakes for stubbing concrete ABC implementations.
- Fakes are implemented in `testing/fakes/` → `FakeRepository`, `FakeCompletionClient`
- In unit tests, fakes can be instantiated and injected into the code directly.
- In functional tests, fakes are better installed via a context manager: `with install_fake_completion_client(): ...`

See `tests/unit/application/test_generate_plan.py:15` for factory usage.
See `tests/functional/api/test_routers.py:12` for repository patching via context manager.

Tests are split into the following categories:
- Unit tests
  - For small pieces of functionality
  - Test should be grouped in to test classes, named after the function under test
  - Each test method name should finish a sentence started by the test classes' name
  - Each test method should have three sections:
    - Setup
    - Execution
    - Assertions
  - Use blank lines to separate the sections, not comments
- Functional tests: for testing interfaces into the code, such as FastAPI endpoints
  - These should use the `api_client` to make requests to the test FastAPI app
  - These tests are not allowed to interact with application or domain code

Test style:
- To facilitate test setup, prefer using factories defined in `testing/helpers/*`, 
rather than directly instantiating domain models. When instantiating factories, you
should only specify the fields that are relevant to the test. 

# Linting
After each commit, all linting checks should pass.
Run the tests using `make lint`.


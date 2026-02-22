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


# Testing
After each commit, all tests should pass.
Run the tests using `make test`.

## Test categorisation
Tests are split into the following categories:
- Unit tests (`tests/unit/`)
  - Purpose: for testing small pieces of functionality in isolation
  - Unit tests should be grouped in to test classes, with the test class named after the function under test
    - For example the test class for `def do_something` should be called `TestDoSomething`
  - Each unit test should test one specific scenario only
  - Each test method name should finish a sentence started by the test classes' name
    - For example the test for the scenario "do_something" errors when invalid inputs are given
    - Should be called `def test_errors_when_invalid_inputs_are_given`
  - Each unit test method should be split into three sections:
    - Setup
    - Execution
    - Assertions
  - Use blank lines to separate the sections of the test, not comments
- Functional tests (`tests/functional/`)
  - Purpose: for testing interfaces into the code, such as FastAPI endpoints
  - Functional tests should use the `api_client` fixture to make requests to the test FastAPI app
  - Functional tests should use the `repository` fixture to set up and inspect state, rather than
    interacting with application or domain code directly
  - Functional tests should also be split into (setup / execution / assertion) blocks, however each
    functional test can have multiple series of blocks
  - Functional tests should be implemented as ordinary functions

## Test factories
Use test factories to generate fake data during test setup.
- Test factories are implemented in `testing/helpers/` → `ExerciseFactory`, `LessonPlanFactory`
- Test factories are used to create domain models, specifying realistic default values for every field,
  and creating any downstream objects via subfactories
- Factories should be instantiated during the "setup" section of tests
- When instantiating a factory, only explicitly specify the fields that are relevant to the test
  - For example, a test for a query that filters exercises on `category` should only specify the
    `category` of the exercises factoried during the test setup
- Factories can be used in two main ways:
  - To instantiate domain objects that are then passed directly to application code (unit tests)
  - To create and persist domain objects into a `Repository` using the `create_in_repo` class method,
    which accepts the repository as its first argument, followed by any fields to override
    - For example: `Exercise.create_in_repo(repository, difficulty="ADVANCED")`
    - This is the expected pattern for setting up state in functional tests

## Test fakes
Use fake implementations to avoid interacting with external services.
- Test fakes are implemented in `/testing/<domain>/`
  - `/testing/vendors/` provides a `FakeCompletionClient`, acting as a fake LLM vendor providing canned completions
- Fake implementations should be used differently, depending on the test category:
  - In unit tests, fakes should be instantiated and injected into the code directly
  - In functional tests, fakes should be instantiated directly, but since we don't call the code under
    test directly, must be installed via their `install` method which is a context manager
    - `with fake_completion_client.install(): ...`
  - The `repository` fixture used in functional tests is backed by the real repository implementation,
    so no fake repository is needed or should be used in functional tests


# Linting
After each commit, all linting checks should pass.
Run the tests using `make lint`.


# Other patterns

## Async everywhere
All application code is async. Use `async def` and `await` throughout.
- `application/generate_plan.py` is async
- `CompletionClient.get_completion()` is async
- FastAPI routes that use these are async
- Tests use `@pytest.mark.asyncio`

## Abstract base classes (ABCs)
Define abstractions in domain layer:
- `domain/vendors/_base.py` → `CompletionClient` ABC with `OutputT` TypeVar
- `domain/lesson_planning/_repository.py` → `Repository` ABC

## Dependency injection via config.py
Get implementations from `config.py`, never instantiate directly.
- `config.get_completion_client()` → returns OpenAI client
- `config.get_lesson_planning_repository()` → returns JSON repository
- Used in `interfaces/api/routers.py` and CLI
- Tests override via `pytest.MonkeyPatch`

## Repository pattern to encapsulate persistence logic
All application and domain code can only interact with the database via a `Repository`
- Each method on the repository defines a database query or operation
- The repository is defined as an ABC in the `domain/` layer, and implemented in the `fake/` layer
- The repository is injected from the interfaces layer into application code

## Private module naming
Implementation modules prefixed with underscore:
- `_models.py`, `_repository.py`, `_render.py`
- Public API exported via `__init__.py`
- Signals internal implementation vs. public interface

This directory contains the backend for the Pilates lesson planning application.
The backend is implemented in Python, and served via a FastAPI application.

# Project structure
The project is split into three main packages:
- Source code for the application, implemented in `./src/pilates/`
- Tests for the source code, implemented in `./tests/`
- Testing helpers, implemented in `./testing/`

`import-linter` is used to prevent:
- The source code importing from the testing helpers or from tests
- The testing helpers importing from tests

## Architecture of the source code
The backend follows a strict layered architecture.
- The layering is: interfaces → config → application | data → domain
- Each layer has a separate responsibility, and can only import from the layers beneath it
- The layering is enforced by `import-linter` (which is configured in `pyproject.toml`)
- The objectives of the layered architecture are to:
  - Clearly define and decouple responsibilities
  - Decouple domain concepts and integrations with external services from their implementations 
  - Prevent circular dependencies 

### Interfaces layer
The interfaces layer contains the entrypoints into the code.
- The interfaces layer is implemented at `./src/pilates/interfaces/`
- For now, the only interface is a FastAPI application, implemented at `./interfaces/api/` 
- Dependencies in the interfaces layer must be instantiated by calling into the config layer
- The interfaces layer must never instantiate dependencies directly from the domain or data layers

### Config layer
The config layer is responsible for instantiating the correct implementations of ABCs declared in the domain.
- The config layer is implemented at `./src/pilates/config.py` 
- Each public function in `config.py` takes the form `get_xyz()`, and returns the instantiated concrete implementation
  of an abstract base class declared in the domain.
- Instantiations retrieved from the config can be used in two ways:
  - Injected into use cases defined in the application layer. For example, the `generate_lesson_plan` use case 
    requires a `CompletionClient` implementation so that it can call a third-party vendor
  - Methods can just be called directly. For example, the `get_lesson_plans` API router just calls the 
    `get_lesson_plans` method on the lesson planning repository to make a database query.
- For example, the config layer determines which implementation of the lesson planning repository to use, giving 

### Application layer
The application layer is responsible for orchestrating domain logic.
- The application layer is implemented at `./src/pilages/application/`
- The application consists of modules name 
- Implementations of ABCs defined in the domain be injected into use cases by the interfaces layer
- The application layer must never instantiate abstract dependencies directly from the domain or data layers

### Data layer
- Implements abstract repositories defined in the domain
- Connects the application to data persistence technologies (currently just a JSON file)

### Domain layer
-

### Repository pattern to encapsulate persistence logic
All application and domain code can only interact with the database via a `Repository`
- Each method on the repository defines a database query or operation
- The repository is defined as an ABC in the `domain/` layer, and implemented in the `fake/` layer
- The repository is injected from the interfaces layer into application code


### Abstract base classes (ABCs)
Define abstractions in domain layer:
- `domain/vendors/_base.py` → `CompletionClient` ABC with `OutputT` TypeVar
- `domain/lesson_planning/_repository.py` → `Repository` ABC

### Other notes on the source code

### Async everywhere
All application code is async. Use `async def` and `await` throughout.
- `application/generate_plan.py` is async
- `CompletionClient.get_completion()` is async
- FastAPI routes that use these are async
- Tests use `@pytest.mark.asyncio`

#### Private module naming
Implementation modules prefixed with underscore:
- `_models.py`, `_repository.py`, `_render.py`
- Public API exported via `__init__.py`
- Signals internal implementation vs. public interface


## Tests
After each commit, all tests should pass.
Run the tests using `make test`.

### Test categorisation
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

### Test factories
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

### Test fakes
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
- Ensure code is formatted correctly by running `make format`
- Run the linting checks by running `make lint`

The following checks are installed:
- `make check`: Ensures code is formatted correctly and all `ruff` rules are satisfied
- `make mypy`: Ensures code is typed correctly, using `mypy`
- `make lint_imports`: Ensures all imports obey the project dependency graph, using `import-linter`

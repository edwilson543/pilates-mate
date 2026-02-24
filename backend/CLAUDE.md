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
- The application consists of "use cases" which orchestrate domain logic into a particular business use case
- For example `generate_lesson_plan.py` contains a function `generate_lesson_plan`, which orchestrates 
  pilates lesson plan modelling, persistence logic and LLM completion logic to generate a lesson plan
- Dependency injection
  - Implementations of ABCs defined in the domain be injected into use cases as keyword arguments
  - The application layer must never instantiate abstract dependencies directly from the domain or data layers

### Data layer
The data layer is responsible for persistence logic.
- The data layer is implemented at `./src/pilates/data/`
- The data layer has two core responsibilities:
  - Implementations of the abstract repositories defined in the domain layer
  - Connection logic to local persistence technologies (for now, this is just a JSON file)

### Domain layer
The domain layer is responsible for modelling business logic.
- The domain layer is implemented at `./src/pilates/domain/`
- Each domain is implemented as a subdirectory within `./domain`, for examples `./domain/lesson_planning/`
- Each domain is responsible for:
  - Modelling the concepts of that domain as objects
    - Models are typically implemented using some combination of enums and Pydantic base models
    - For example, the `lesson_planning` domain includes models like `Exercise` and `LessonPlan`
  - Defining the interface into that domain for the application layer
    - This interface is defined as a Python API represented by an abstract base class (ABC)
    - For example, the `lesson_planning` domain includes a `Repository` interface, for retrieving lesson plans
      from the relevant database (but abstracting the implementation details)
    - For example, the `vendors` domain includes a `CompletionClient` interface, for requesting vendor APIs
    - Implementations of the ABC can be implemented either directly in the domain, or in the `data/` layer
      in the case of repositories. Implementations must always be instantiated from the config layer.

### Other notes on the source code

#### Async everywhere
All application code is async. Use `async def` and `await` throughout.
- `application/generate_plan.py` is async
- `CompletionClient.get_completion()` is async
- FastAPI routes that use these are async
- Tests use `@pytest.mark.asyncio`

#### Private module naming
Modules prefixed with a private underscore cannot be imported, except:
- By the packages `__init__.py` module (to expose objects publicly)
- By neighbouring packages (to make use of the module's contents)
- By the test module for that module
 
Other notes:
- Default to the minimum level of public visibility
- Always import modules, not objects
- Use the same private underscore naming convention for functions and classes

## Testing helpers
Testing helpers are implemented at `./testing/helpers`
- There are two main types of helpers:
  - Factories, for creating domain objects without having to populate every field
  - Fake implementations of ABCs defined in the domain
- The helpers are organised by the domain they help test (but are not restricted to use for tests of domain code)
  - For example, `./helpers/vendors` contains a `FakeCompletiongClient` for testing use cases that call an LLM,
    without actually making a request to a vendor API
  - For example, `./helpers/lesson_planning` contains factories for creating Pilates lesson plans, without every
    test having to write-out the creation boilerplate
The "Tests" section provides more detail on how and when to use helpers.

## Tests
After each commit, all tests should pass.
Run the tests using `make test`.

### Test categorisation
Tests are split into the following categories:
- Unit tests, for testing small pieces of functionality in isolation (`tests/unit/`)
- Functional tests, for testing interfaces into the code, such as FastAPI endpoints (`tests/functional/`)

### Unit tests
- Unit tests must live in a module in `tests/unit` mirroring the application module
  - For example, tests for: `./src/pilates/application/generate_lesson_plan.py`
  - Must be implemented in: `./tests/unit/application/test_generate_lesson_plan.py`
- Group tests for each function/method into test classes, named after the function under test
  - For example the test class for `def do_something` should be called `TestDoSomething`
- Each test should be implemented as a method on the test class, and cover one specific scenario only
  - Test method names should finish a sentence started by the test classes' name
    - For example the test for the scenario "do_something" errors when invalid inputs are given
    - The method should be called be called `def test_errors_when_invalid_inputs_are_given`
- Unit tests should be split into three sections:
  - Setup: instantiation of any objects (perhaps using factories), to pass as kwargs to the code under test
  - Execution: call the function/method we are testing
  - Assertions: make final assertions on the return value / exception raised by the application code
- Use blank lines to separate the sections of the test, not comments. Somtimes, it's also useful to
  add blank lines between sections of the setup / assertions. It depends on the length of the test -
  the main objective is that the test is easy to read

### Functional tests
- Functional tests must live in a module named after the API router being tested
  - For example, tests for the `create_lesson_plan` API route live in `test_create_lesson_plan`
- Functional tests should be implemented as functions (note, not test classes)
  - Each test function name should finish a sentence started by the module name
  - For example, `test_creates_then_gets_lesson_plan`
- Functional tests should invoke one (or more, if necessary) API router
  - Using the `api_client` fixture to make HTTP requests
  - Using the `repository` fixture plus testing helper factories to set up and inspect state, rather than
    interacting with application or domain code directly
- Functional tests should not cover every scenario, typically one test for each status code, for example:
  - One test for the happy path (e.g. object created successfully, 201)
  - One test for an application error (e.g. invalid creationg parameters, 400)
- Functional tests should also be split into (setup / execution / assertion) blocks, however each
  functional test can have multiple series of such blocks

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

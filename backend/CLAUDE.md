# Backend
This is the Python and FastAPI backend for the Pilates lesson planning application. 

## Architecture
- The backend follows a layered architecture:
  - Interfaces
    - Entrypoints into the code, for now just a FastAPI server
  - Config
    - Defines the configuration of the application
    - For example the implementations of ABCs defined in the doma to use
  - Application
    - Contains functions that orchestrate domain logic
    - Can only be called from the interfaces layer
  - Data
    - Implements abstract repositories defined in the domain
    - Connects the application to data persistence technologies (currently just a JSON file)

## Testing
After each commit, all tests should pass.
Run the tests using `make test`.

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

## Linting
After each commit, all linting checks should pass.
Run the tests using `make lint`.

## Git
This project uses atomic commits.

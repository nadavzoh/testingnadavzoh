# Lotus Unit Tests

This directory contains unit tests for the Lotus application core components.

## Running Tests

There are multiple ways to run the tests:

### 1. Using the run_unit_tests.py script:

```bash
python tests/run_unit_tests.py
# or
./tests/run_unit_tests.py
```

### 2. Using pytest:

```bash
pytest
# or for more verbose output
pytest -v
# or to run a specific test file
pytest tests/unit/test_document_model.py
```

### 3. Using unittest directly:

```bash
python -m unittest discover tests/unit
# or to run a specific test file
python -m unittest tests/unit/test_document_model.py
```

## Test Structure

- `test_document_model.py`: Tests for the DocumentModel class
- `test_line_models.py`: Tests for the LineModelInterface implementations
- `test_line_model_factories.py`: Tests for the factory classes
- `test_file_manager.py`: Tests for the FileManager class

## Writing New Tests

When adding new functionality, please add corresponding tests. 
Tests should follow these guidelines:

1. Test files should be named `test_*.py`
2. Test classes should be named `Test*`
3. Test methods should be named `test_*`
4. Each test method should test a single behavior
5. Use descriptive method names that indicate what is being tested
6. Tests should be independent and not rely on other tests
7. Tests should clean up after themselves (use setUp/tearDown)

## Code Coverage

Code coverage reports can be generated using pytest-cov:

```bash
# Generate console coverage report
pytest --cov=src.core.models tests/unit

# Generate HTML coverage report
pytest --cov=src.core.models --cov-report=html:tests/coverage_html tests/unit
```

The HTML report will be generated in the `tests/coverage_html/` directory. You can open the `index.html` file in a web browser to view a detailed, interactive coverage report that shows exactly which lines of code are covered by tests and which are not.

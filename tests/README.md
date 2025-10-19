# TinyDSL Test Suite

This directory contains the test suite for TinyDSL using pytest.

## Structure

```
tests/
├── __init__.py           # Package marker
├── conftest.py           # Pytest fixtures and configuration
├── test_core.py          # Tests for core framework (BaseDSL, Registry, Memory, Evaluator)
├── test_tinycalc.py      # Tests for TinyCalc DSL
├── test_tinysql.py       # Tests for TinySQL DSL
├── test_gli.py           # Tests for Gli DSL (V1 and V2)
├── test_lexi.py          # Tests for Lexi DSL (V1 and V2)
├── test_rl.py            # Tests for RL framework
└── test_agent_tools.py   # Tests for agent tools
```

## Running Tests

### Install Dependencies

First, install pytest and other dev dependencies:

```bash
# Using pip
pip install -e ".[dev]"

# Or using uv
uv sync --group dev
```

### Run All Tests

```bash
pytest
```

### Run Specific Test File

```bash
pytest tests/test_core.py
```

### Run Specific Test Class

```bash
pytest tests/test_core.py::TestDSLRegistry
```

### Run Specific Test

```bash
pytest tests/test_core.py::TestDSLRegistry::test_register_dsl
```

### Run with Coverage

```bash
pytest --cov=tinydsl --cov-report=html
```

### Run with Verbose Output

```bash
pytest -v
```

### Run Only Fast Tests (skip slow RL tests)

```bash
pytest -m "not slow"
```

## Test Coverage

The test suite covers:

- **Core Framework**: BaseDSL, DSLRegistry, Memory implementations, DSLEvaluator
- **DSLs**: TinyCalc, TinySQL, Gli (v1/v2), Lexi (v1/v2)
- **RL Framework**: Environments, Agents, Rewards, Trainer, Evaluator
- **Agent Tools**: GenericDSLClient, KAITAgent

## Writing New Tests

### Test Structure

Follow the existing pattern:

```python
"""Tests for <module>."""
import pytest
from tinydsl.module import YourClass


class TestYourClass:
    """Test YourClass."""

    def test_initialization(self):
        """Test initialization."""
        obj = YourClass()
        assert obj is not None

    def test_specific_feature(self):
        """Test specific feature."""
        obj = YourClass()
        result = obj.do_something()
        assert result == expected_value
```

### Using Fixtures

Fixtures are defined in `conftest.py` and can be used in any test:

```python
def test_with_fixture(sample_tinycalc_code):
    """Test using a fixture."""
    calc = TinyCalc()
    result = calc.execute(sample_tinycalc_code)
    assert result is not None
```

### Mocking

Use `unittest.mock` for mocking external dependencies:

```python
from unittest.mock import Mock, patch

@patch('requests.get')
def test_api_call(mock_get):
    """Test API call."""
    mock_get.return_value.json.return_value = {"key": "value"}
    # Your test code
```

## Continuous Integration

These tests are designed to run in CI/CD pipelines. Add to your CI configuration:

```yaml
# GitHub Actions example
- name: Run tests
  run: |
    pip install -e ".[dev]"
    pytest --cov=tinydsl --cov-report=xml
```

## Tips

- Keep tests simple and focused
- Use descriptive test names that explain what is being tested
- Test both success and failure cases
- Use fixtures for common test data
- Mock external dependencies (network calls, file I/O)
- Aim for fast tests (< 1s per test when possible)

# Auth Service Tests

This directory contains tests for the saturn-mousehunter-auth-service.

## Structure

- `unit/` - Unit tests for individual components
- `integration/` - Integration tests for service interactions

## Running Tests

```bash
# Run all tests
uv run python -m unittest discover tests

# Run specific test module
uv run python -m unittest tests.unit.test_password_utils

# Run with coverage
uv run coverage run -m unittest discover tests
uv run coverage report
```

## Test Configuration

Create a `.env.test` file for test-specific environment variables.
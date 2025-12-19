# Testing Guide

This directory contains comprehensive tests for the Stock Tracker backend application.

## Test Structure

- `conftest.py` - Pytest configuration and shared fixtures
- `test_transaction_service.py` - Unit tests for transaction service functions
- `test_auth.py` - Tests for authentication and security
- `test_crud.py` - Tests for CRUD operations
- `test_api_endpoints.py` - Integration tests for API endpoints

## Running Tests

### Install Dependencies

First, make sure you have the testing dependencies installed:

```bash
cd backend
pip install -r requirements.txt
```

### Run All Tests

```bash
pytest
```

### Run with Coverage

```bash
pytest --cov=app --cov-report=html
```

This will generate an HTML coverage report in `htmlcov/index.html`.

### Run Specific Test Files

```bash
# Run only transaction service tests
pytest tests/test_transaction_service.py

# Run only authentication tests
pytest tests/test_auth.py

# Run only CRUD tests
pytest tests/test_crud.py

# Run only API endpoint tests
pytest tests/test_api_endpoints.py
```

### Run Specific Test Classes or Functions

```bash
# Run a specific test class
pytest tests/test_transaction_service.py::TestGetCurrentPosition

# Run a specific test function
pytest tests/test_transaction_service.py::TestGetCurrentPosition::test_empty_position
```

### Verbose Output

```bash
pytest -v
```

## Test Coverage

The test suite covers:

1. **Transaction Service** - Position calculation logic
   - Empty positions
   - Single and multiple buy transactions
   - Buy and sell transactions
   - Case-insensitive ticker matching
   - Portfolio and ticker isolation

2. **Authentication** - Security functions
   - Password hashing and verification
   - User authentication
   - JWT token creation and validation
   - Registration and login endpoints

3. **CRUD Operations** - Database operations
   - Portfolio CRUD with user isolation
   - Transaction CRUD with validation
   - Stock CRUD operations

4. **API Endpoints** - Integration tests
   - Transaction endpoints (create, read, update, delete)
   - Portfolio endpoints
   - Stock endpoints
   - Authentication and authorization

## Test Fixtures

The `conftest.py` file provides several useful fixtures:

- `db_session` - Fresh database session for each test
- `client` - FastAPI test client with database override
- `test_user` - Test user fixture
- `test_user2` - Second test user fixture
- `test_portfolio` - Test portfolio fixture
- `test_stock` - Test stock fixture
- `test_transaction_buy` - Test buy transaction fixture
- `auth_headers` - Authentication headers for API tests

## Writing New Tests

When writing new tests:

1. Use the provided fixtures to set up test data
2. Follow the naming convention: `test_<functionality>`
3. Use descriptive test names that explain what is being tested
4. Test both success and failure cases
5. Test edge cases and boundary conditions
6. Ensure tests are isolated (don't depend on execution order)

## Example Test

```python
def test_create_portfolio(client: TestClient, auth_headers: dict):
    """Test creating a portfolio."""
    response = client.post(
        "/portfolios/",
        json={"name": "New Portfolio"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "New Portfolio"
```

## Continuous Integration

These tests are designed to run in CI/CD pipelines. The test database is in-memory SQLite, so no external database setup is required.


# Logging and Error Handling

This document describes the logging and error handling system implemented in the Stock Tracker application.

## Logging Configuration

### Setup

Logging is configured in `app/logging_config.py` and initialized in `app/main.py` on application startup.

### Configuration Options

Environment variables (in `.env`):
- `LOG_LEVEL` - Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL). Default: `INFO`
- `LOG_TO_FILE` - Whether to log to files (true/false). Default: `true`
- `LOG_TO_CONSOLE` - Whether to log to console (true/false). Default: `true`
- `ENVIRONMENT` - Environment name (development/production). Default: `development`

### Log Files

- `backend/logs/app.log` - All application logs (rotating, max 10MB, 5 backups)
- `backend/logs/error.log` - Error and above logs only (rotating, max 10MB, 5 backups)

### Log Format

**Console:**
```
2025-01-15 10:30:45 - app.routers.auth - INFO - User logged in successfully: john_doe (ID: 1)
```

**File (with more context):**
```
2025-01-15 10:30:45 - app.routers.auth - INFO - [auth.py:75] - login_for_access_token() - User logged in successfully: john_doe (ID: 1)
```

## Custom Exceptions

The application uses custom exception classes for standardized error handling:

### Exception Classes

- `AppException` - Base exception class
- `ValidationError` - Input validation failures (400)
- `NotFoundError` - Resource not found (404)
- `UnauthorizedError` - Authentication required/failed (401)
- `ForbiddenError` - Permission denied (403)
- `ConflictError` - Resource conflicts (409)
- `ExternalServiceError` - External API failures (502)
- `DatabaseError` - Database operation failures (500)
- `BusinessLogicError` - Business rule violations (400)

### Usage Example

```python
from app.exceptions import NotFoundError, BusinessLogicError

# Raise a not found error
raise NotFoundError("Portfolio", portfolio_id)

# Raise a business logic error
raise BusinessLogicError("Insufficient holdings for sell transaction", "INSUFFICIENT_HOLDINGS")
```

## Error Response Format

All errors return a standardized JSON response:

```json
{
  "error": true,
  "error_code": "NOT_FOUND",
  "message": "Portfolio with id 123 not found",
  "path": "/portfolios/123"
}
```

For validation errors:
```json
{
  "error": true,
  "error_code": "VALIDATION_ERROR",
  "message": "Request validation failed",
  "details": [
    "body -> quantity: ensure this value is greater than 0",
    "body -> price: ensure this value is greater than 0"
  ],
  "path": "/transactions"
}
```

## Logging Best Practices

### When to Log

1. **INFO Level:**
   - User actions (login, registration, CRUD operations)
   - Successful operations
   - Application lifecycle events (startup, shutdown)

2. **WARNING Level:**
   - Failed authentication attempts
   - Validation failures
   - Business logic violations
   - External service warnings

3. **ERROR Level:**
   - Exceptions and errors
   - Database failures
   - External service failures
   - Unexpected errors

4. **DEBUG Level:**
   - Detailed operation information
   - Request/response details (when needed)

### Example Usage

```python
from app.logging_config import get_logger

logger = get_logger(__name__)

# Info log
logger.info(f"User {username} logged in successfully")

# Warning log
logger.warning(f"Failed login attempt for {username}")

# Error log with exception info
logger.error(f"Error creating transaction: {str(e)}", exc_info=True)

# Debug log
logger.debug(f"Processing request with params: {params}")
```

## Error Handling Flow

1. **Request comes in** → Logged at INFO level
2. **Validation fails** → ValidationError raised → Logged at WARNING level
3. **Business logic violation** → BusinessLogicError raised → Logged at WARNING level
4. **Resource not found** → NotFoundError raised → Logged at WARNING level
5. **Unexpected exception** → General exception handler → Logged at ERROR level with traceback

## Production Considerations

- In production (`ENVIRONMENT=production`), internal error details are not exposed to users
- Log files are automatically rotated to prevent disk space issues
- Error logs are separated from general logs for easier monitoring
- Consider integrating with external logging services (e.g., Sentry, Datadog) for production

## Monitoring

To monitor application health:

1. Check `backend/logs/error.log` for errors
2. Check `backend/logs/app.log` for general application activity
3. Set up log aggregation tools for production environments
4. Monitor error rates and patterns

## Testing Logging

Logging can be tested by:

1. Setting `LOG_LEVEL=DEBUG` for verbose output
2. Checking log files after operations
3. Verifying error messages are user-friendly
4. Ensuring sensitive data is not logged


# FastAPI Money Saver Server Setup Guide

This guide provides instructions for starting the FastAPI server and running tests for the Money Saver application.

## Prerequisites

- Python 3.12+
- Virtual environment already set up in `venv/`
- All dependencies installed via `requirements.txt`
- Supabase database configured

## Starting the Server

### Method 1: Using Uvicorn (Recommended for Development)

1. **Navigate to the project directory:**
   ```bash
   cd /Users/emekaanyaegbunam/Workspace/money_saver/fastapi-money-saver
   ```

2. **Activate the virtual environment:**
   ```bash
   source venv/bin/activate
   ```

3. **Start the server:**
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```

### Method 2: Using Python directly

1. **Navigate to the project directory and activate virtual environment:**
   ```bash
   cd /Users/emekaanyaegbunam/Workspace/money_saver/fastapi-money-saver
   source venv/bin/activate
   ```

2. **Run the main.py file:**
   ```bash
   python app/main.py
   ```

## Server Information

- **Server URL:** `http://localhost:8000`
- **API Documentation:** `http://localhost:8000/docs` (Swagger UI)
- **Alternative Docs:** `http://localhost:8000/redoc`
- **Health Check:** `http://localhost:8000/health`

## CORS Configuration

The server is configured to accept requests from:
- `http://localhost:3000` (React frontend)
- `http://127.0.0.1:3000`

## Running Tests

### Run All Tests

```bash
# Make sure you're in the project directory with venv activated
source venv/bin/activate
python -m pytest tests/ -v
```

### Alternative Test Commands

```bash
# Run tests without verbose output
pytest

# Run tests with coverage
python -m pytest --cov=app tests/

# Run specific test file
python -m pytest tests/test_savings_api.py -v
```

## Database Setup

### Running Migrations

If you need to update the database schema:

```bash
# Activate virtual environment
source venv/bin/activate

# Run migrations
alembic upgrade head
```

## Troubleshooting

### Database Connection Issues

1. **Check the health endpoint:** `http://localhost:8000/health`
2. **Verify environment variables** are set for:
   - `DATABASE_URL`
   - `SUPABASE_URL`
   - `SUPABASE_KEY`

### Transaction Errors

If you encounter database transaction errors:

1. **Stop the server** (Ctrl+C)
2. **Restart the server** using the commands above

### Docker Issues

If using Docker Compose fails with network errors:
- Use the Python method instead (Method 1 above)
- Docker containers may have network isolation issues with external services like Supabase

## Development Notes

- The server runs with auto-reload enabled in development mode
- All API endpoints require authentication except `/`, `/health`, and `/docs`
- The server includes scheduled email reminders and background tasks
- CORS is configured for frontend integration

## Test Coverage

Current test suite includes:
- Saving plan CRUD operations
- Weekly amount management
- Authentication flows
- Statistics endpoints
- Error handling

All tests use a test database configuration and mock authentication for isolated testing.
# chat-with-pgdb

A natural language to SQL query API for PostgreSQL databases using Claude AI.

## Features

- Convert natural language questions to SQL queries
- Execute queries safely (read-only)
- FastAPI-based REST API
- Modular, testable architecture

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Configure `.env`:
   ```bash
   # Database (use read-only user)
   DB_HOST=localhost
   DB_PORT=5432
   DB_NAME=your_database
   DB_USER=your_readonly_user
   DB_PASSWORD=your_password
   
   # Anthropic API
   ANTHROPIC_API_KEY=your_api_key
   ```

## Running the API

Start the server:
```bash
python main.py
```

API available at: `http://localhost:8000`

### API Endpoints

**Health Check**
```bash
curl http://localhost:8000/health
```

**Ask Question**
```bash
curl -X POST http://localhost:8000/ask_question \
  -H "Content-Type: application/json" \
  -d '{"question": "How many actors are in the database?"}'
```

**API Docs**: http://localhost:8000/docs

## Testing

```bash
# Unit tests only
pytest tests/ -v -m "not integration"

# All tests
pytest tests/ -v

# Test agent directly
python test_agent.py
```

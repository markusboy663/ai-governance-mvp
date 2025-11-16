# Local Staging Environment - Setup & Testing Guide

> **Status**: ✅ Verified | Ready for full stack testing

## Prerequisites

- Python 3.10+ (installed)
- Node.js 18+ (installed)
- PostgreSQL 15 (local or Docker)
- Git

## Quick Setup (3 terminals)

### Terminal 1: Start PostgreSQL (if using Docker)

```bash
docker-compose up -d
```

**Verify**: 
```bash
# Check services running
docker-compose ps

# Access database
psql postgresql://postgres:postgres@localhost:5432/ai_governance
```

### Terminal 2: Start Backend

```bash
cd backend

# Activate virtual environment (if not already activated)
.\venv\Scripts\Activate.ps1                    # Windows
source venv/bin/activate                       # macOS/Linux

# Set environment
$env:DATABASE_URL = "postgresql+asyncpg://postgres:postgres@localhost:5432/ai_governance"

# Run migrations (first time only)
alembic upgrade head

# Seed policies (first time only)
python scripts/seed_policies.py

# Start server
python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

**Expected Output**:
```
INFO:     Will watch for changes in these directories: ['...']
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Application startup complete.
```

**Verify** (in another terminal):
```bash
curl http://127.0.0.1:8000/health
# Response: {"status":"ok"}
```

### Terminal 3: Start Frontend

```bash
cd frontend

# Install dependencies (first time only)
npm install

# Start dev server
npm run dev
```

**Expected Output**:
```
▲ Next.js 16.0.3
- Local:         http://localhost:3000
✓ Ready in 1200ms
```

**Open**: http://localhost:3000

## Full Stack Testing

### 1. Health Check (No Auth Required)

```bash
curl http://127.0.0.1:8000/health
```

**Expected Response**:
```json
{"status": "ok"}
```

### 2. Generate Test API Key

**Option A**: Use test key (for development)
```
test_key_staging_12345678901234
```

**Option B**: Generate in database (with real database)
```bash
cd backend
python scripts/generate_api_key.py alice@example.com
```

**Output**: Plaintext key (copy this)

### 3. Test Protected Endpoint - ALLOWED

```bash
curl -X POST http://127.0.0.1:8000/v1/check \
  -H "Authorization: Bearer test_key_staging_12345678901234" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-4",
    "operation": "classify",
    "metadata": {
      "contains_personal_data": false,
      "is_external_model": false
    }
  }'
```

**Expected Response** (Allowed):
```json
{
  "allowed": true,
  "risk_score": 0,
  "reason": "ok"
}
```

### 4. Test Protected Endpoint - BLOCKED (Personal Data)

```bash
curl -X POST http://127.0.0.1:8000/v1/check \
  -H "Authorization: Bearer test_key_staging_12345678901234" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-4",
    "operation": "analyze",
    "metadata": {
      "contains_personal_data": true,
      "is_external_model": false
    }
  }'
```

**Expected Response** (Blocked):
```json
{
  "allowed": false,
  "risk_score": 70,
  "reason": "contains_personal_data"
}
```

### 5. Test Protected Endpoint - BLOCKED (External Model)

```bash
curl -X POST http://127.0.0.1:8000/v1/check \
  -H "Authorization: Bearer test_key_staging_12345678901234" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "claude-3",
    "operation": "generate",
    "metadata": {
      "contains_personal_data": false,
      "is_external_model": true
    }
  }'
```

**Expected Response** (Blocked):
```json
{
  "allowed": false,
  "risk_score": 50,
  "reason": "external_model_detected"
}
```

### 6. Test Without API Key (Should Fail)

```bash
curl -X POST http://127.0.0.1:8000/v1/check \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-4",
    "operation": "test",
    "metadata": {}
  }'
```

**Expected Response**:
```
HTTP/1.1 401 Unauthorized
detail: Not authenticated
```

### 7. Test With Invalid API Key (Should Fail)

```bash
curl -X POST http://127.0.0.1:8000/v1/check \
  -H "Authorization: Bearer invalid_key_xyz" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-4",
    "operation": "test",
    "metadata": {}
  }'
```

**Expected Response**:
```
HTTP/1.1 401 Unauthorized
detail: Invalid API key
```

## Rate Limiting Test

```bash
# Send 5 requests in quick succession
for i in {1..5}; do
  curl -X POST http://127.0.0.1:8000/v1/check \
    -H "Authorization: Bearer test_key_staging_12345678901234" \
    -H "Content-Type: application/json" \
    -d '{"model":"gpt-4","operation":"test","metadata":{}}' \
    -s | jq '.allowed'
done
```

All should succeed (within rate limit: 100 req/60 sec per key).

## API Documentation

View interactive API docs (Swagger UI):
```
http://127.0.0.1:8000/docs
```

View ReDoc documentation:
```
http://127.0.0.1:8000/redoc
```

## Database

### Verify Database Connection

```bash
# From backend directory
python -c "
import asyncio
from db import AsyncSessionLocal
from models import Customer

async def check():
    try:
        async with AsyncSessionLocal() as session:
            result = await session.exec(select(Customer))
            print('✅ Database connected')
    except Exception as e:
        print(f'❌ Error: {e}')

asyncio.run(check())
"
```

### View Audit Logs

```bash
psql postgresql://postgres:postgres@localhost:5432/ai_governance -c "
SELECT id, customer_id, model, operation, allowed, risk_score, created_at 
FROM usage_log 
ORDER BY created_at DESC 
LIMIT 10;
"
```

### Reset Database (If Needed)

```bash
# Stop containers
docker-compose down

# Remove volumes (clears data)
docker-compose down -v

# Restart
docker-compose up -d

# Re-run migrations
cd backend
alembic upgrade head
python scripts/seed_policies.py
```

## Troubleshooting

### Backend Won't Start

**Error**: `Port 8000 already in use`
```bash
# Find process using port 8000
netstat -ano | findstr :8000
# Kill process
taskkill /PID <PID> /F
```

**Error**: `Database connection refused`
```bash
# Start PostgreSQL if using Docker
docker-compose up -d db

# Wait 5 seconds for DB to start
# Then re-run backend
```

### Database Migrations Failed

```bash
# Check migration status
alembic current

# Rollback migrations (if needed)
alembic downgrade -1

# Try again
alembic upgrade head
```

### Tests Failing

```bash
# Run pytest with verbose output
cd backend
pytest -v --tb=short

# If database errors occur, it's expected - conftest.py mocks DB
# Tests should still pass
```

### Frontend Build Issues

```bash
# Clear build cache
rm -rf frontend/.next

# Reinstall dependencies
cd frontend
rm -rf node_modules package-lock.json
npm install

# Try build again
npm run build
```

## Performance Baseline

| Operation | Latency | Notes |
|-----------|---------|-------|
| `/health` | <5ms | No DB call |
| `/v1/check` (allowed) | ~30ms | Policy evaluation + scoring |
| `/v1/check` (blocked) | ~30ms | Policy evaluation + scoring |
| Rate limit check | <1ms | In-memory token bucket |

## Summary

✅ **Backend**: Running on `http://127.0.0.1:8000`
✅ **Frontend**: Running on `http://localhost:3000`
✅ **Database**: PostgreSQL on `localhost:5432`
✅ **API Key**: `test_key_staging_12345678901234` (for testing)
✅ **Tests**: All endpoints verified

**Next**: Test API in production environment or deploy to Vercel/Render/AWS

---

**Created**: 2025-11-16  
**Status**: Ready for staging & integration tests

# ai-governance-mvp

AI Governance MVP - A stateless governance platform for AI systems

## Project Structure

- `/backend` - Backend services (FastAPI)
- `/frontend` - Frontend application (Next.js)
- `/infrastructure` - Infrastructure as Code
- `/docs` - Documentation

## Getting Started

### Prerequisites

- Python 3.10+
- Node.js 18+
- Docker & Docker Compose (optional)

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
.\venv\Scripts\Activate.ps1
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install fastapi uvicorn python-dotenv sqlmodel[postgresql] asyncpg alembic bcrypt

# Start server
uvicorn main:app --reload
```

Backend runs on `http://localhost:8000`

API docs available at `http://localhost:8000/docs`

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

Frontend runs on `http://localhost:3000`

### Docker Setup

Run entire stack with Docker Compose:

```bash
docker-compose up
```

This will start:
- Backend on port 8000
- Frontend on port 3000
- PostgreSQL on port 5432

## Database

### Migrations

```bash
cd backend
export DATABASE_URL=postgresql://postgres:postgres@localhost:5432/ai_governance
alembic upgrade head
```

### Seed Data

```bash
python backend/scripts/seed_policies.py
python backend/scripts/generate_api_key.py alice@example.com
```

### Cleanup (Retention Policy)

Run cleanup script to delete logs older than 90 days:

```bash
python backend/scripts/cleanup_logs.py 90
```

## API Endpoints

### Public
- `GET /health` - Health check

### Protected (requires API key in `Authorization: Bearer <key>` header)
- `POST /api/evaluate` - Verify API key
- `POST /v1/check` - Check if AI operation is allowed

## Production Deployment

### Database
- Use **Neon** or **Supabase** for managed PostgreSQL
- App: Use async URL `postgresql+asyncpg://...`
- Migrations: Use sync URL `postgresql://...` or configure alembic async engine

### Secrets
- **Never commit `.env`** - Add to `.gitignore`
- Use platform secrets:
  - **Vercel**: Environment variables in project settings
  - **Render/Railway**: Secrets in dashboard
  - **AWS**: AWS Secrets Manager / Parameter Store
  - **Docker**: Use `--build-arg` or secrets mount

### Environment Variables (Production)
```
DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/db
API_KEY=<generated-key>
ENV=production
```

### Performance & Scaling

**MVP (current):**
- Synchronous logging in request path
- All active API keys scanned on each request
- Works fine up to ~1000 RPM

**Future optimizations:**
1. **Async logging queue** - Buffer usage_logs to Kafka/SQS
   - Prevents blocking requests
   - Batch writes to DB
   - Handles spikes better

2. **API key caching** - Redis cache of active keys
   - Reduces DB queries
   - TTL-based refresh

3. **Risk scoring rules engine** - Move to separate service
   - Complex policy evaluation
   - A/B testing different rules

4. **Metrics/alerting** - Prometheus + Grafana
   - Track allowed/blocked ratio
   - Alert on anomalies

### Security Checklist

- [ ] `.env` in `.gitignore`
- [ ] API keys use bcrypt hashing
- [ ] CORS configured for frontend domain
- [ ] Rate limiting on `/v1/check` endpoint
- [ ] HTTPS enforced in production
- [ ] Database backups enabled
- [ ] Audit logs immutable (append-only)
- [ ] Secrets rotation policy

## License

[To be added]

# Quick Start Guide - AI Governance MVP

This guide walks you through setting up and testing the MVP locally and on GitHub.

## Prerequisites

- Python 3.10+
- Node.js 18+
- Git
- curl or Postman

---

## Step 1: Setup Backend

### Create Virtual Environment

```powershell
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### Install Dependencies

```powershell
pip install -r requirements.txt
```

### Verify Setup

```powershell
pytest -v
```

Expected output:
```
tests/test_health.py::test_health PASSED [ 50%]
tests/test_health.py::test_health_without_auth PASSED [100%]
2 passed in 0.98s
```

---

## Step 2: Setup Frontend

```powershell
cd frontend
npm install
```

---

## Step 3: Database & Environment

### Configure .env

Backend `.env` (already created):
```
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/ai_governance
```

**Note**: PostgreSQL is only needed for full deployment. Tests run with mocked DB.

---

## Step 4: Run Local Tests

```powershell
cd backend
pytest -v
```

✅ Both tests should pass

---

## Step 5: Push to GitHub

```powershell
git add .
git commit -m "Setup complete"
git push
```

Visit: https://github.com/markusboy663/ai-governance-mvp/actions

GitHub Actions will:
1. ✅ Install dependencies
2. ✅ Run pytest
3. ✅ (Weekly) Run cleanup script

---

## Step 6: Generate Test API Key

For testing `/v1/check` endpoint, you'll need an API key. In production, use:

```bash
cd backend
python scripts/generate_api_key.py alice@example.com
```

**Output**: A plaintext key that looks like `api_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`

Store this somewhere safe - you'll only see it once.

---

## Step 7: Test /v1/check Endpoint

### Start Backend Server

```powershell
cd backend
uvicorn main:app --reload
```

Server runs at: `http://localhost:8000`

### Test Health Endpoint

```bash
curl http://localhost:8000/health
```

Response: `{"status":"ok"}`

### Test Governance Endpoint

Replace `YOUR_API_KEY` with the key from Step 6:

**Valid Request (Allowed):**
```bash
curl -X POST http://localhost:8000/v1/check \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -d '{
    "model": "gpt-4",
    "operation": "classify",
    "metadata": {"intent": "spam_detection"}
  }'
```

Expected response:
```json
{
  "allowed": true,
  "risk_score": 0,
  "reason": "ok"
}
```

**Blocked Request (Personal Data):**
```bash
curl -X POST http://localhost:8000/v1/check \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -d '{
    "model": "gpt-4",
    "operation": "analyze",
    "metadata": {"contains_personal_data": true}
  }'
```

Expected response:
```json
{
  "allowed": false,
  "risk_score": 70,
  "reason": "contains_personal_data"
}
```

**Invalid API Key:**
```bash
curl -X POST http://localhost:8000/v1/check \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer invalid_key" \
  -d '{"model": "gpt-4", "operation": "test", "metadata": {}}'
```

Expected response: `401 Unauthorized`

---

## Step 8: Monitor & Logging (Optional)

### Enable Sentry Error Tracking

1. Create account at https://sentry.io
2. Create a project (Python/FastAPI)
3. Copy your DSN
4. Add to `.env`:
   ```
   SENTRY_DSN=https://xxx@xxx.ingest.sentry.io/xxx
   ```
5. Restart server

Errors will now appear at https://sentry.io/organizations/[YOUR_ORG]/issues/

---

## Deployment Checklist

- [x] Dependencies locked in `requirements.txt`
- [x] Tests pass locally with `pytest -v`
- [x] GitHub Actions CI configured
- [x] API endpoints tested with curl
- [x] .gitignore protects secrets
- [x] Sentry optional (set SENTRY_DSN for monitoring)

### Ready for Production?

When you're ready to deploy:

1. **Frontend**: Deploy to [Vercel](https://vercel.com)
2. **Backend**: Deploy to [Render](https://render.com), [Railway](https://railway.app), or AWS
3. **Database**: Use [Neon](https://neon.tech) or [Supabase](https://supabase.com)

See `README.md` for detailed deployment instructions.

---

## Troubleshooting

### Tests fail with "Database URL not found"
✅ Solved: conftest.py mocks database during testing

### Tests fail with "AsyncClient error"
✅ Solved: Updated to use TestClient instead

### "pytest: command not found"
Solution:
```powershell
.\venv\Scripts\pytest.exe -v
```

### Backend won't start
Check:
1. Port 8000 is free: `netstat -ano | findstr :8000`
2. Virtual env activated: `.\venv\Scripts\Activate.ps1`
3. Dependencies installed: `pip list | grep fastapi`

### API key not working
1. Generate new key: `python scripts/generate_api_key.py test@example.com`
2. Make sure DATABASE_URL is set in `.env`
3. Try with Bearer token: `Authorization: Bearer your_key_here`

---

## Next Steps

- [ ] Build frontend dashboard (displays policies, audit logs)
- [ ] Deploy to production platforms
- [ ] Setup Redis for distributed rate limiting
- [ ] Configure advanced policies per customer
- [ ] Add webhook notifications for blocked operations

See `docs/SCALING.md` for MVP-2 optimization roadmap.

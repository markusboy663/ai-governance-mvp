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

## Step 3: Run Tests

```powershell
cd backend
python -m pytest tests/test_integration.py -v
```

Expected: **All 15 tests pass** ✅

---

## Step 4: Start Backend Server

### Option A: Using startup script (Recommended)

```powershell
# From project root
python start_backend.py

# Or use batch file on Windows
.\start_backend.bat
```

### Option B: Manual (from backend directory)

```powershell
cd backend
python -m uvicorn main:app --host 0.0.0.0 --port 8000
```

Expected output:
```
[WARNING] DATABASE_URL not set - database features disabled
INFO:     Started server process [XXXX]
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

---

## Step 5: Start Frontend Server

### Terminal 2 (new terminal)

```powershell
cd frontend
npm run dev
```

Expected output:
```
▲ Next.js 16.0.3 (Turbopack)
- Local: http://localhost:3000
✓ Ready in 1100ms
```

---

## Step 6: Verify Both Servers

```powershell
# Test health endpoint
curl http://localhost:8000/health

# Test API endpoint with auth
curl -X POST http://localhost:8000/v1/check `
  -H "Authorization: Bearer test-key.secret" `
  -H "Content-Type: application/json" `
  -d '{"model":"gpt-4","operation":"test","metadata":{}}'
```

Expected response:
```json
{
  "allowed": true,
  "risk_score": 0,
  "reason": "ok"
}
```

Open browser to `http://localhost:3000` - Dashboard should load!

---

## Step 7: Push to GitHub

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

### Backend won't start - "Error loading ASGI app. Could not import module 'main'"

**Problem**: Using `cd` in PowerShell with background processes doesn't change directory properly

**Solution**: Use one of these approaches:

1. **Use startup script (RECOMMENDED)**:
   ```powershell
   python start_backend.py     # Python script
   .\start_backend.bat         # Or batch file
   ```

2. **Use full path with cd separator**:
   ```powershell
   cd C:\Users\marku\Desktop\ai-governance-mvp\backend; python -m uvicorn main:app --host 0.0.0.0 --port 8000
   ```

3. **Use semicolon separator**:
   ```powershell
   cd backend; python -m uvicorn main:app --host 0.0.0.0 --port 8000
   ```

The startup scripts handle directory changes automatically!

---

### Port 8000 already in use

```powershell
# Kill existing Python processes
Get-Process python | Stop-Process -Force
Start-Sleep -Seconds 2

# Then start backend
python start_backend.py
```

---

### Frontend shows "Backend connection refused"

Check backend is running:
```powershell
curl http://127.0.0.1:8000/health
```

If not running, start it in another terminal:
```powershell
python start_backend.py
```
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

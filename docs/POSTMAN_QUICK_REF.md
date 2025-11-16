# Postman Collection - Quick Reference Card

## 📋 What's Included

| File | Purpose | Size |
|------|---------|------|
| `postman_collection.json` | 11 automated test requests | 20 KB |
| `postman_environment.json` | Pre-configured variables | 1 KB |
| `POSTMAN_GUIDE.md` | Step-by-step usage guide | 8 KB |
| `README_POSTMAN.md` | Complete reference | 12 KB |
| `POSTMAN_TESTS.md` | Implementation summary | 11 KB |
| `run_postman_tests.py` | Python CLI runner | 8 KB |
| `run_postman_tests.ps1` | PowerShell CLI runner | 5 KB |

---

## 🚀 3-Second Start

```bash
# Option A: Desktop (Easiest)
1. Open Postman
2. Import → docs/postman_collection.json
3. Select environment dropdown → AI Governance MVP - Local
4. Click any request → Send

# Option B: Command Line (Fastest)
python run_postman_tests.py

# Option C: PowerShell (Windows Native)
.\run_postman_tests.ps1
```

---

## 📊 11 Test Requests

### 🟢 Health (1)
- GET `/health` → Should return `{"status": "ok"}`

### 🔐 Authentication (2)
- POST `/v1/check` (no auth) → 401 Unauthorized
- POST `/v1/check` (invalid key) → 401 Unauthorized

### ✅ Policy Evaluation (4)
- POST `/v1/check` (no flags) → `allowed: true, risk_score: 0`
- POST `/v1/check` (personal data) → `allowed: false, risk_score: 70`
- POST `/v1/check` (external model) → `allowed: false, risk_score: 50`
- POST `/v1/check` (both flags) → `allowed: false, risk_score: 120`

### 🚀 Rate Limiting (2)
- 100 rapid requests → All 200 OK (pass)
- 101st request → 429 Too Many Requests (pass)

### 🔒 Security (2)
- POST with `prompt` field → 400/422 Bad Request
- POST with `content` field → 400/422 Bad Request

---

## ⚙️ Configuration

**Environment Variables** (top right in Postman):
```
BASE_URL  = http://localhost:8000
API_KEY   = test_key_staging_12345678901234
```

**Update for different servers**:
```
LOCAL:      http://localhost:8000
STAGING:    http://staging.example.com
PRODUCTION: https://api.example.com
```

---

## 🧪 Running Tests

### Desktop (GUI)
```
1. Collections → AI Governance MVP → Run
2. Select environment → AI Governance MVP - Local
3. Click "Start Test Run"
4. Watch results in real-time
```

### Command Line (Python)
```bash
python run_postman_tests.py
python run_postman_tests.py --url http://staging.example.com
python run_postman_tests.py --report  # Generate HTML
```

### Command Line (PowerShell)
```powershell
.\run_postman_tests.ps1
.\run_postman_tests.ps1 -BaseUrl "http://staging.example.com"
.\run_postman_tests.ps1 -GenerateReport
```

### Command Line (Newman - Direct)
```bash
npm install -g newman
newman run docs/postman_collection.json \
  --environment docs/postman_environment.json
```

---

## ✅ Success Criteria

All 11 requests should show:
- ✅ Status code correct (200, 401, 429, etc.)
- ✅ Response structure valid (has required fields)
- ✅ Response time <1000ms
- ✅ All assertions pass

---

## 🚨 Common Issues

| Issue | Fix |
|-------|-----|
| "Cannot connect" | Start backend: `python -m uvicorn main:app --reload` |
| "Invalid API key" | Generate new key: `python scripts/generate_api_key.py` |
| "Rate limit test fails" | Run tests without delays between them |
| "Forbidden field returns 200" | Check governance logic in `main.py` |

---

## 📚 Documentation

- **POSTMAN_GUIDE.md** - Detailed step-by-step guide
- **README_POSTMAN.md** - Complete reference with examples
- **POSTMAN_TESTS.md** - Full implementation summary
- **docs/TESTING.md** - API endpoint documentation

---

## 🎯 Use Cases

| User | Usage |
|------|-------|
| **QA Team** | Run collection to verify release |
| **Pilot Customers** | Import collection to validate policies |
| **DevOps/CI** | Use Python runner in GitHub Actions |
| **Developers** | Debug endpoints interactively in Postman |

---

## 📊 Test Results Example

```
✅ Health Check - Status code is 200
✅ No Auth - Status code is 401 (Unauthorized)
✅ Invalid Key - Status code is 401 (Unauthorized)
✅ Policy ALLOWED - allowed: true, risk_score: 0
✅ Policy BLOCKED (Personal) - allowed: false, risk_score: 70
✅ Policy BLOCKED (External) - allowed: false, risk_score: 50
✅ Policy BLOCKED (High Risk) - allowed: false, risk_score: 120
✅ Rate Limit Pass - All 100 requests: 200 OK
✅ Rate Limit Fail - Request 101: 429 Too Many
✅ Security Check (prompt) - Status code 400
✅ Security Check (content) - Status code 400

================================================
✅ ALL TESTS PASSED (11/11)
================================================
Execution Time: 2.3 seconds
Environment: Local (http://localhost:8000)
```

---

## 💾 API Key Generation

```bash
# Generate new test API key
cd backend
python scripts/generate_api_key.py

# Output:
# Raw Key:  test_key_new_xxxxxxxxxxxxxxxxxxxx
# Hash:     $2b$12$abcdef123456789...

# Copy raw key and update in:
# 1. Postman environment (API_KEY variable)
# 2. run_postman_tests.py --api-key
# 3. run_postman_tests.ps1 -ApiKey
```

---

## 🔗 Quick Links

**Files**:
- `docs/postman_collection.json` - Main test suite
- `docs/postman_environment.json` - Variables
- `run_postman_tests.py` - Python runner
- `run_postman_tests.ps1` - PowerShell runner

**Documentation**:
- `docs/POSTMAN_GUIDE.md` - User guide
- `docs/README_POSTMAN.md` - Full reference
- `docs/POSTMAN_TESTS.md` - Summary
- `README.md` - Project overview

**Related**:
- `docs/STAGING.md` - Local environment setup
- `docs/TESTING.md` - API documentation
- `gen_test_key.py` - Test key generator

---

**Status**: ✅ Ready for QA & Testing  
**Created**: November 16, 2025  
**Version**: 1.0

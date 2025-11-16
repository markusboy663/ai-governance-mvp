# Postman Collection - Complete Testing Guide

**AI Governance MVP - Automated Testing Suite**

---

## 📋 Overview

This Postman collection provides:

✅ **11 comprehensive test requests** covering all API endpoints  
✅ **Automated assertions** for each request (sanity checks)  
✅ **Rate limiting validation** (100 req/60s testing)  
✅ **Security checks** (forbidden field detection)  
✅ **Authentication tests** (valid/invalid keys)  
✅ **Pre-configured environment variables**

Perfect for:
- QA teams validating releases
- Pilot programs testing governance policies
- Integration testing before deployment
- Continuous performance monitoring

---

## 🚀 Quick Start

### 1. Import into Postman (Desktop)

**Windows**:
```powershell
# Option A: Manual Import
# 1. Open Postman
# 2. Click "Import" (top left)
# 3. Select docs/postman_collection.json
# 4. Click "Import"
# 5. Import environment: docs/postman_environment.json

# Option B: Use Postman CLI (Newman)
npx newman run docs/postman_collection.json \
  --environment docs/postman_environment.json
```

### 2. Set Environment Variables

In Postman (top right dropdown):
- **BASE_URL**: `http://localhost:8000` (or your server)
- **API_KEY**: `test_key_staging_12345678901234` (or your key)

### 3. Run Tests

**Send individual request**:
- Click request name
- Click "Send"
- View results in "Tests" tab

**Run entire collection**:
- Click "Run" button
- Select "AI Governance MVP"
- Click "Start Test Run"

---

## 📁 Files Included

| File | Purpose |
|------|---------|
| `postman_collection.json` | Complete API test suite (11 requests) |
| `postman_environment.json` | Environment variables (BASE_URL, API_KEY) |
| `run_postman_tests.py` | Python CLI test runner |
| `run_postman_tests.ps1` | PowerShell test runner |
| `POSTMAN_GUIDE.md` | Detailed user guide |
| `README_POSTMAN.md` | This file |

---

## 🧪 Test Structure

### Folder 1: Health & Setup
- **Health Check**: Validates server availability

### Folder 2: Authentication
- **No Auth - Should Fail**: Tests rejection without credentials
- **Invalid API Key - Should Fail**: Tests rejection with invalid key

### Folder 3: Policy Evaluation
- **✅ ALLOWED - No Risk Flags**: Tests normal operation passes
- **⚠️ BLOCKED - Personal Data**: Tests personal data protection
- **⚠️ BLOCKED - External Model**: Tests external model restriction
- **⚠️ BLOCKED - High Risk**: Tests combined risk factors (personal data + external model)

### Folder 4: Rate Limiting
- **Rapid Fire - First 100 Requests**: Tests requests within window pass
- **Rate Limit Exceeded - 429**: Tests requests beyond limit are rejected

### Folder 5: Security Validation
- **Forbidden Field - 'prompt'**: Tests prompt field rejection
- **Forbidden Field - 'content'**: Tests content field rejection in nested objects

---

## 🔄 Running Tests via CLI

### Python (Recommended for CI/CD)

```bash
# Run with default settings
python run_postman_tests.py

# Run against staging server
python run_postman_tests.py --url http://staging.example.com

# Run with custom API key
python run_postman_tests.py --api-key your_api_key_here

# Generate HTML report
python run_postman_tests.py --report

# All together
python run_postman_tests.py \
  --url http://staging.example.com \
  --api-key your_api_key \
  --report
```

### PowerShell (Windows)

```powershell
# Run with default settings
.\run_postman_tests.ps1

# Run against staging
.\run_postman_tests.ps1 -BaseUrl "http://staging.example.com"

# Run with custom API key
.\run_postman_tests.ps1 -ApiKey "your_custom_key"

# Generate HTML report
.\run_postman_tests.ps1 -GenerateReport

# All together
.\run_postman_tests.ps1 `
  -BaseUrl "http://staging.example.com" `
  -ApiKey "your_api_key" `
  -GenerateReport
```

### Newman (Direct)

```bash
# Install Newman
npm install -g newman

# Run collection
newman run docs/postman_collection.json \
  --environment docs/postman_environment.json

# Generate reports
newman run docs/postman_collection.json \
  --environment docs/postman_environment.json \
  --reporters cli,json,html \
  --reporter-html-export report.html
```

---

## ✅ Expected Results

### Successful Test Run

```
Health Check
✅ Status code is 200
✅ Response has status field
✅ Response time is less than 500ms

Authentication - No Auth
✅ Status code is 401 (Unauthorized)
✅ Error message indicates missing credentials

Policy Evaluation - ALLOWED
✅ Status code is 200
✅ Response structure is valid
✅ Request is allowed (risk_score = 0)

Rate Limiting
✅ First 100 requests: 200 OK
✅ Request 101+: 429 Too Many Requests
```

### Common Failures

| Issue | Cause | Fix |
|-------|-------|-----|
| Connection refused | Server not running | Start backend: `python -m uvicorn main:app --reload` |
| Invalid API key | Wrong key configured | Update `API_KEY` env var in Postman |
| Rate limit test fails | Wrong rate limit config | Check `rate_limit.py` (default: 100/60s) |
| Forbidden field test fails | Field validation disabled | Check governance logic in `main.py` |

---

## 🔐 API Key Management

### Generate Test Key

```bash
# Generate new test API key
cd backend
python scripts/generate_api_key.py

# Output example:
# Raw Key:  test_key_staging_12345678901234
# Hash:     $2b$12$abcdef123456789...
```

### Update Postman

1. **Copy raw key** from generate script output
2. **Go to Postman** → Environments
3. **Select "AI Governance MVP - Local"**
4. **Update API_KEY value**
5. **Click Save**

### Production Keys

For production testing:
- Obtain API key from administrator
- Create new environment file (e.g., `postman_environment_prod.json`)
- Update BASE_URL and API_KEY
- Run tests against production

---

## 📊 Interpreting Results

### Response Code Legend

| Code | Meaning | When to Expect |
|------|---------|-----------------|
| 200 | OK - Request succeeded | Valid requests to `/v1/check` |
| 400 | Bad Request | Forbidden fields detected |
| 401 | Unauthorized | Missing/invalid API key |
| 422 | Validation Error | Invalid request format |
| 429 | Too Many Requests | Rate limit exceeded |

### Risk Score Explanation

| Flag | Risk Score | Result |
|------|-----------|--------|
| None | 0 | ✅ ALLOWED |
| `contains_personal_data: true` | 70 | ⚠️ BLOCKED |
| `uses_external_model: true` | 50 | ⚠️ BLOCKED |
| Both flags | 120 | ⚠️ BLOCKED |

**Threshold**: Requests with risk_score > 50 are blocked

---

## 🔍 Detailed Test Descriptions

### Health Check
```
GET /health
No authentication required
Expected: {"status": "ok"}
Purpose: Verify server is running and responsive
```

### Authentication Tests
```
POST /v1/check (without auth)
Expected: 401 Unauthorized
Purpose: Ensure unauthenticated access is rejected

POST /v1/check (with invalid key)
Expected: 401 Unauthorized  
Purpose: Ensure invalid credentials are rejected
```

### Policy Evaluation Tests
```
POST /v1/check (no risk flags)
Body: {"model": "gpt-4", "operation": "chat_completion", "metadata": {...}}
Expected: {"allowed": true, "risk_score": 0, "reason": "ok"}
Purpose: Test normal operations pass through

POST /v1/check (personal data flag)
Body includes: "contains_personal_data": true
Expected: {"allowed": false, "risk_score": 70, "reason": "Personal data..."}
Purpose: Test personal data protection is enforced

POST /v1/check (external model flag)
Body includes: "uses_external_model": true
Expected: {"allowed": false, "risk_score": 50, "reason": "External model..."}
Purpose: Test external model restrictions

POST /v1/check (both flags)
Body includes: both flags above
Expected: {"allowed": false, "risk_score": 120, ...}
Purpose: Test combined risk scoring
```

### Rate Limiting Tests
```
Rapid Fire - 100 requests/60s
Expected: All return 200 OK
Purpose: Verify within-limit requests are allowed

Request 101+
Expected: 429 Too Many Requests
Purpose: Verify limit enforcement (resets after 60s)
```

### Security Tests
```
POST /v1/check with "prompt" field in metadata
Expected: 400/422 Bad Request
Purpose: Verify prompt field is rejected

POST /v1/check with "content" field nested in metadata
Expected: 400/422 Bad Request
Purpose: Verify recursive content field detection
```

---

## 🚨 Troubleshooting

### "Cannot connect to localhost:8000"

**Problem**: Backend server not running

**Solution**:
```powershell
cd C:\Users\marku\Desktop\ai-governance-mvp\backend
python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

Wait for: `Uvicorn running on http://127.0.0.1:8000`

---

### "Invalid API key" (401 error)

**Problem**: API_KEY environment variable doesn't match database

**Solution**:
1. Generate new test key:
   ```bash
   python scripts/generate_api_key.py
   ```
2. Copy the **raw key** output
3. In Postman: Environments → Update API_KEY value
4. Click Save
5. Retry requests

---

### "Tests passed but rate limit test failed"

**Problem**: Rate limit window (60s) might be resetting between tests

**Solution**:
- Run rate limit tests consecutively without delays
- Or manually trigger 100+ requests rapidly using the collection runner

---

### "Forbidden field test returns 200 instead of 400"

**Problem**: Forbidden field validation might be disabled

**Solution**:
1. Check `main.py` for `contains_forbidden_fields()` function
2. Verify it's called in `/v1/check` endpoint
3. Check fields match: `{"prompt", "text", "input", "message", "messages", "content"}`
4. Test with curl to debug:
   ```bash
   curl -X POST http://localhost:8000/v1/check \
     -H "Authorization: Bearer test_key_staging_12345678901234" \
     -H "Content-Type: application/json" \
     -d '{"model":"gpt-4","operation":"test","metadata":{"prompt":"test"}}'
   ```

---

## 📈 Performance Benchmarks

Expected response times (local environment):

| Endpoint | Operation | Time |
|----------|-----------|------|
| /health | No processing | <10ms |
| /v1/check | No risk flags | 50-100ms |
| /v1/check | With risk flags | 50-100ms |
| /v1/check | Rate limit check | 5-20ms |

**Slow responses indicate**:
- Database connection issues
- High server load
- Network latency

---

## 🔄 CI/CD Integration

### GitHub Actions Example

```yaml
name: Postman Tests
on: [push, pull_request]

jobs:
  postman-tests:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_DB: ai_governance
          POSTGRES_PASSWORD: postgres
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    steps:
      - uses: actions/checkout@v3
      
      - name: Start backend
        run: |
          cd backend
          pip install -r requirements.txt
          python -m uvicorn main:app --host 0.0.0.0 --port 8000 &
          sleep 2
      
      - name: Run Postman tests
        run: |
          npm install -g newman
          newman run docs/postman_collection.json \
            --environment docs/postman_environment.json \
            --reporters cli,json \
            --reporter-json-export results.json
      
      - name: Upload results
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: postman-results
          path: results.json
```

---

## 📞 Support & Documentation

**Need help?**

1. **POSTMAN_GUIDE.md** - Detailed Postman usage guide
2. **docs/TESTING.md** - API endpoint documentation
3. **docs/STAGING.md** - Local environment setup
4. **README.md** - Project overview

**API Reference**:
- `GET /health` - Health check (no auth required)
- `POST /v1/check` - Policy evaluation (requires Bearer token)
- `POST /api/evaluate` - Alternative endpoint (requires Bearer token)

---

## 📝 Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | Nov 16, 2025 | Initial release - 11 test requests, 2 CLI runners |
| - | - | - |

---

**Last Updated**: November 16, 2025  
**Status**: ✅ Ready for QA & Testing  
**Maintained By**: AI Governance MVP Project

# Postman Collection Guide

**AI Governance MVP - QA & Testing Suite**

Complete API testing collection with automated sanity tests and rate limiting validation.

---

## Quick Start

### 1. Import Collection & Environment

1. **Open Postman** (https://www.postman.com/downloads/)
2. **Click "Import"** (top left)
3. **Select `docs/postman_collection.json`**
4. **Click "Import"**
5. **Import environment**: Click **Import → `docs/postman_environment.json`**
6. **Select environment**: Top right dropdown, choose **"AI Governance MVP - Local"**

### 2. Set Your API Key

**Option A: Use Test Key (Default)**
- Already pre-configured: `test_key_staging_12345678901234`
- Ready to use immediately

**Option B: Generate New Test Key**
```powershell
cd C:\Users\marku\Desktop\ai-governance-mvp
python gen_test_key.py
```

**Option C: Create Production Key**
- Contact admin to generate production API key
- Update `{{API_KEY}}` variable in Postman

### 3. Update BASE_URL If Needed

- **Local development**: `http://localhost:8000` ✅ (default)
- **Staging server**: `http://staging-api.example.com`
- **Production**: `https://api.example.com`

Edit in Postman: **Environments → AI Governance MVP - Local → BASE_URL**

---

## Test Suite Overview

### 🟢 Health & Setup (Quick Validation)

**1. Health Check**
- Validates server is running
- ✅ Should return `{"status": "ok"}` in <500ms
- **Run first** to verify connectivity

### 🔐 Authentication Tests

**2. No Auth - Should Fail**
- POST `/v1/check` without Authorization header
- ✅ Should return **401 Unauthorized**
- Tests that unauthenticated requests are rejected

**3. Invalid API Key - Should Fail**
- POST `/v1/check` with invalid key
- ✅ Should return **401 Unauthorized**
- Tests that invalid credentials are rejected

### ✅ Policy Evaluation (Core Tests)

**4. ALLOWED - No Risk Flags**
- Request with no governance flags
- ✅ Should return `allowed: true, risk_score: 0`
- Base case: normal operations pass

**5. BLOCKED - Personal Data**
- Request with `contains_personal_data: true`
- ✅ Should return `allowed: false, risk_score: 70+`
- Tests personal data protection

**6. BLOCKED - External Model**
- Request with `uses_external_model: true`
- ✅ Should return `allowed: false, risk_score: 50+`
- Tests external model restrictions

**7. BLOCKED - High Risk**
- Request with both personal data + external model
- ✅ Should return `allowed: false, risk_score: 120+`
- Tests combined risk factors

### 🚀 Rate Limiting Tests

**8. Rapid Fire - First 100 Requests**
- Sends requests in rapid succession
- ✅ Should all return **200 OK** (within limit)
- Tests rate limit window works

**9. Rate Limit Exceeded - 429**
- Send after hitting 100 request limit
- ✅ Should return **429 Too Many Requests**
- Tests rate limit enforcement

### 🔒 Security Validation

**10. Forbidden Field - 'prompt'**
- Includes `prompt` field in metadata
- ✅ Should return **400/422 Bad Request**
- Tests content field protection

**11. Forbidden Field - 'content'**
- Includes `content` in nested objects
- ✅ Should return **400/422 Bad Request**
- Tests recursive content validation

---

## Running Tests

### Option 1: Run Individual Test

1. Click on any request (e.g., "✅ ALLOWED - No Risk Flags")
2. Click **Send**
3. Check results in **Tests** tab

### Option 2: Run Full Collection

1. Click **"Run"** button (collection name)
2. Select **"AI Governance MVP"** collection
3. Select **"AI Governance MVP - Local"** environment
4. Click **"Start Test Run"**
5. Watch tests execute sequentially
6. Review **Summary** tab when complete

### Option 3: Run Test Folder

1. Click **⋮ (three dots)** next to folder name
2. Click **"Run Folder"**
3. Tests execute in order

---

## Interpreting Results

### ✅ PASS (Green)

```
✅ Status code is 200
✅ Response has status field
✅ Response time is less than 500ms
```

Request executed successfully, all assertions passed.

### ❌ FAIL (Red)

```
❌ Status code is 200
   Expected: 200
   Actual: 401
```

Request failed - check:
- API key is valid
- Server is running
- Endpoint URL is correct

### ⚠️ SKIP (Orange)

Test skipped - usually due to previous test failure. Fix errors in order.

---

## Common Issues

### "Connection refused" or "Cannot connect"

**Problem**: Server not running

**Solution**:
```powershell
cd C:\Users\marku\Desktop\ai-governance-mvp\backend
python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

Wait for: `Uvicorn running on http://127.0.0.1:8000`

### "Invalid API key"

**Problem**: API_KEY variable not set or wrong key

**Solution**:
1. Check Postman environment dropdown (top right)
2. Click on active environment
3. Verify `API_KEY` value matches generated key
4. Click **Save** after changes

### "Rate limit exceeded"

**Problem**: Hit 100 requests/60sec limit

**Solution**:
- Wait 60 seconds, then retry
- Or use different API key
- Rate limit resets automatically

### Tests in "Policy Evaluation" show wrong risk_score

**Problem**: Governance policies not initialized in database

**Solution**:
```powershell
cd C:\Users\marku\Desktop\ai-governance-mvp\backend
python -m scripts.seed_policies
```

---

## Advanced Usage

### Custom Request

Create new request in collection:

```json
POST /v1/check
Authorization: Bearer {{API_KEY}}

{
    "model": "gpt-4",
    "operation": "classification",
    "metadata": {
        "contains_personal_data": false,
        "uses_external_model": false,
        "custom_field": "value"
    }
}
```

Add test script:
```javascript
pm.test('Custom validation', function () {
    var jsonData = pm.response.json();
    pm.expect(jsonData.allowed).to.be.true;
});
```

### Batch Testing

Run multiple environments:
1. Create copies of environment for staging/prod
2. Update BASE_URL for each
3. Run collection against each environment
4. Compare results

### Performance Testing

Monitor response times:
- **Excellent**: <100ms
- **Good**: 100-500ms
- **Acceptable**: 500-1000ms
- **Slow**: >1000ms

View in **Test Results** → **Summary** → **Average response time**

---

## QA Checklist

- [ ] Health check passes
- [ ] Authentication rejects invalid keys
- [ ] Valid request returns allowed: true
- [ ] Personal data flag returns allowed: false
- [ ] External model flag returns allowed: false
- [ ] Combined flags return allowed: false
- [ ] First 100 requests allowed within 60s
- [ ] Request 101+ returns 429 error
- [ ] Forbidden fields are rejected
- [ ] Response times acceptable

---

## Integration Testing

### Test Against Different Servers

**Local**:
```
BASE_URL: http://localhost:8000
API_KEY: test_key_staging_12345678901234
```

**Staging**:
```
BASE_URL: http://staging.example.com
API_KEY: <staging API key>
```

**Production**:
```
BASE_URL: https://api.example.com
API_KEY: <production API key>
```

### Generate Report

1. Run full collection
2. Click **Export** (top right of results)
3. Choose **HTML Report**
4. Send to stakeholders

---

## Support

**Issues?** Check:
1. README.md - Project overview
2. docs/TESTING.md - API documentation
3. docs/STAGING.md - Local environment setup
4. QUICK_START.md - Getting started guide

**API Endpoints Reference**:
- `GET /health` - Health check (no auth)
- `POST /v1/check` - Policy evaluation (requires auth)
- `POST /api/evaluate` - Alias (requires auth)

---

**Last Updated**: November 16, 2025  
**Collection Version**: 1.0  
**Environment**: Local Development

# API Testing Guide

This document provides examples for testing the AI Governance MVP API.

## Quick Start

### 1. Health Check

Test that the backend is running:

```bash
curl http://localhost:8000/health
```

Expected response:
```json
{"status": "ok"}
```

---

## Protected Endpoints

These endpoints require a valid API key in the `Authorization` header.

### Generate an API Key

First, generate a test API key:

```bash
cd backend
source venv/bin/activate
python scripts/generate_api_key.py alice@example.com
```

Output:
```
Created API key (plaintext show once): api_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
Store hashed key in DB only.
```

**Copy the plaintext key** - you'll use it in the next step.

### 2. Check Governance Policy

Test the main governance endpoint:

```bash
curl -X POST http://localhost:8000/v1/check \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer api_YOUR_KEY_HERE" \
  -d '{
    "model": "gpt-4o-mini",
    "operation": "completion",
    "metadata": {
      "contains_personal_data": false,
      "is_external_model": false
    }
  }'
```

Expected response (allowed):
```json
{
  "allowed": true,
  "risk_score": 0,
  "reason": "ok"
}
```

### 3. Test with Personal Data Flag

Test request that should be blocked:

```bash
curl -X POST http://localhost:8000/v1/check \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer api_YOUR_KEY_HERE" \
  -d '{
    "model": "gpt-4o-mini",
    "operation": "completion",
    "metadata": {
      "contains_personal_data": true
    }
  }'
```

Expected response (blocked):
```json
{
  "allowed": false,
  "risk_score": 70,
  "reason": "contains_personal_data"
}
```

### 4. Test with Invalid API Key

Test that invalid keys are rejected:

```bash
curl -X POST http://localhost:8000/v1/check \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer invalid_key" \
  -d '{"model":"gpt-4o-mini","operation":"completion","metadata":{}}'
```

Expected response:
```json
{"detail":"Invalid API key"}
```
HTTP Status: 401

### 5. Test Forbidden Metadata

Try to send a prompt in metadata (should be rejected):

```bash
curl -X POST http://localhost:8000/v1/check \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer api_YOUR_KEY_HERE" \
  -d '{
    "model": "gpt-4o-mini",
    "operation": "completion",
    "metadata": {
      "prompt": "This is a secret prompt"
    }
  }'
```

Expected response:
```json
{"detail":"Forbidden metadata keys: {'prompt', 'text', 'input', 'content', 'message'}. Never send prompts in metadata."}
```
HTTP Status: 400

---

## Postman Setup

### Import Collection

Create a new Postman collection:

1. **File** → **New** → **Collection**
2. Name it: `AI Governance MVP`
3. Add requests below

### Environment Variables

1. **Create Environment** → Name: `local`
2. Add variables:
   - `base_url`: `http://localhost:8000`
   - `api_key`: `api_YOUR_KEY_HERE` (replace with actual key)

### Request 1: Health Check

**Method:** GET  
**URL:** `{{base_url}}/health`  
**Headers:** None  
**Body:** None

### Request 2: Check Policy (Allowed)

**Method:** POST  
**URL:** `{{base_url}}/v1/check`

**Headers:**
```
Content-Type: application/json
Authorization: Bearer {{api_key}}
```

**Body (raw JSON):**
```json
{
  "model": "gpt-4o-mini",
  "operation": "completion",
  "metadata": {
    "contains_personal_data": false,
    "is_external_model": false
  }
}
```

### Request 3: Check Policy (Blocked)

**Method:** POST  
**URL:** `{{base_url}}/v1/check`

**Headers:**
```
Content-Type: application/json
Authorization: Bearer {{api_key}}
```

**Body (raw JSON):**
```json
{
  "model": "gpt-4o-mini",
  "operation": "completion",
  "metadata": {
    "contains_personal_data": true
  }
}
```

### Request 4: Invalid API Key

**Method:** POST  
**URL:** `{{base_url}}/v1/check`

**Headers:**
```
Content-Type: application/json
Authorization: Bearer invalid_key
```

**Body (raw JSON):**
```json
{
  "model": "gpt-4o-mini",
  "operation": "completion",
  "metadata": {}
}
```

---

## Automated Testing

Run pytest to validate all endpoints:

```bash
cd backend
source venv/bin/activate
pytest -v
```

---

## Troubleshooting

**401 Unauthorized:**
- Check API key is correct
- Verify `Authorization: Bearer <key>` format
- Generate new key if needed: `python scripts/generate_api_key.py test@example.com`

**400 Bad Request:**
- Check metadata doesn't contain forbidden keys (prompt, text, input, content, message)
- Verify JSON is valid

**Connection Refused:**
- Ensure backend is running: `uvicorn main:app --reload`
- Check port 8000 is not blocked

---

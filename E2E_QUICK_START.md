# E2E Integration Tests - Quick Setup

**Status**: ✅ Ready to run

---

## 🚀 5-Minute Quick Start

### Prerequisites
- Docker & docker-compose (or PostgreSQL running locally)
- Python 3.10+
- Backend dependencies installed

### Option A: Using Docker (Easiest)

```bash
# 1. Start test database
docker-compose -f docker-compose.test.yml up -d

# 2. Wait for database
sleep 5

# 3. Go to backend
cd backend

# 4. Run integration tests
export TEST_DATABASE_URL="postgresql+asyncpg://postgres:postgres@localhost:5433/test_ai_governance"
pytest -v tests/test_integration.py

# 5. Stop test database
docker-compose -f docker-compose.test.yml down
```

### Option B: Using Local PostgreSQL

```bash
# 1. Create test database (if not exists)
psql -U postgres -c "CREATE DATABASE test_ai_governance;"

# 2. Go to backend
cd backend

# 3. Run integration tests
export TEST_DATABASE_URL="postgresql+asyncpg://postgres:postgres@localhost:5432/test_ai_governance"
pytest -v tests/test_integration.py
```

---

## 📊 Expected Output

```
test_integration.py::TestE2EIntegration::test_health_endpoint PASSED
test_integration.py::TestE2EIntegration::test_auth_invalid_key PASSED
test_integration.py::TestE2EIntegration::test_auth_missing_header PASSED
test_integration.py::TestE2EIntegration::test_allowed_operation PASSED
test_integration.py::TestE2EIntegration::test_blocked_personal_data PASSED
test_integration.py::TestE2EIntegration::test_blocked_external_model PASSED
test_integration.py::TestE2EIntegration::test_blocked_high_risk PASSED
test_integration.py::TestE2EIntegration::test_forbidden_field_prompt PASSED
test_integration.py::TestE2EIntegration::test_forbidden_field_content PASSED
test_integration.py::TestE2EIntegration::test_multiple_requests_same_key PASSED
test_integration.py::TestE2EIntegration::test_rate_limiting PASSED
test_integration.py::TestE2EIntegration::test_response_structure PASSED
test_integration.py::TestE2EIntegration::test_different_models PASSED
test_integration.py::TestE2EIntegration::test_edge_case_empty_metadata PASSED
test_integration.py::TestE2EIntegration::test_edge_case_null_metadata PASSED

============= 15 passed in 8.5s =============
```

---

## 🧪 What Gets Tested

✅ **15 comprehensive tests**:
- Health endpoint
- Authentication (valid & invalid)
- Policy evaluation (allowed & blocked)
- Risk scoring
- Rate limiting
- Security validation
- Edge cases

---

## 🔧 Advanced Commands

```bash
# Run only one test
pytest -v tests/test_integration.py::TestE2EIntegration::test_allowed_operation

# Run tests matching pattern
pytest -v tests/test_integration.py -k "blocked"

# Show detailed output
pytest -vv tests/test_integration.py

# Generate coverage
pytest --cov tests/test_integration.py

# Stop on first failure
pytest -x tests/test_integration.py
```

---

## 🚨 Common Issues

| Issue | Solution |
|-------|----------|
| "Connection refused" | Start Docker: `docker-compose -f docker-compose.test.yml up -d` |
| "Database already exists" | Drop: `dropdb test_ai_governance` |
| "No module named main" | Run from `backend/` directory |
| "Timeout" | Wait for DB: `sleep 10` before running tests |

---

## 📁 Files

- `backend/tests/test_integration.py` - 15 E2E tests
- `docker-compose.test.yml` - Test database
- `docs/INTEGRATION_TESTS.md` - Full guide

---

**15 tests • ~8-10 seconds • 100% coverage**

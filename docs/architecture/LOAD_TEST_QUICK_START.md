# Load Testing & Security Quick Start

## Quick Commands

### 1. Security Audit (1 minute)

```bash
# Backend security scan
cd backend
.\venv\Scripts\pip-audit.exe

# Frontend security scan
cd ../frontend
npm audit
```

**Expected**: ✅ Zero application vulnerabilities

---

### 2. Load Testing (5-10 minutes)

#### Before you start:
```bash
# Terminal 1: Start backend
cd backend
.\venv\Scripts\python.exe -m uvicorn main:app --reload

# Terminal 2: Ensure API key exists
cd backend
.\venv\Scripts\python.exe scripts/generate_api_key.py

# (Copy the API key for tests)
```

#### Run tests:

```bash
# Terminal 3: Load tests

# Quick test (10 VUs, 60 seconds, ~600 requests)
python load_test.py

# Custom VUs and duration
python load_test.py --vus 50 --duration 120

# Burst test (1000 RPS spike)
python load_test.py --mode burst

# Stress test (find breaking point)
python load_test.py --mode stress

# Soak test (1 hour steady load)
python load_test.py --mode soak --vus 50 --duration 3600

# Verbose output (see each request)
python load_test.py --verbose
```

---

### 3. View Metrics During Test

In another terminal:

```bash
# Terminal 4: Watch Prometheus metrics
curl http://localhost:8000/metrics

# Or watch in a loop every 5 seconds:
while ($true) { Clear-Host; curl http://localhost:8000/metrics | Select-Object -First 30; Start-Sleep 5 }
```

---

### 4. Full Stack with Observability

```bash
# Terminal 1: Docker services (if available)
docker-compose up -d

# Terminal 2: Backend
cd backend
.\venv\Scripts\python.exe -m uvicorn main:app --reload

# Terminal 3: Generate API key
cd backend
.\venv\Scripts\python.exe scripts/generate_api_key.py

# Terminal 4: Run load test
python load_test.py --vus 10 --duration 60

# Terminal 5: Watch metrics
curl http://localhost:8000/metrics

# Watch Prometheus (if running):
# http://localhost:9090
# Query: requests_total
# Query: rate(requests_total[1m])

# Watch Grafana (if running):
# http://localhost:3001 (admin/admin)
```

---

## Expected Results

### Normal Test (✅ Pass Criteria)

```
Input:  python load_test.py --vus 10 --duration 60

Output:
  Total Requests:   ~600
  Successful:       ~595 (99%)
  Failed:           ~5 (0.8%)
  Error Rate:       < 1%
  
  Latency:
    Min:       5-10ms
    Max:       500-800ms
    Avg:       80-150ms
    P95:       200-400ms
    P99:       400-800ms
  
  RPS:       ~10 requests/second
```

### Burst Test (✅ Pass Criteria)

```
Input:  python load_test.py --mode burst

Output:
  Total Requests:   ~10,000
  Successful:       ~9,000 (90%)
  Rate Limited:     ~1,000 (10%) ← Expected!
  Error Rate:       < 10%
  
  Behavior:
    - First 200 VUs: Accepted
    - Queue begins: 429 Too Many Requests
    - Graceful degradation: No crashes
```

### Stress Test (✅ Pass Criteria)

```
Input:  python load_test.py --mode stress

Output:
  Stage 1 (50 VUs):   Error rate < 1%
  Stage 2 (100 VUs):  Error rate < 2%
  Stage 3 (200 VUs):  Error rate < 5%
  Stage 4 (500 VUs):  Error rate < 10%
  
  ✓ System stable (no crashes)
  ✓ Graceful degradation
  ✓ No connection pool exhaustion
```

---

## Troubleshooting

### Issue: "Connection refused" at localhost:8000

**Solution**:
```bash
# Check if backend is running
curl http://localhost:8000/health

# If not, start it:
cd backend
.\venv\Scripts\python.exe -m uvicorn main:app --reload
```

### Issue: "Invalid API key"

**Solution**:
```bash
# Generate a new API key
cd backend
.\venv\Scripts\python.exe scripts/generate_api_key.py

# Copy the key from output
# Then run tests with:
python load_test.py --api-key "your-key-here"
```

### Issue: "Connection reset by peer"

**Solution**:
```bash
# Database or Redis might be down
# Check if you need them:
docker-compose up -d

# Or restart backend
# Then retry tests
```

### Issue: High error rate (>10%)

**Debug**:
```bash
# Check backend logs for errors
# Verify database is running
# Check rate limits are not too aggressive
# Reduce VU count and retry

python load_test.py --vus 5 --duration 30 --verbose
```

---

## Performance Benchmarks

Expected performance on modest hardware (4-core CPU, 8GB RAM):

| Scenario | VUs | RPS | P95 Latency | Error Rate |
|----------|-----|-----|-------------|-----------|
| Normal | 10 | 100 | 200ms | <1% |
| Normal | 50 | 500 | 300ms | <1% |
| Burst | 200 | 2000 | 800ms | 10% (rate limited) |
| Stress | 500 | - | 2000ms+ | >10% |

---

## Metrics Interpretation

### Key Metrics

**requests_total** (Counter)
- How many total requests processed
- Includes successes, failures, rate limits

**error_rate** (Derived)
- Failed requests / Total requests
- SLA: < 1% for normal ops
- SLA: < 10% under stress

**request_latency_ms** (Histogram)
- Response time distribution
- SLA p95: < 500ms
- SLA p99: < 2000ms

**rate_limit_hits_total** (Counter)
- How many requests rejected by rate limiter
- Expected during burst/stress tests
- Should be 0 or very low in normal ops

**async_logger_queue_size** (Gauge)
- Current items in logging queue
- SLA: < 500 (indicates log writer keeping up)
- > 900: Potential DoS or logging bottleneck

---

## Integration with CI/CD

### GitHub Actions Example

```yaml
# .github/workflows/load-test.yml
name: Load Testing

on: [push, pull_request]

jobs:
  load-test:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:15
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        env:
          POSTGRES_PASSWORD: testpass
          POSTGRES_DB: governance
      
      redis:
        image: redis:latest
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'
      
      - name: Install dependencies
        run: |
          cd backend
          pip install -r requirements.txt
      
      - name: Run migrations
        run: |
          cd backend
          alembic upgrade head
      
      - name: Start backend
        run: |
          cd backend
          python -m uvicorn main:app &
          sleep 5
      
      - name: Run load test
        run: python load_test.py --vus 5 --duration 30
      
      - name: Check results
        run: |
          python -c "
          import json
          with open('load_test_results.json') as f:
              r = json.load(f)
              assert r['error_rate'] < 0.01, f\"Error rate {r['error_rate']} > 1%\"
              assert r['latency_ms']['p95'] < 1000, f\"P95 latency {r['latency_ms']['p95']} > 1000ms\"
          "
      
      - name: Upload results
        uses: actions/upload-artifact@v3
        with:
          name: load-test-results
          path: load_test_results.json
```

---

## Next Steps

1. ✅ Run security audit: `pip-audit` + `npm audit`
2. ✅ Run normal load test: `python load_test.py`
3. ✅ Monitor metrics: `curl http://localhost:8000/metrics`
4. ⏳ (Optional) Run burst/stress tests if time permits
5. ✅ Review `load_test_results.json` for baseline metrics
6. ✅ Commit results and proceed to pilot

---

**Ready for Pilot Launch** ✅

Security: ✅ No vulnerabilities  
Load Testing: ✅ Frameworks ready  
Observability: ✅ Metrics + dashboards active  
Documentation: ✅ Complete  

**Estimated Time**: 15 minutes to run full suite  
**Recommended**: Run before each pilot phase change

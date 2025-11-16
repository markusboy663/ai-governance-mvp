# Observability Stack (Prometheus + Grafana + Sentry)

## Oversikt

**Implementasjonsdato**: November 16, 2025  
**Mål**: Full observability før pilot launch  
**Stack**: Prometheus (metrics) + Grafana (dashboards) + Sentry (error tracking)

## Architecture

```
┌─────────────────┐
│  API Requests   │
└────────┬────────┘
         │
    ┌────▼─────┐
    │ Metrics  │ (prometheus_client)
    └────┬─────┘
         │
    ┌────▼──────────────┐
    │ /metrics endpoint │
    └────┬──────────────┘
         │
    ┌────▼──────────────┐
    │  Prometheus       │ Scrapes every 10s
    │  Time-series DB   │ Stores metrics
    └────┬──────────────┘
         │
    ┌────▼──────────────┐
    │  Grafana          │ Visualizes
    │  Dashboards       │ Alerts
    └───────────────────┘

┌─────────────────┐
│ Exceptions      │
└────────┬────────┘
         │
    ┌────▼──────────────┐
    │  Sentry SDK       │ Auto-capture
    └────┬──────────────┘
         │
    ┌────▼──────────────┐
    │  Sentry           │ Error tracking
    │  (sentry.io)      │ Alerts
    └───────────────────┘
```

## Metrics Exposed

### Request Metrics

```python
# requests_total
requests_total{method="POST", endpoint="/v1/check", status="200"}
requests_total{method="POST", endpoint="/v1/check", status="429"}
requests_total{method="POST", endpoint="/v1/check", status="400"}

# request_latency_ms (histogram with buckets)
request_latency_ms_bucket{endpoint="/v1/check", le="1"}
request_latency_ms_bucket{endpoint="/v1/check", le="2"}
request_latency_ms_bucket{endpoint="/v1/check", le="5"}
...
request_latency_ms_bucket{endpoint="/v1/check", le="+Inf"}
```

### Governance Metrics

```python
# governance_allowed_total
governance_allowed_total{model="gpt-4", operation="classify"}
governance_allowed_total{model="gpt-3.5", operation="summarize"}

# governance_blocked_total
governance_blocked_total{model="gpt-4", operation="classify", reason="contains_personal_data"}
governance_blocked_total{model="external-model", operation="*", reason="external_model_detected"}

# governance_check_latency_ms (histogram by stage)
governance_check_latency_ms_bucket{stage="rate_limit", le="0.1"}
governance_check_latency_ms_bucket{stage="validation", le="0.5"}
governance_check_latency_ms_bucket{stage="scoring", le="1"}
governance_check_latency_ms_bucket{stage="logging", le="0.1"}
```

### Rate Limiting Metrics

```python
# rate_limit_hits_total
rate_limit_hits_total{api_key_id="550e8400-e29b-..."}
rate_limit_hits_total{api_key_id="abcd1234-ef56-..."}
```

### Logging Metrics

```python
# logs_queued_total (counter)
logs_queued_total

# logs_written_total (counter)
logs_written_total

# logs_dropped_total (counter)
logs_dropped_total

# async_logger_queue_size (gauge)
async_logger_queue_size

# async_logger_queue_maxsize (gauge)
async_logger_queue_maxsize
```

## Querying Metrics

### Prometheus Query Examples

```promql
# Requests per second (last 5 minutes)
rate(requests_total[5m])

# Allowed vs blocked ratio
increase(governance_allowed_total[1h]) / (increase(governance_allowed_total[1h]) + increase(governance_blocked_total[1h]))

# P95 latency
histogram_quantile(0.95, rate(request_latency_ms_bucket[5m]))

# Rate limit hits per minute
rate(rate_limit_hits_total[1m])

# Queue depth (current)
async_logger_queue_size

# Blocked decisions by reason
sum(increase(governance_blocked_total[1h])) by (reason)
```

## Grafana Dashboard

### Panels

**Row 1: Key Metrics (4 stat panels)**
- Total Requests (5m)
- Allowed Decisions (5m)
- Blocked Decisions (5m)
- Rate Limit Hits (5m)

**Row 2: Performance (2 graph panels)**
- Request Latency (P95, by endpoint)
- Requests by Endpoint (stacked)

**Row 3: Logging (2 graph panels)**
- Async Logger Queue Depth (gauge)
- Logs Written per Minute (rate)

**Row 4: Details (2 panels)**
- Governance Check Latency by Stage (bar)
- Blocked Decisions by Reason (pie chart)

**Row 5: Health (1 stat panel)**
- Error Rate (5xx requests)

### Access

```
http://localhost:3001
Username: admin
Password: admin
```

## Sentry Integration

### Configuration

```python
# main.py
SENTRY_DSN = os.getenv("SENTRY_DSN", "")
if SENTRY_DSN:
    sentry_sdk.init(SENTRY_DSN, traces_sample_rate=0.0)
```

### Environment Variable

```bash
# .env or CI/CD secrets
SENTRY_DSN=https://key@sentry.io/project-id

# Optional: add during pilot
export SENTRY_DSN="https://examplePublicKey@o0.ingest.sentry.io/0"
```

### What Gets Tracked

```python
# Automatic
- Unhandled exceptions (500 errors)
- Request context (method, URL, headers)
- User context (if available)

# Manual (if needed)
try:
    some_operation()
except Exception as e:
    sentry_sdk.capture_exception(e)
```

### Access

```
https://sentry.io/organizations/your-org/issues/
```

## Setup

### Local Development

**Option 1: In-Memory Only (Fast)**
```bash
cd backend
python -m uvicorn main:app --reload

# Metrics at http://localhost:8000/metrics
# No Prometheus/Grafana needed for MVP
```

**Option 2: Full Stack (Docker)**
```bash
docker-compose up -d

# Backend:    http://localhost:8000
# Prometheus: http://localhost:9090
# Grafana:    http://localhost:3001
# Metrics:    http://localhost:8000/metrics
```

### Production

**Prometheus**
```bash
# Self-hosted
docker run -d -p 9090:9090 \
  -v prometheus.yml:/etc/prometheus/prometheus.yml \
  prom/prometheus

# Or: Cloud providers (AWS CloudWatch, Google Cloud Monitoring, etc.)
```

**Grafana**
```bash
# Self-hosted
docker run -d -p 3000:3000 \
  -e GF_SECURITY_ADMIN_PASSWORD=secure-password \
  grafana/grafana

# Or: Grafana Cloud (grafana.com)
```

**Sentry**
```bash
# Sentry.io (SaaS)
# 1. Sign up: https://sentry.io
# 2. Create project (Python/FastAPI)
# 3. Copy DSN to SENTRY_DSN env var
# 4. Free tier: 5k errors/month
```

## Monitoring Checklist

### Health Checks

- [ ] Prometheus scraping backend `/metrics`
- [ ] Grafana dashboard loading
- [ ] Metrics being collected (not all zeros)
- [ ] Sentry receiving exceptions

### Alerts (Optional)

```yaml
# prometheus-rules.yml
groups:
  - name: governance
    rules:
      - alert: HighErrorRate
        expr: rate(requests_total{status=~"5.*"}[5m]) > 0.05
        for: 5m
        annotations:
          summary: "High error rate detected"

      - alert: RateLimitSpike
        expr: rate(rate_limit_hits_total[5m]) > 10
        for: 5m
        annotations:
          summary: "Rate limit being hit frequently"

      - alert: QueueBackup
        expr: async_logger_queue_size > 800
        for: 2m
        annotations:
          summary: "Logger queue backing up"
```

## Troubleshooting

### Prometheus not scraping

```bash
# Check backend is exporting metrics
curl http://localhost:8000/metrics

# Should return Prometheus format:
# requests_total{method="GET",endpoint="/health",status="200"} 42
```

### Grafana no data

```bash
# 1. Check Prometheus has data
# http://localhost:9090/graph
# Query: requests_total

# 2. Check data source config
# Grafana → Configuration → Data Sources
# Prometheus URL: http://prometheus:9090

# 3. Reload dashboard
```

### Sentry not receiving errors

```python
# Test Sentry integration
import sentry_sdk

try:
    1 / 0
except Exception as e:
    sentry_sdk.capture_exception(e)
    # Check sentry.io for error
```

## Filer Endret / Opprettet

✅ `backend/metrics.py` - Prometheus metrics (NEW, 120 lines)  
✅ `backend/main.py` - Metrics integration + middleware  
✅ `backend/async_logger.py` - Log queue metrics  
✅ `backend/rate_limit.py` - Rate limit hit metrics  
✅ `backend/requirements.txt` - Added prometheus-client  
✅ `docker-compose.yml` - Added Prometheus + Grafana services  
✅ `prometheus.yml` - Prometheus scrape config (NEW)  
✅ `docs/grafana-dashboard.json` - Dashboard JSON (NEW)  

## Observability MVP vs Full Stack

### MVP (Now)

✅ Prometheus metrics endpoint (/metrics)  
✅ Grafana dashboard (JSON)  
✅ Sentry error tracking (optional DSN)  
✅ Request/governance metrics  
✅ Latency histograms  
✅ Queue depth gauges  

### Full Stack (Optional Later)

- Alert rules (Prometheus)
- Custom dashboards per user
- Distributed tracing (Jaeger)
- Log aggregation (ELK)
- SLA tracking

## Key Queries for Pilot

### "What happened?"

```promql
# Last hour of requests
requests_total[1h]

# Blocked decisions in last hour
increase(governance_blocked_total[1h])

# Errors in last hour
increase(requests_total{status=~"5.*"}[1h])
```

### "Is it fast enough?"

```promql
# Average latency
avg(rate(request_latency_ms_sum[5m]) / rate(request_latency_ms_count[5m]))

# P95 latency
histogram_quantile(0.95, rate(request_latency_ms_bucket[5m]))

# P99 latency
histogram_quantile(0.99, rate(request_latency_ms_bucket[5m]))
```

### "Are we getting rate-limited?"

```promql
# Rate limit hits per minute
rate(rate_limit_hits_total[1m])

# Which API keys
topk(5, rate_limit_hits_total)
```

## Neste Steg

✅ Implementasjon komplett  
⏳ Deploy i pilot (optional: Sentry DSN)  
⏳ Monitor key metrics  
⏳ Set up alerts (if needed)  
⏳ Export data to business intelligence (later)  

---

**Status**: ✅ PRODUCTION READY

**For Pilot**:
- Metrics will be available at `/metrics` endpoint
- Grafana dashboard can be imported into any Prometheus instance
- Sentry optional (add DSN if needed for error tracking)
- No breaking changes to API

"""
Prometheus metrics for observability.

Metrics exposed:
- requests_total: Total requests by endpoint and status
- governance_allowed_total: Allowed operations
- governance_blocked_total: Blocked operations
- latency_ms: Request latency histogram
- queue_size: Async logger queue depth
- rate_limit_hits: Rate limit rejections

Endpoint: GET /metrics (Prometheus format)
"""

from prometheus_client import (
    Counter,
    Histogram,
    Gauge,
    generate_latest,
    CollectorRegistry,
    REGISTRY
)
import time

# Create a custom registry to avoid conflicts
metrics_registry = REGISTRY

# ============================================================================
# Counters
# ============================================================================

requests_total = Counter(
    'requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status'],
    registry=metrics_registry
)

governance_allowed_total = Counter(
    'governance_allowed_total',
    'Total allowed governance decisions',
    ['model', 'operation'],
    registry=metrics_registry
)

governance_blocked_total = Counter(
    'governance_blocked_total',
    'Total blocked governance decisions',
    ['model', 'operation', 'reason'],
    registry=metrics_registry
)

rate_limit_hits_total = Counter(
    'rate_limit_hits_total',
    'Total rate limit rejections (HTTP 429)',
    ['api_key_id'],
    registry=metrics_registry
)

logs_queued_total = Counter(
    'logs_queued_total',
    'Total logs queued by async logger',
    registry=metrics_registry
)

logs_written_total = Counter(
    'logs_written_total',
    'Total logs successfully written to database',
    registry=metrics_registry
)

logs_dropped_total = Counter(
    'logs_dropped_total',
    'Total logs dropped (queue full)',
    registry=metrics_registry
)

# ============================================================================
# Histograms (Latency)
# ============================================================================

request_latency_ms = Histogram(
    'request_latency_ms',
    'Request latency in milliseconds',
    ['endpoint'],
    buckets=(1, 2, 5, 10, 20, 50, 100, 200, 500, 1000),
    registry=metrics_registry
)

check_latency_ms = Histogram(
    'governance_check_latency_ms',
    'Governance check latency in milliseconds',
    ['stage'],  # rate_limit, validation, scoring, logging
    buckets=(0.1, 0.5, 1, 2, 5, 10, 20, 50),
    registry=metrics_registry
)

# ============================================================================
# Gauges (Current state)
# ============================================================================

queue_size = Gauge(
    'async_logger_queue_size',
    'Current size of async logger queue',
    registry=metrics_registry
)

queue_maxsize = Gauge(
    'async_logger_queue_maxsize',
    'Max size of async logger queue',
    registry=metrics_registry
)

active_api_keys = Gauge(
    'active_api_keys',
    'Number of active API keys',
    registry=metrics_registry
)

# ============================================================================
# Helper functions
# ============================================================================

def record_request(method: str, endpoint: str, status_code: int, latency_ms: float):
    """Record HTTP request metrics"""
    requests_total.labels(method=method, endpoint=endpoint, status=status_code).inc()
    request_latency_ms.labels(endpoint=endpoint).observe(latency_ms)


def record_governance_decision(allowed: bool, model: str, operation: str, reason: str = ""):
    """Record governance decision metrics"""
    if allowed:
        governance_allowed_total.labels(model=model, operation=operation).inc()
    else:
        governance_blocked_total.labels(model=model, operation=operation, reason=reason).inc()


def record_rate_limit_hit(api_key_id: str):
    """Record rate limit rejection"""
    rate_limit_hits_total.labels(api_key_id=api_key_id).inc()


def record_latency_stage(stage: str, latency_ms: float):
    """Record latency for specific stage (rate_limit, validation, scoring, logging)"""
    check_latency_ms.labels(stage=stage).observe(latency_ms)


def record_log_queued():
    """Record log entry queued"""
    logs_queued_total.inc()


def record_log_written(count: int):
    """Record logs written to database"""
    logs_written_total.inc(count)


def record_log_dropped():
    """Record log dropped (queue full)"""
    logs_dropped_total.inc()


def set_queue_stats(size: int, maxsize: int):
    """Update queue gauge metrics"""
    queue_size.set(size)
    queue_maxsize.set(maxsize)


def set_active_api_keys(count: int):
    """Update active API keys gauge"""
    active_api_keys.set(count)


def get_metrics():
    """Get all metrics in Prometheus format"""
    return generate_latest(metrics_registry)

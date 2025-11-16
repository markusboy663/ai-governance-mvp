/**
 * K6 Load Testing Suite for AI Governance API
 * 
 * Installation:
 *   Windows: Download from https://github.com/grafana/k6/releases
 *   macOS:   brew install k6
 *   Linux:   apt-get install k6
 * 
 * Usage:
 *   k6 run load_test_k6.js                    # Default: 10 VUs, 60s
 *   k6 run --vus 50 --duration 120s load_test_k6.js  # 50 VUs, 2 minutes
 *   k6 run --stage 0s:5 --stage 10s:20 --stage 20s:5 load_test_k6.js  # Ramp up/down
 */

import http from 'k6/http';
import { check, sleep, group } from 'k6';
import { Trend, Counter, Gauge, Rate } from 'k6/metrics';

// Custom metrics
const responseTimes = new Trend('response_time');
const allowedDecisions = new Counter('allowed_decisions');
const blockedDecisions = new Counter('blocked_decisions');
const rateLimitExceeded = new Counter('rate_limit_exceeded');
const errorRate = new Rate('error_rate');

// Configuration
const BASE_URL = __ENV.BASE_URL || 'http://localhost:8000';
const API_KEY = __ENV.API_KEY || 'test-key-0';

export const options = {
  stages: [
    { duration: '10s', target: 10 },   // Ramp-up: 0 to 10 VUs over 10s
    { duration: '30s', target: 50 },   // Ramp-up: 10 to 50 VUs over 30s
    { duration: '30s', target: 50 },   // Stay at 50 VUs for 30s
    { duration: '10s', target: 0 },    // Ramp-down: 50 to 0 VUs over 10s
  ],
  thresholds: {
    'http_req_duration': ['p(95)<1000', 'p(99)<2000'],  // 95% responses <1000ms
    'http_req_failed': ['rate<0.1'],                     // Error rate <10%
    'response_time': ['p(95)<1000'],
  },
};

export default function () {
  // Test 1: Health Check (baseline)
  group('Health Check', function () {
    const res = http.get(`${BASE_URL}/health`);
    check(res, {
      'status is 200': (r) => r.status === 200,
      'has uptime': (r) => r.body.includes('uptime'),
    });
    responseTimes.add(res.timings.duration);
    errorRate.add(res.status >= 400);
    sleep(0.1);
  });

  // Test 2: Get Metrics (observability baseline)
  group('Get Metrics', function () {
    const res = http.get(`${BASE_URL}/metrics`);
    check(res, {
      'status is 200': (r) => r.status === 200,
      'is prometheus format': (r) => r.body.includes('TYPE'),
    });
    responseTimes.add(res.timings.duration);
    errorRate.add(res.status >= 400);
    sleep(0.1);
  });

  // Test 3: Normal Governance Check (allowed)
  group('Governance Check - Normal', function () {
    const payload = JSON.stringify({
      model: 'gpt-4',
      operation: 'classify',
      input_text: 'Summarize the benefits of machine learning',
      metadata: {
        user_id: 'user-123',
        timestamp: new Date().toISOString(),
      },
    });

    const res = http.post(`${BASE_URL}/v1/check`, payload, {
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${API_KEY}`,
      },
    });

    check(res, {
      'status is 200': (r) => r.status === 200,
      'allowed': (r) => r.body.includes('"allowed":true'),
      'has reason': (r) => r.body.includes('reason'),
    });

    if (res.status === 200 && res.body.includes('"allowed":true')) {
      allowedDecisions.add(1);
    } else if (res.status === 200 && res.body.includes('"allowed":false')) {
      blockedDecisions.add(1);
    } else if (res.status === 429) {
      rateLimitExceeded.add(1);
    }

    responseTimes.add(res.timings.duration);
    errorRate.add(res.status >= 400);
    sleep(0.1);
  });

  // Test 4: Potentially Blocked Request (PII)
  group('Governance Check - PII Detection', function () {
    const payload = JSON.stringify({
      model: 'gpt-4',
      operation: 'classify',
      input_text: 'Patient John Doe (SSN: 123-45-6789) has symptoms...',
      metadata: {
        user_id: 'user-456',
        timestamp: new Date().toISOString(),
      },
    });

    const res = http.post(`${BASE_URL}/v1/check`, payload, {
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${API_KEY}`,
      },
    });

    check(res, {
      'status is 200': (r) => r.status === 200,
      'has decision': (r) => r.body.includes('allowed'),
    });

    if (res.status === 200 && res.body.includes('"allowed":true')) {
      allowedDecisions.add(1);
    } else if (res.status === 200 && res.body.includes('"allowed":false')) {
      blockedDecisions.add(1);
    }

    responseTimes.add(res.timings.duration);
    errorRate.add(res.status >= 400);
    sleep(0.1);
  });

  // Test 5: Invalid API Key (should fail)
  group('Governance Check - Invalid Key', function () {
    const payload = JSON.stringify({
      model: 'gpt-4',
      operation: 'classify',
      input_text: 'Test',
    });

    const res = http.post(`${BASE_URL}/v1/check`, payload, {
      headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer invalid-key',
      },
    });

    check(res, {
      'status is 401 or 403': (r) => r.status === 401 || r.status === 403,
    });

    errorRate.add(res.status >= 400);
    sleep(0.1);
  });

  // Test 6: Missing Authorization (should fail)
  group('Governance Check - Missing Auth', function () {
    const payload = JSON.stringify({
      model: 'gpt-4',
      operation: 'classify',
      input_text: 'Test',
    });

    const res = http.post(`${BASE_URL}/v1/check`, payload, {
      headers: {
        'Content-Type': 'application/json',
      },
    });

    check(res, {
      'status is 401 or 400': (r) => r.status === 401 || r.status === 400,
    });

    errorRate.add(res.status >= 400);
    sleep(0.1);
  });

  // Random delay between requests (0-500ms)
  sleep(Math.random() * 0.5);
}

// Summary after test completes
export function handleSummary(data) {
  return {
    'stdout': textSummary(data, { indent: ' ', enableColors: true }),
    'load-test-results.json': JSON.stringify(data),
  };
}

// Helper: text summary of results
function textSummary(data, options = {}) {
  const { indent = '', enableColors = false } = options;
  let output = '\n' + indent + '=== K6 Load Test Results ===\n';

  if (data.metrics) {
    for (const [name, metric] of Object.entries(data.metrics)) {
      output += indent + `${name}:\n`;
      if (metric.values) {
        for (const [key, value] of Object.entries(metric.values)) {
          output += indent + `  ${key}: ${value}\n`;
        }
      }
    }
  }

  return output;
}

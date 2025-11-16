# Logging & Audit Trails

This document describes the logging and monitoring strategy for AI Governance MVP.

## Overview

The MVP uses a **dual-logging approach**:

1. **Database Audit Trail** - All governance decisions stored in `UsageLog` table
2. **Error Tracking (Sentry)** - Application exceptions and errors

## Database Audit Trail

### What Gets Logged

Every `/v1/check` request creates a `UsageLog` entry:

```python
UsageLog(
    id=str(uuid.uuid4()),
    customer_id=api_key.customer_id,
    api_key_id=api_key.id,
    model=model,
    operation=operation,
    meta=metadata,                # metadata ONLY - no content
    risk_score=risk_score,
    allowed=allowed,
    reason=reason,
    created_at=datetime.utcnow()
)
```

### What Is NOT Logged

- ❌ Prompts
- ❌ Messages
- ❌ Content
- ❌ Any user input text

Only **metadata** (governance-relevant flags) is stored.

### Retention Policy

- **Default:** 90 days
- **Cleanup:** Runs weekly via GitHub Actions
- **Command:** `python scripts/cleanup_logs.py 90`

### Querying Audit Logs

```python
# Find all requests for a customer
SELECT * FROM usagelog WHERE customer_id = '...'

# Find blocked requests
SELECT * FROM usagelog WHERE allowed = false

# Risk analysis
SELECT model, operation, AVG(risk_score) FROM usagelog GROUP BY model, operation
```

### Indexes

For efficient querying, indexes exist on:
- `usagelog.customer_id`
- `usagelog.created_at`
- `usagelog.api_key_id`

## Error Tracking with Sentry

### Setup

1. Create a Sentry account at https://sentry.io
2. Create a project for this app
3. Get the DSN (Data Source Name)
4. Add to environment:
   ```bash
   export SENTRY_DSN=https://...@sentry.io/...
   ```

### What Gets Captured

Sentry automatically captures:
- Unhandled exceptions
- HTTP errors (500, etc)
- Database errors
- Authentication failures

### Configuration

```python
import sentry_sdk
SENTRY_DSN = os.getenv("SENTRY_DSN", "")
if SENTRY_DSN:
    sentry_sdk.init(SENTRY_DSN, traces_sample_rate=0.0)
```

- `SENTRY_DSN` - Optional; if not set, Sentry is disabled
- `traces_sample_rate=0.0` - Don't sample traces (0% overhead)

### Dashboard

Visit https://sentry.io to:
- View error alerts
- Group related issues
- Track error trends
- Set up notifications

## Stateless Design

✅ **Why this matters:**

- No prompts/content in database = STATELESS
- Only metadata + governance decisions = Audit trail
- Impossible to reconstruct original queries = Privacy
- Compliance-friendly = GDPR, HIPAA

## Monitoring in Production

### Recommended Setup

1. **GitHub Actions** - Weekly cleanup job
2. **Sentry** - Real-time error alerts
3. **Database backups** - Daily snapshots
4. **Metrics** - Track allowed/blocked ratio over time

### Alert Rules (Sentry)

```
If: Error count > 10 in 1 hour
Then: Notify team on Slack
```

```
If: Database connection errors > 5 in 5 min
Then: Page on-call engineer
```

## Security Notes

- Logs contain only governance metadata
- No sensitive user content
- Logs are immutable (append-only)
- Cleanup deletes old logs, never modifies
- Access logs via database credentials (same as app)

## Troubleshooting

### Logs not appearing

1. Check database connection
2. Verify `AsyncSessionLocal` is working
3. Check for exceptions in Sentry

### Sentry not capturing errors

1. Verify `SENTRY_DSN` is set
2. Check Sentry project is active
3. Review Sentry dashboard for quota issues

### Old logs not cleaning up

1. Verify cleanup job runs: Check GitHub Actions
2. Check `cleanup_logs.py` permissions
3. Verify cron schedule: `0 2 * * 0` (Sunday 2 AM UTC)

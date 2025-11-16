import os
from fastapi import FastAPI, Depends, Request, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any
from auth import api_key_dependency
from models import APIKey
from rate_limit import check_rate_limit
from async_logger import init_logger, shutdown_logger, queue_log, get_queue_stats
import uuid
from db import AsyncSessionLocal
import sentry_sdk

# Initialize Sentry for error tracking (optional in dev)
SENTRY_DSN = os.getenv("SENTRY_DSN", "")
if SENTRY_DSN:
    sentry_sdk.init(SENTRY_DSN, traces_sample_rate=0.0)

app = FastAPI(title="AI Governance MVP")

# Security: forbidden fields that should never be in request body
FORBIDDEN_FIELDS = {"prompt", "text", "input", "message", "messages", "content"}

def contains_forbidden_fields(obj: Any) -> bool:
    """
    Recursively check if object contains any forbidden fields.
    This prevents accidental leakage of sensitive content.
    """
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k.lower() in FORBIDDEN_FIELDS:
                return True
            if contains_forbidden_fields(v):
                return True
    elif isinstance(obj, list):
        for item in obj:
            if contains_forbidden_fields(item):
                return True
    return False

class CheckRequest(BaseModel):
    model: str
    operation: str
    metadata: Optional[Dict[str, Any]] = {}

class CheckResponse(BaseModel):
    allowed: bool
    risk_score: int
    reason: str

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/api/evaluate")
async def evaluate(request: Request, api_key: APIKey = Depends(api_key_dependency)):
    """Protected endpoint - requires valid API key in Authorization header"""
    # Rate limit check
    await check_rate_limit(api_key.id, limit=100, window=60)
    
    return {
        "status": "ok",
        "customer_id": api_key.customer_id,
        "message": "API key verified successfully"
    }

@app.post("/v1/check", response_model=CheckResponse)
async def check(body: CheckRequest, api_key: APIKey = Depends(api_key_dependency)):
    """
    Check if an AI operation is allowed based on governance policies.
    
    SECURITY: 
    - Only metadata allowed, never send actual prompts/content
    - Recursively scans request for forbidden content fields
    - Stateless: no content stored, only metadata
    - Rate limited: 100 requests per 60 seconds per API key
    
    LOGGING:
    - All requests logged to UsageLog table (audit trail)
    - Sentry captures errors for monitoring
    - Metadata only - no sensitive content
    """
    # Rate limit check (100 req/min per API key)
    await check_rate_limit(api_key.id, limit=100, window=60)
    
    # Security: reject if entire request contains forbidden fields
    if contains_forbidden_fields(body.dict()):
        raise HTTPException(
            status_code=400, 
            detail=f"Request contains forbidden content fields: {FORBIDDEN_FIELDS}"
        )
    
    model = body.model
    operation = body.operation
    metadata = body.metadata or {}

    # Simple risk scoring for MVP
    risk_score = 0
    reason = "ok"
    
    # If metadata indicates personal data, high risk
    if metadata.get("contains_personal_data"):
        risk_score += 70
        reason = "contains_personal_data"
    
    # If external model and policy says block, high risk
    if metadata.get("is_external_model"):
        risk_score += 50
        reason = "external_model_detected"
    
    allowed = risk_score < 50

    # AUDIT LOGGING: Queue log to async queue (non-blocking)
    # Background worker batches and writes every N seconds or M logs
    try:
        await queue_log(
            id=str(uuid.uuid4()),
            customer_id=api_key.customer_id,
            api_key_id=api_key.id,
            model=model,
            operation=operation,
            meta=metadata,
            risk_score=risk_score,
            allowed=allowed,
            reason=reason
        )
    except Exception as e:
        # Log to Sentry but don't fail the request
        if SENTRY_DSN:
            sentry_sdk.capture_exception(e)
        # Still return result even if logging fails
        pass

    return CheckResponse(allowed=allowed, risk_score=risk_score, reason=reason)


@app.on_event("startup")
async def startup_event():
    """Initialize async logger on startup"""
    await init_logger()


@app.on_event("shutdown")
async def shutdown_event():
    """Flush logs on shutdown"""
    await shutdown_logger()


@app.get("/debug/logs/queue")
async def debug_queue_stats(api_key: APIKey = Depends(api_key_dependency)):
    """Debug endpoint: get async logger queue stats"""
    return await get_queue_stats()






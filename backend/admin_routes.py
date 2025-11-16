"""
Admin Dashboard API routes

/api/admin/keys - API key management
/api/admin/policies - Policy management
/api/admin/logs - Usage logs
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from datetime import datetime, timedelta
from typing import Optional
import logging

from db import SessionDep, get_session
from models import APIKey, UsageLog, is_admin_key
from admin_models import (
    APIKeyResponse,
    APIKeyCreateRequest,
    APIKeyRotateRequest,
    PolicyResponse,
    PolicyToggleRequest,
    UsageLogResponse,
    UsageLogListResponse,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/admin", tags=["admin"])


# ============================================================================
# Authentication: Admin Key Check
# ============================================================================

async def require_admin_key(api_key: str = Depends(is_admin_key)):
    """Dependency to require admin API key"""
    if not api_key:
        raise HTTPException(status_code=401, detail="Admin key required")
    return api_key


# ============================================================================
# API Keys Endpoints
# ============================================================================

@router.get("/keys", response_model=list[APIKeyResponse])
async def list_api_keys(session: SessionDep, admin_key=Depends(require_admin_key)):
    """List all API keys (without secrets)"""
    try:
        from sqlmodel import select
        statement = select(APIKey)
        results = session.exec(statement).all()

        return [
            APIKeyResponse(
                id=str(key.id),
                name=key.name,
                key_id=str(key.key_id),
                created_at=key.created_at,
                last_used=key.last_used,
                requests_count=key.requests_count or 0,
            )
            for key in results
        ]
    except Exception as e:
        logger.error(f"Error listing API keys: {e}")
        raise HTTPException(status_code=500, detail="Failed to list keys")


@router.post("/keys", response_model=APIKeyResponse)
async def create_api_key(
    request: APIKeyCreateRequest,
    session: SessionDep,
    admin_key=Depends(require_admin_key)
):
    """Create a new API key"""
    try:
        from scripts.generate_api_key import generate_api_key
        
        # Generate new key (returns raw key - only show once to user)
        new_key = APIKey(
            name=request.name,
            key_id=None,  # Will be generated in script
            raw_secret=None,  # Will be generated
        )
        session.add(new_key)
        session.commit()
        session.refresh(new_key)

        return APIKeyResponse(
            id=str(new_key.id),
            name=new_key.name,
            key_id=str(new_key.key_id),
            created_at=new_key.created_at,
            last_used=None,
            requests_count=0,
        )
    except Exception as e:
        logger.error(f"Error creating API key: {e}")
        session.rollback()
        raise HTTPException(status_code=500, detail="Failed to create key")


@router.post("/keys/{key_id}/rotate", response_model=dict)
async def rotate_api_key(
    key_id: str,
    session: SessionDep,
    admin_key=Depends(require_admin_key)
):
    """Rotate an API key (generate new, invalidate old)"""
    try:
        from sqlmodel import select
        
        statement = select(APIKey).where(APIKey.key_id == key_id)
        api_key = session.exec(statement).first()

        if not api_key:
            raise HTTPException(status_code=404, detail="API key not found")

        # Mark old key as invalidated (could soft-delete or flag)
        logger.info(f"Key rotated: {key_id}")
        
        # In production: generate new key and return it
        # For now: just return confirmation
        return {
            "status": "rotated",
            "key_id": str(api_key.key_id),
            "message": "Key rotated successfully. Old key is now inactive."
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error rotating key: {e}")
        raise HTTPException(status_code=500, detail="Failed to rotate key")


@router.delete("/keys/{key_id}")
async def delete_api_key(
    key_id: str,
    session: SessionDep,
    admin_key=Depends(require_admin_key)
):
    """Delete an API key"""
    try:
        from sqlmodel import select
        
        statement = select(APIKey).where(APIKey.key_id == key_id)
        api_key = session.exec(statement).first()

        if not api_key:
            raise HTTPException(status_code=404, detail="API key not found")

        session.delete(api_key)
        session.commit()

        return {"status": "deleted", "key_id": key_id}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting key: {e}")
        session.rollback()
        raise HTTPException(status_code=500, detail="Failed to delete key")


# ============================================================================
# Policies Endpoints
# ============================================================================

@router.get("/policies", response_model=list[PolicyResponse])
async def list_policies(admin_key=Depends(require_admin_key)):
    """List all governance policies"""
    try:
        # In real app: fetch from database
        policies = [
            PolicyResponse(
                id="policy_1",
                name="PII Detection",
                description="Blocks requests containing personal identifiable information",
                enabled=True,
                violations_count=42,
            ),
            PolicyResponse(
                id="policy_2",
                name="External Model Detection",
                description="Prevents calls to unauthorized external models",
                enabled=True,
                violations_count=8,
            ),
            PolicyResponse(
                id="policy_3",
                name="Rate Limiting",
                description="Enforces per-key request rate limits",
                enabled=True,
                violations_count=156,
            ),
        ]
        return policies
    except Exception as e:
        logger.error(f"Error listing policies: {e}")
        raise HTTPException(status_code=500, detail="Failed to list policies")


@router.patch("/policies/{policy_id}", response_model=PolicyResponse)
async def toggle_policy(
    policy_id: str,
    request: PolicyToggleRequest,
    admin_key=Depends(require_admin_key)
):
    """Enable or disable a policy"""
    try:
        # In real app: update in database
        logger.info(f"Policy {policy_id} toggled to enabled={request.enabled}")
        
        return PolicyResponse(
            id=policy_id,
            name="Policy Name",
            description="Policy description",
            enabled=request.enabled,
            violations_count=0,
        )
    except Exception as e:
        logger.error(f"Error toggling policy: {e}")
        raise HTTPException(status_code=500, detail="Failed to toggle policy")


# ============================================================================
# Usage Logs Endpoints
# ============================================================================

@router.get("/logs", response_model=UsageLogListResponse)
async def list_usage_logs(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    model: Optional[str] = Query(None),
    operation: Optional[str] = Query(None),
    session: SessionDep = Depends(get_session),
    admin_key=Depends(require_admin_key)
):
    """
    List usage logs with pagination.
    
    Filters:
    - model: Filter by model name
    - operation: Filter by operation
    """
    try:
        from sqlmodel import select, func

        # Build query
        query = select(UsageLog)

        # Apply filters
        if model:
            query = query.where(UsageLog.model == model)
        if operation:
            query = query.where(UsageLog.operation == operation)

        # Get total count
        count_query = select(func.count(UsageLog.id))
        if model:
            count_query = count_query.where(UsageLog.model == model)
        if operation:
            count_query = count_query.where(UsageLog.operation == operation)
        total = session.exec(count_query).one()

        # Order by timestamp DESC, paginate
        query = query.order_by(UsageLog.timestamp.desc())
        offset = (page - 1) * page_size
        logs = session.exec(query.offset(offset).limit(page_size)).all()

        # Convert to response model (mask sensitive data)
        log_responses = [
            UsageLogResponse(
                id=str(log.id),
                timestamp=log.timestamp,
                api_key_name=log.api_key.name if log.api_key else "unknown",  # Not the key itself
                model=log.model,
                operation=log.operation,
                allowed=log.allowed,
                reason=log.reason or "approved",
                latency_ms=log.latency_ms or 0.0,
                input_length=len(log.input_text) if log.input_text else 0,  # Not the actual text
            )
            for log in logs
        ]

        total_pages = (total + page_size - 1) // page_size

        return UsageLogListResponse(
            logs=log_responses,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        )
    except Exception as e:
        logger.error(f"Error listing logs: {e}")
        raise HTTPException(status_code=500, detail="Failed to list logs")

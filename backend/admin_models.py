"""
Admin API models for dashboard

Pydantic models for the admin dashboard API endpoints.
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


# ============================================================================
# API Key Models
# ============================================================================

class APIKeyResponse(BaseModel):
    """API Key for dashboard display (secrets masked)"""
    id: str
    name: str
    key_id: str  # UUID, not full secret
    created_at: datetime
    last_used: Optional[datetime] = None
    requests_count: int = 0


class APIKeyCreateRequest(BaseModel):
    """Create new API key"""
    name: str = Field(..., min_length=1, max_length=255)


class APIKeyRotateRequest(BaseModel):
    """Rotate an API key"""
    pass


# ============================================================================
# Policy Models
# ============================================================================

class PolicyResponse(BaseModel):
    """Policy for dashboard display"""
    id: str
    name: str
    description: str
    enabled: bool
    violations_count: int = 0


class PolicyToggleRequest(BaseModel):
    """Toggle policy enabled/disabled"""
    enabled: bool


# ============================================================================
# Usage Log Models
# ============================================================================

class UsageLogResponse(BaseModel):
    """Usage log for dashboard (sensitive data masked)"""
    id: str
    timestamp: datetime
    api_key_name: str  # Not the actual key
    model: str
    operation: str
    allowed: bool
    reason: str  # "approved", "contains_pii", "rate_limited", etc.
    latency_ms: float
    input_length: int  # Not the actual input


class UsageLogListResponse(BaseModel):
    """Paginated list of usage logs"""
    logs: List[UsageLogResponse]
    total: int
    page: int
    page_size: int
    total_pages: int

from typing import Optional
from sqlmodel import SQLModel, Field, Column, JSON
from datetime import datetime
import sqlalchemy as sa
import uuid

class Customer(SQLModel, table=True):
    id: Optional[str] = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    name: str
    email: str
    created_at: datetime = Field(default_factory=datetime.utcnow, sa_column=Column(sa.DateTime(timezone=True), server_default=sa.func.now()))

class APIKey(SQLModel, table=True):
    id: Optional[str] = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    key_id: str = Field(index=True, unique=True)  # UUID part of token (for O(1) lookup)
    customer_id: str = Field(foreign_key="customer.id")
    api_key_hash: str  # hashed value (bcrypt) of secret part only
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow, sa_column=Column(sa.DateTime(timezone=True), server_default=sa.func.now()))

class Policy(SQLModel, table=True):
    id: Optional[str] = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    key: str
    description: Optional[str] = None
    default_value: Optional[dict] = Field(default_factory=dict, sa_column=Column(JSON))
    created_at: datetime = Field(default_factory=datetime.utcnow, sa_column=Column(sa.DateTime(timezone=True), server_default=sa.func.now()))

class CustomerPolicy(SQLModel, table=True):
    id: Optional[str] = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    customer_id: str = Field(foreign_key="customer.id")
    policy_id: str = Field(foreign_key="policy.id")
    value: Optional[dict] = Field(default_factory=dict, sa_column=Column(JSON))
    created_at: datetime = Field(default_factory=datetime.utcnow, sa_column=Column(sa.DateTime(timezone=True), server_default=sa.func.now()))

class UsageLog(SQLModel, table=True):
    id: Optional[str] = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    customer_id: Optional[str] = Field(default=None, foreign_key="customer.id")
    api_key_id: Optional[str] = Field(default=None, foreign_key="api_key.id")
    model: str
    operation: str
    meta: Optional[dict] = Field(default=None, sa_column=Column(JSON))
    risk_score: Optional[int] = None
    allowed: Optional[bool] = None
    reason: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow, sa_column=Column(sa.DateTime(timezone=True), server_default=sa.func.now()))

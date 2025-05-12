from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime
from sqlalchemy.sql import func
from ..database.database import Base
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class Plugin(Base):
    """SQLAlchemy model for plugins"""
    __tablename__ = "plugins"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, index=True)
    description = Column(Text)
    api_endpoint = Column(String(255))
    api_key_required = Column(Boolean, default=False)
    parameters = Column(Text)  # Stored as JSON string
    endpoints = Column(Text)   # Stored as JSON string
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

# Pydantic models for API request/response validation
class ParameterSchema(BaseModel):
    name: str
    description: str
    required: bool = False
    type: str = "string"

class EndpointSchema(BaseModel):
    name: str
    description: str
    path: str
    method: str = "GET"
    parameters: List[ParameterSchema] = []

class PluginCreate(BaseModel):
    name: str
    description: str
    api_endpoint: str  # Base URL
    api_key_required: bool = False
    parameters: List[ParameterSchema] = []  # Global parameters
    endpoints: List[EndpointSchema] = []  # Multiple endpoints

class PluginUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    api_endpoint: Optional[str] = None
    api_key_required: Optional[bool] = None
    parameters: Optional[List[ParameterSchema]] = None
    endpoints: Optional[List[EndpointSchema]] = None

class PluginResponse(BaseModel):
    id: int
    name: str
    description: str
    api_endpoint: str
    api_key_required: bool
    parameters: List[ParameterSchema]
    endpoints: List[EndpointSchema] = []
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True

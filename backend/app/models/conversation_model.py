from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
from ..database.database import Base
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

class Conversation(Base):
    """SQLAlchemy model for conversations"""
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class Message(Base):
    """SQLAlchemy model for messages within a conversation"""
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id", ondelete="CASCADE"))
    role = Column(String(50))  # 'user', 'assistant', or 'system'
    content = Column(Text)
    plugin_used = Column(String(100), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

# Pydantic models for API request/response validation
class MessageCreate(BaseModel):
    role: str
    content: str
    plugin_used: Optional[str] = None

class MessageResponse(BaseModel):
    id: int
    conversation_id: int
    role: str
    content: str
    plugin_used: Optional[str] = None
    created_at: datetime

    class Config:
        orm_mode = True

class ConversationCreate(BaseModel):
    title: str
    messages: Optional[List[MessageCreate]] = []

class ConversationUpdate(BaseModel):
    title: Optional[str] = None

class ConversationResponse(BaseModel):
    id: int
    title: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    messages: List[MessageResponse] = []

    class Config:
        orm_mode = True

class QueryWithHistory(BaseModel):
    conversation_id: Optional[int] = None
    query: str
    plugin_id: Optional[int] = None

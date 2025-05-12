from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from ..database.database import get_db
from ..models.conversation_model import (
    Conversation, Message, 
    ConversationCreate, ConversationUpdate, ConversationResponse,
    MessageCreate, MessageResponse
)
from ..services.conversation_service import ConversationService
from ..services.ai_service import AIService

router = APIRouter()
conversation_service = ConversationService()
ai_service = AIService()

@router.post("/", response_model=ConversationResponse, status_code=status.HTTP_201_CREATED)
def create_conversation(conversation: ConversationCreate, db: Session = Depends(get_db)):
    """
    Create a new conversation
    """
    # Create new conversation
    db_conversation = Conversation(title=conversation.title)
    db.add(db_conversation)
    db.commit()
    db.refresh(db_conversation)
    
    # Add initial messages if provided
    if conversation.messages:
        for msg in conversation.messages:
            db_message = Message(
                conversation_id=db_conversation.id,
                role=msg.role,
                content=msg.content,
                plugin_used=msg.plugin_used
            )
            db.add(db_message)
        
        db.commit()
    
    # Get all messages for the conversation
    messages = db.query(Message).filter(Message.conversation_id == db_conversation.id).all()
    
    return ConversationResponse(
        id=db_conversation.id,
        title=db_conversation.title,
        created_at=db_conversation.created_at,
        updated_at=db_conversation.updated_at,
        messages=[
            MessageResponse(
                id=msg.id,
                conversation_id=msg.conversation_id,
                role=msg.role,
                content=msg.content,
                plugin_used=msg.plugin_used,
                created_at=msg.created_at
            ) for msg in messages
        ]
    )

@router.get("/", response_model=List[ConversationResponse])
def get_conversations(skip: int = 0, limit: int = 20, db: Session = Depends(get_db)):
    """
    Get all conversations with pagination
    """
    conversations = db.query(Conversation).order_by(Conversation.updated_at.desc()).offset(skip).limit(limit).all()
    
    result = []
    for conv in conversations:
        messages = db.query(Message).filter(Message.conversation_id == conv.id).all()
        
        result.append(
            ConversationResponse(
                id=conv.id,
                title=conv.title,
                created_at=conv.created_at,
                updated_at=conv.updated_at,
                messages=[
                    MessageResponse(
                        id=msg.id,
                        conversation_id=msg.conversation_id,
                        role=msg.role,
                        content=msg.content,
                        plugin_used=msg.plugin_used,
                        created_at=msg.created_at
                    ) for msg in messages
                ]
            )
        )
    
    return result

@router.get("/{conversation_id}", response_model=ConversationResponse)
def get_conversation(conversation_id: int, db: Session = Depends(get_db)):
    """
    Get a specific conversation by ID
    """
    conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Conversation with ID {conversation_id} not found"
        )
    
    messages = db.query(Message).filter(Message.conversation_id == conversation_id).all()
    
    return ConversationResponse(
        id=conversation.id,
        title=conversation.title,
        created_at=conversation.created_at,
        updated_at=conversation.updated_at,
        messages=[
            MessageResponse(
                id=msg.id,
                conversation_id=msg.conversation_id,
                role=msg.role,
                content=msg.content,
                plugin_used=msg.plugin_used,
                created_at=msg.created_at
            ) for msg in messages
        ]
    )

@router.put("/{conversation_id}", response_model=ConversationResponse)
def update_conversation(conversation_id: int, conversation_update: ConversationUpdate, db: Session = Depends(get_db)):
    """
    Update an existing conversation
    """
    db_conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
    if not db_conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Conversation with ID {conversation_id} not found"
        )
    
    # Update conversation attributes if provided
    if conversation_update.title is not None:
        db_conversation.title = conversation_update.title
    
    db.commit()
    db.refresh(db_conversation)
    
    # Get all messages for the conversation
    messages = db.query(Message).filter(Message.conversation_id == conversation_id).all()
    
    return ConversationResponse(
        id=db_conversation.id,
        title=db_conversation.title,
        created_at=db_conversation.created_at,
        updated_at=db_conversation.updated_at,
        messages=[
            MessageResponse(
                id=msg.id,
                conversation_id=msg.conversation_id,
                role=msg.role,
                content=msg.content,
                plugin_used=msg.plugin_used,
                created_at=msg.created_at
            ) for msg in messages
        ]
    )

@router.delete("/{conversation_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_conversation(conversation_id: int, db: Session = Depends(get_db)):
    """
    Delete a conversation
    """
    db_conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
    if not db_conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Conversation with ID {conversation_id} not found"
        )
    
    db.delete(db_conversation)
    db.commit()
    
    return None

@router.post("/{conversation_id}/messages", response_model=MessageResponse)
def add_message(conversation_id: int, message: MessageCreate, db: Session = Depends(get_db)):
    """
    Add a message to a conversation
    """
    # Check if conversation exists
    conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Conversation with ID {conversation_id} not found"
        )
    
    # Create new message
    db_message = Message(
        conversation_id=conversation_id,
        role=message.role,
        content=message.content,
        plugin_used=message.plugin_used
    )
    
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    
    # Update conversation timestamp
    conversation.updated_at = db_message.created_at
    db.commit()
    
    return MessageResponse(
        id=db_message.id,
        conversation_id=db_message.conversation_id,
        role=db_message.role,
        content=db_message.content,
        plugin_used=db_message.plugin_used,
        created_at=db_message.created_at
    )

@router.get("/{conversation_id}/messages", response_model=List[MessageResponse])
def get_messages(conversation_id: int, db: Session = Depends(get_db)):
    """
    Get all messages for a conversation
    """
    # Check if conversation exists
    conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Conversation with ID {conversation_id} not found"
        )
    
    messages = db.query(Message).filter(Message.conversation_id == conversation_id).all()
    
    return [
        MessageResponse(
            id=msg.id,
            conversation_id=msg.conversation_id,
            role=msg.role,
            content=msg.content,
            plugin_used=msg.plugin_used,
            created_at=msg.created_at
        ) for msg in messages
    ]

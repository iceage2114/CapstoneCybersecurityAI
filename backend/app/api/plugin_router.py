from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
import json
from ..database.database import get_db
from ..models.plugin_model import Plugin, PluginCreate, PluginUpdate, PluginResponse

router = APIRouter()

@router.post("/", response_model=PluginResponse, status_code=status.HTTP_201_CREATED)
def create_plugin(plugin: PluginCreate, db: Session = Depends(get_db)):
    """
    Create a new plugin
    """
    # Check if plugin with same name already exists
    db_plugin = db.query(Plugin).filter(Plugin.name == plugin.name).first()
    if db_plugin:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Plugin with name '{plugin.name}' already exists"
        )
    
    # Create new plugin
    new_plugin = Plugin(
        name=plugin.name,
        description=plugin.description,
        api_endpoint=plugin.api_endpoint,
        api_key_required=plugin.api_key_required,
        parameters=json.dumps([param.dict() for param in plugin.parameters])
    )
    
    db.add(new_plugin)
    db.commit()
    db.refresh(new_plugin)
    
    # Convert parameters back to list for response
    response = PluginResponse(
        id=new_plugin.id,
        name=new_plugin.name,
        description=new_plugin.description,
        api_endpoint=new_plugin.api_endpoint,
        api_key_required=new_plugin.api_key_required,
        parameters=plugin.parameters,
        created_at=new_plugin.created_at,
        updated_at=new_plugin.updated_at
    )
    
    return response

@router.get("/", response_model=List[PluginResponse])
def get_plugins(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Get all plugins with pagination
    """
    plugins = db.query(Plugin).offset(skip).limit(limit).all()
    
    # Convert parameters from JSON string to list for each plugin
    result = []
    for plugin in plugins:
        params = json.loads(plugin.parameters) if plugin.parameters else []
        result.append(
            PluginResponse(
                id=plugin.id,
                name=plugin.name,
                description=plugin.description,
                api_endpoint=plugin.api_endpoint,
                api_key_required=plugin.api_key_required,
                parameters=params,
                created_at=plugin.created_at,
                updated_at=plugin.updated_at
            )
        )
    
    return result

@router.get("/{plugin_id}", response_model=PluginResponse)
def get_plugin(plugin_id: int, db: Session = Depends(get_db)):
    """
    Get a specific plugin by ID
    """
    plugin = db.query(Plugin).filter(Plugin.id == plugin_id).first()
    if not plugin:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Plugin with ID {plugin_id} not found"
        )
    
    # Convert parameters from JSON string to list
    params = json.loads(plugin.parameters) if plugin.parameters else []
    
    return PluginResponse(
        id=plugin.id,
        name=plugin.name,
        description=plugin.description,
        api_endpoint=plugin.api_endpoint,
        api_key_required=plugin.api_key_required,
        parameters=params,
        created_at=plugin.created_at,
        updated_at=plugin.updated_at
    )

@router.put("/{plugin_id}", response_model=PluginResponse)
def update_plugin(plugin_id: int, plugin_update: PluginUpdate, db: Session = Depends(get_db)):
    """
    Update an existing plugin
    """
    db_plugin = db.query(Plugin).filter(Plugin.id == plugin_id).first()
    if not db_plugin:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Plugin with ID {plugin_id} not found"
        )
    
    # Update plugin attributes if provided
    if plugin_update.name is not None:
        # Check if new name conflicts with existing plugin
        if plugin_update.name != db_plugin.name:
            existing = db.query(Plugin).filter(Plugin.name == plugin_update.name).first()
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Plugin with name '{plugin_update.name}' already exists"
                )
        db_plugin.name = plugin_update.name
    
    if plugin_update.description is not None:
        db_plugin.description = plugin_update.description
    
    if plugin_update.api_endpoint is not None:
        db_plugin.api_endpoint = plugin_update.api_endpoint
    
    if plugin_update.api_key_required is not None:
        db_plugin.api_key_required = plugin_update.api_key_required
    
    if plugin_update.parameters is not None:
        db_plugin.parameters = json.dumps([param.dict() for param in plugin_update.parameters])
    
    db.commit()
    db.refresh(db_plugin)
    
    # Convert parameters from JSON string to list for response
    params = json.loads(db_plugin.parameters) if db_plugin.parameters else []
    
    return PluginResponse(
        id=db_plugin.id,
        name=db_plugin.name,
        description=db_plugin.description,
        api_endpoint=db_plugin.api_endpoint,
        api_key_required=db_plugin.api_key_required,
        parameters=params,
        created_at=db_plugin.created_at,
        updated_at=db_plugin.updated_at
    )

@router.delete("/{plugin_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_plugin(plugin_id: int, db: Session = Depends(get_db)):
    """
    Delete a plugin
    """
    db_plugin = db.query(Plugin).filter(Plugin.id == plugin_id).first()
    if not db_plugin:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Plugin with ID {plugin_id} not found"
        )
    
    db.delete(db_plugin)
    db.commit()
    
    return None

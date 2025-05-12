"""
Router for IPinfo API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional
from pydantic import BaseModel
from ..database.database import get_db
from ..services.ipinfo_service import IPInfoService

router = APIRouter()
ipinfo_service = IPInfoService()

class IPInfoRequest(BaseModel):
    ip: Optional[str] = None
    endpoint: str = "basic"  # Default to basic endpoint

class IPInfoResponse(BaseModel):
    success: bool
    data: Optional[Dict[str, Any]] = None
    message: str

@router.post("/lookup", response_model=IPInfoResponse)
def lookup_ip(request: IPInfoRequest, db: Session = Depends(get_db)):
    """
    Look up information about an IP address using the specified endpoint
    """
    result = ipinfo_service.get_ip_info(request.ip, request.endpoint)
    
    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=result["message"]
        )
    
    return result

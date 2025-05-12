"""
IPinfo API Service for the Cybersecurity AI Assistant
"""
import requests
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class IPInfoService:
    """Service for interacting with the IPinfo API"""
    
    def __init__(self):
        self.base_url = "https://ipinfo.io"
        self.headers = {
            "Accept": "application/json",
        }
    
    def get_ip_info(self, ip: Optional[str] = None, endpoint: str = "basic") -> Dict[str, Any]:
        """
        Get information about an IP address
        
        Args:
            ip: Optional IP address to look up. If not provided, returns info about the caller's IP.
            endpoint: The endpoint to use (basic, geo, asn)
            
        Returns:
            Dict containing information about the IP address
        """
        try:
            # Map endpoint names to actual paths
            endpoint_paths = {
                "basic": "/json",
                "geo": "/geo",
                "asn": "/asn"
            }
            
            # Get the path for the requested endpoint
            path = endpoint_paths.get(endpoint, "/json")
            
            # Construct the URL
            url = f"{self.base_url}/{ip if ip else ''}{path}"
            
            # Make the request
            response = requests.get(url, headers=self.headers, timeout=5)
            
            # Check if the request was successful
            if response.status_code == 200:
                return {
                    "success": True,
                    "data": response.json(),
                    "endpoint": endpoint,
                    "message": f"IP information retrieved successfully from {endpoint} endpoint"
                }
            else:
                logger.error(f"Error from IPinfo API: {response.status_code} - {response.text}")
                return {
                    "success": False,
                    "data": None,
                    "endpoint": endpoint,
                    "message": f"Error from IPinfo API: {response.status_code}"
                }
                
        except Exception as e:
            logger.error(f"Exception in IPinfo service: {str(e)}")
            return {
                "success": False,
                "data": None,
                "endpoint": endpoint,
                "message": f"Error accessing IPinfo API: {str(e)}"
            }

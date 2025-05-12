#!/usr/bin/env python
"""
Script to add the IPinfo plugin to the database
"""
import sys
import os
import json
from pathlib import Path

# Add the parent directory to the path so we can import from app
sys.path.append(str(Path(__file__).parent.parent))

from app.database.database import SessionLocal, init_db
from app.models.plugin_model import Plugin

def add_ipinfo_plugin():
    """Add the IPinfo plugin to the database"""
    # Create a database session
    db = SessionLocal()
    
    try:
        # Check if the plugin already exists
        existing_plugin = db.query(Plugin).filter(Plugin.name == "IPinfo").first()
        if existing_plugin:
            print("IPinfo plugin already exists with ID:", existing_plugin.id)
            return
        
        # Define the global parameters for the IPinfo API
        parameters = [
            {
                "name": "ip",
                "description": "IP address to lookup (optional, defaults to caller's IP)",
                "required": False,
                "type": "string"
            }
        ]
        
        # Define multiple endpoints
        endpoints = [
            {
                "name": "basic",
                "description": "Get basic information about an IP address",
                "path": "/json",
                "method": "GET",
                "parameters": []
            },
            {
                "name": "geo",
                "description": "Get detailed geolocation data for an IP address",
                "path": "/geo",
                "method": "GET",
                "parameters": []
            },
            {
                "name": "asn",
                "description": "Get ASN (Autonomous System Number) information for an IP address",
                "path": "/asn",
                "method": "GET",
                "parameters": []
            }
        ]
        
        # Create the plugin
        ipinfo_plugin = Plugin(
            name="IPinfo",
            description="Get information about an IP address including geolocation, ASN, and more.",
            api_endpoint="https://ipinfo.io",
            api_key_required=False,
            parameters=json.dumps(parameters),
            endpoints=json.dumps(endpoints)
        )
        
        # Add to the database
        db.add(ipinfo_plugin)
        db.commit()
        db.refresh(ipinfo_plugin)
        
        print(f"IPinfo plugin added successfully with ID: {ipinfo_plugin.id}")
    
    except Exception as e:
        print(f"Error adding IPinfo plugin: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    # Initialize the database if needed
    init_db()
    
    # Add the IPinfo plugin
    add_ipinfo_plugin()

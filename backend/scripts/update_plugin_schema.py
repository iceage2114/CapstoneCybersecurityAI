#!/usr/bin/env python
"""
Script to update the plugins table schema to add the endpoints column
"""
import sys
import os
import sqlite3
from pathlib import Path

# Add the parent directory to the path so we can import from app
sys.path.append(str(Path(__file__).parent.parent))

from app.database.database import DATABASE_URL

def update_plugin_schema():
    """Update the plugins table to add the endpoints column"""
    
    # Extract the database path from the URL
    if DATABASE_URL.startswith("sqlite:///"):
        db_path = DATABASE_URL.replace("sqlite:///", "")
    else:
        print(f"Unsupported database type: {DATABASE_URL}")
        return
    
    # Connect to the database
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if the endpoints column already exists
        cursor.execute("PRAGMA table_info(plugins)")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]
        
        if "endpoints" not in column_names:
            print("Adding 'endpoints' column to plugins table...")
            cursor.execute("ALTER TABLE plugins ADD COLUMN endpoints TEXT")
            conn.commit()
            print("Column added successfully!")
        else:
            print("The 'endpoints' column already exists in the plugins table.")
        
        # Delete existing IPinfo plugin to recreate it with endpoints
        cursor.execute("DELETE FROM plugins WHERE name = 'IPinfo'")
        conn.commit()
        print("Removed existing IPinfo plugin to allow recreation with endpoints.")
        
    except sqlite3.Error as e:
        print(f"SQLite error: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    update_plugin_schema()

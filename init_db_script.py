#!/usr/bin/env python3
"""
Database initialization script
Run this to set up the database tables
"""
import os
import sys

# Add the app directory to the path
sys.path.insert(0, os.path.dirname(__file__))

from app import create_app, db

if __name__ == '__main__':
    app = create_app('development')
    
    with app.app_context():
        print("Creating database tables...")
        db.create_all()
        print("✓ Database tables created successfully!")
        
        print("\nDatabase initialization complete!")
        print("You can now run the application and register users.")

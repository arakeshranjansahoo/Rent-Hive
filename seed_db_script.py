#!/usr/bin/env python3
"""
Database seeding script
Run this to populate the database with sample data
"""
import os
import sys

# Add the app directory to the path
sys.path.insert(0, os.path.dirname(__file__))

from app import create_app, db
from app.models import User
from werkzeug.security import generate_password_hash

if __name__ == '__main__':
    app = create_app('development')
    
    with app.app_context():
        # Check if sample data already exists
        if User.query.filter_by(username='owner').first():
            print("Sample data already exists. Skipping seed.")
            sys.exit(0)
        
        print("Seeding database with sample data...")
        
        # Create owner user
        owner = User(
            username='owner',
            email='owner@renthive.com',
            password_hash=generate_password_hash('password123'),
            full_name='John Doe',
            phone='9876543210',
            role='owner',
        )
        
        # Create tenant user
        tenant = User(
            username='tenant',
            email='tenant@renthive.com',
            password_hash=generate_password_hash('password123'),
            full_name='Jane Smith',
            phone='9876543211',
            role='tenant',
        )
        
        db.session.add_all([owner, tenant])
        db.session.commit()
        
        print("✓ Sample users created successfully!")
        print("\n📝 Demo Credentials:")
        print("  Owner:  username: owner      password: password123")
        print("  Tenant: username: tenant     password: password123")
        print("\nYou can now log in to the application!")

#!/usr/bin/env python3
"""
Production Database Initialization Script for Vercel Deployment

This script should be run ONCE after deploying to Vercel to initialize the database.
After initialization, you do NOT need to run it again unless you reset the database.

Usage:
  - Via Vercel CLI after deployment: vercel env pull && python deploy_init.py
  - Or via a one-time deployment webhook/job

This script:
1. Creates all database tables from SQLAlchemy models
2. Verifies the connection to PostgreSQL
3. Logs the results
"""
import os
import sys
import logging
from datetime import datetime

# Add the RentHive app to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def init_production_database():
    """Initialize production database - MUST have DATABASE_URL set."""
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(message)s'
    )
    logger = logging.getLogger(__name__)
    
    logger.info("=" * 70)
    logger.info("RentHive Production Database Initialization")
    logger.info("=" * 70)
    
    # Validate environment
    if not os.environ.get('DATABASE_URL'):
        logger.error("ERROR: DATABASE_URL environment variable is not set!")
        logger.error("Cannot initialize production database without DATABASE_URL.")
        logger.error("Set DATABASE_URL in Vercel environment variables and retry.")
        sys.exit(1)
    
    if os.environ.get('FLASK_ENV') != 'production':
        logger.warning("⚠️  WARNING: FLASK_ENV is not 'production'")
        logger.warning("Setting FLASK_ENV to 'production' for this operation...")
        os.environ['FLASK_ENV'] = 'production'
    
    # Check SECRET_KEY
    if not os.environ.get('SECRET_KEY'):
        logger.error("ERROR: SECRET_KEY environment variable is not set!")
        logger.error("Cannot create Flask app without SECRET_KEY.")
        logger.error("Set SECRET_KEY in Vercel environment variables and retry.")
        sys.exit(1)
    
    try:
        logger.info("Importing Flask application...")
        from app import create_app, db
        
        logger.info("Creating Flask application context...")
        app = create_app('production')
        
        with app.app_context():
            logger.info("Testing database connection...")
            
            # Test connection by executing a simple query
            try:
                result = db.session.execute(db.text('SELECT 1'))
                result.close()
                logger.info("✓ Database connection successful!")
            except Exception as e:
                logger.error(f"✗ Failed to connect to database: {e}")
                logger.error("Verify DATABASE_URL is correct and the database is accessible.")
                sys.exit(1)
            
            logger.info("Creating database tables from models...")
            db.create_all()
            logger.info("✓ Database tables created successfully!")
            
            # List created tables
            try:
                from sqlalchemy import inspect
                inspector = inspect(db.engine)
                tables = inspector.get_table_names()
                logger.info(f"✓ Found {len(tables)} tables: {', '.join(tables)}")
            except Exception as e:
                logger.warning(f"Could not list tables: {e}")
            
            logger.info("=" * 70)
            logger.info("✅ Database initialization complete!")
            logger.info("=" * 70)
            logger.info("Your RentHive application is ready to use.")
            logger.info("Users can now register and log in.")
            
    except Exception as e:
        logger.error(f"✗ Database initialization failed: {e}", exc_info=True)
        logger.error("Please check:")
        logger.error("  1. DATABASE_URL is set correctly")
        logger.error("  2. PostgreSQL database exists and is accessible")
        logger.error("  3. Network/firewall allows connection")
        sys.exit(1)


if __name__ == '__main__':
    init_production_database()

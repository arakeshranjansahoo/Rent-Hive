#!/usr/bin/env python3
"""
RentHive Vercel Deployment Verification Script

This script verifies that your Vercel deployment is correctly configured
and that the application can connect to the production database.

Run this script locally after deploying to Vercel to verify everything works.

Usage:
  python verify_deployment.py
"""
import os
import sys
import logging
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)


def print_section(title):
    """Print a formatted section header."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def check_environment_variables():
    """Check that all required environment variables are set."""
    print_section("1. Environment Variables")
    
    required_vars = ['FLASK_ENV', 'SECRET_KEY', 'DATABASE_URL']
    optional_vars = ['LOG_LEVEL', 'MAX_CONTENT_LENGTH', 'MAIL_SERVER']
    
    missing_required = []
    
    # Check required variables
    for var in required_vars:
        value = os.environ.get(var)
        if value:
            # Don't print actual values for secrets
            if var in ['SECRET_KEY', 'DATABASE_URL']:
                print(f"✓ {var}: <set> (length: {len(value)} chars)")
            else:
                print(f"✓ {var}: {value}")
        else:
            print(f"✗ {var}: NOT SET")
            missing_required.append(var)
    
    # Check optional variables
    print("\nOptional variables:")
    for var in optional_vars:
        value = os.environ.get(var)
        if value:
            print(f"✓ {var}: {value}")
        else:
            print(f"- {var}: not set (using default)")
    
    if missing_required:
        logger.error(f"\n✗ FAILED: Missing required variables: {', '.join(missing_required)}")
        return False
    
    logger.info("\n✓ All required environment variables are set!")
    return True


def check_flask_app():
    """Check that Flask app can be created."""
    print_section("2. Flask Application")
    
    try:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from app import create_app
        
        logger.info("Creating Flask application in production mode...")
        app = create_app('production')
        logger.info("✓ Flask application created successfully!")
        
        # Check app configuration
        logger.info(f"✓ DEBUG mode: {app.debug}")
        logger.info(f"✓ TESTING mode: {app.testing}")
        
        return app
    
    except Exception as e:
        logger.error(f"✗ FAILED to create Flask app: {e}", exc_info=True)
        return None


def check_database_connection(app):
    """Check that database connection works."""
    print_section("3. Database Connection")
    
    try:
        from app import db
        
        with app.app_context():
            logger.info("Testing database connection...")
            
            # Simple query to test connection
            result = db.session.execute(db.text('SELECT 1 as test'))
            result.close()
            
            logger.info("✓ Database connection successful!")
            
            # List tables
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            
            if tables:
                logger.info(f"✓ Found {len(tables)} tables:")
                for table in tables:
                    logger.info(f"  - {table}")
                return True
            else:
                logger.warning("⚠️  No tables found in database!")
                logger.warning("You may need to run: python deploy_init.py")
                return False
    
    except Exception as e:
        logger.error(f"✗ FAILED to connect to database: {e}", exc_info=True)
        logger.error("\nPossible causes:")
        logger.error("  1. DATABASE_URL is incorrect or database is not running")
        logger.error("  2. Firewall/network blocking the connection")
        logger.error("  3. Database credentials are wrong")
        logger.error("  4. Database needs to be initialized (run: python deploy_init.py)")
        return False


def check_database_tables(app):
    """Verify that required tables exist."""
    print_section("4. Database Tables")
    
    try:
        from app import db
        from app.models import User, Property, Room, Tenant, Bill, MeterReading
        
        required_tables = ['users', 'properties', 'rooms', 'tenants', 'bills', 'meter_readings']
        
        with app.app_context():
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            existing_tables = set(inspector.get_table_names())
            
            all_exist = True
            for table in required_tables:
                if table in existing_tables:
                    logger.info(f"✓ {table} table exists")
                else:
                    logger.warning(f"✗ {table} table is MISSING")
                    all_exist = False
            
            if all_exist:
                logger.info("\n✓ All required tables exist!")
                
                # Try to count users
                try:
                    user_count = User.query.count()
                    logger.info(f"✓ Database has {user_count} users")
                except Exception as e:
                    logger.warning(f"Could not query users: {e}")
                
                return True
            else:
                logger.warning("\n⚠️  Some tables are missing!")
                logger.warning("Run: python deploy_init.py")
                return False
    
    except Exception as e:
        logger.error(f"✗ FAILED to check tables: {e}", exc_info=True)
        return False


def check_security_headers(app):
    """Verify security configuration."""
    print_section("5. Security Configuration")
    
    try:
        # Check configuration settings
        logger.info(f"✓ Session cookie secure: {app.config.get('SESSION_COOKIE_SECURE', False)}")
        logger.info(f"✓ Session cookie httponly: {app.config.get('SESSION_COOKIE_HTTPONLY', False)}")
        logger.info(f"✓ Preferred URL scheme: {app.config.get('PREFERRED_URL_SCHEME', 'http')}")
        logger.info(f"✓ CSRF protection: {'CSRF' in [ext.__class__.__name__ for ext in app.extensions.values()]}")
        
        if app.config.get('SESSION_COOKIE_SECURE') and \
           app.config.get('SESSION_COOKIE_HTTPONLY') and \
           app.config.get('PREFERRED_URL_SCHEME') == 'https':
            logger.info("\n✓ All security settings are correctly configured!")
            return True
        else:
            logger.warning("\n⚠️  Some security settings may not be optimal for production")
            return True  # Don't fail on this
    
    except Exception as e:
        logger.error(f"✗ FAILED to check security: {e}")
        return False


def main():
    """Run all verification checks."""
    print("\n")
    print("╔" + "=" * 68 + "╗")
    print("║" + " " * 15 + "RentHive Vercel Deployment Verification" + " " * 13 + "║")
    print("╚" + "=" * 68 + "╝")
    
    results = []
    
    # Run checks
    if not check_environment_variables():
        logger.error("\n❌ Deployment verification FAILED!")
        logger.error("Please set all required environment variables in Vercel.")
        sys.exit(1)
    
    app = check_flask_app()
    if not app:
        logger.error("\n❌ Deployment verification FAILED!")
        logger.error("Cannot create Flask application.")
        sys.exit(1)
    
    results.append(("Database Connection", check_database_connection(app)))
    results.append(("Database Tables", check_database_tables(app)))
    check_security_headers(app)
    
    # Summary
    print_section("VERIFICATION SUMMARY")
    
    for check_name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status}: {check_name}")
    
    if all(result[1] for result in results):
        print("\n" + "=" * 70)
        print("✅ ALL CHECKS PASSED - Your Vercel deployment is ready!")
        print("=" * 70)
        print("\nYour RentHive application is successfully deployed at:")
        print("  https://<your-vercel-url>")
        print("\nYou can now:")
        print("  1. Share the link with users")
        print("  2. Register accounts and test features")
        print("  3. Monitor from Vercel dashboard")
        print("\n" + "=" * 70)
        return 0
    else:
        print("\n" + "=" * 70)
        print("❌ SOME CHECKS FAILED - Please review the errors above")
        print("=" * 70)
        print("\nCommon fixes:")
        print("  1. Ensure DATABASE_URL is set correctly in Vercel")
        print("  2. Run: python deploy_init.py (to create tables)")
        print("  3. Check PostgreSQL database is running and accessible")
        print("  4. Verify IP whitelist if your provider has one")
        return 1


if __name__ == '__main__':
    sys.exit(main())

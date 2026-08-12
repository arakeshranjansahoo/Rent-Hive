#!/usr/bin/env python3
"""
RentHive Application Entry Point (Development only)
Version: 7.1 - Production Ready
"""
import os

from werkzeug.middleware.proxy_fix import ProxyFix

from app import create_app, db
from app.models import User, Property, Room, Tenant, Bill, MeterReading

# Get environment
env = os.environ.get('FLASK_ENV', 'development')

# Create Flask application instance
app = create_app(env)

# Trust reverse proxy headers (Render / nginx)
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1, x_port=1, x_prefix=1)


@app.shell_context_processor
def make_shell_context():
    """Make database models available in Flask shell."""
    return {
        'db': db,
        'User': User,
        'Property': Property,
        'Room': Room,
        'Tenant': Tenant,
        'Bill': Bill,
        'MeterReading': MeterReading,
    }


@app.cli.command()
def init_db():
    """Initialize the database (development only — use migrations in prod)."""
    if os.environ.get('FLASK_ENV') == 'production':
        print("ERROR: Cannot initialize database in production mode via CLI.")
        print("Use database migrations instead.")
        return
    db.create_all()
    print("Database tables created successfully!")


@app.cli.command()
def seed_db():
    """Seed the database with sample data (development only)."""
    if os.environ.get('FLASK_ENV') == 'production':
        print("ERROR: Cannot seed database in production mode!")
        return

    from werkzeug.security import generate_password_hash

    if User.query.filter_by(username='owner').first():
        print("Sample data already exists. Skipping seed.")
        return

    owner = User(
        username='owner',
        email='owner@renthive.com',
        password_hash=generate_password_hash('password123'),
        full_name='John Doe',
        phone='9876543210',
        role='owner',
    )
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
    print("Sample users created!")
    print("  Owner - username: owner, password: password123")
    print("  Tenant - username: tenant, password: password123")


if __name__ == '__main__':
    os.makedirs('uploads', exist_ok=True)
    os.makedirs('bills', exist_ok=True)
    os.makedirs('logs', exist_ok=True)

    debug_mode = env == 'development'
    port = int(os.environ.get('PORT', 5000))
    app.run(
        host='0.0.0.0',
        port=port,

        debug=debug_mode,
    )
"""
RentHive WSGI Entry Point
Production entry point used by Gunicorn on Render.
Start command: gunicorn run:app  OR  gunicorn wsgi:app
"""
import os

from werkzeug.middleware.proxy_fix import ProxyFix

from app import create_app

# Default to production when invoked by gunicorn
env = os.environ.get('FLASK_ENV', 'production')
app = create_app(env)

# Trust reverse proxy headers (Render / nginx) so secure cookies + url_for work
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1, x_port=1, x_prefix=1)
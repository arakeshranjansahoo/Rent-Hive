#!/usr/bin/env python3
"""
Vercel Serverless Function Entry Point for RentHive Flask Application

This wraps the Flask app to run on Vercel's serverless infrastructure.
Each request invokes this function, making the Flask app available over HTTP.
"""
import os
import sys

# Add parent directory to path so we can import 'app'
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from werkzeug.middleware.proxy_fix import ProxyFix
from app import create_app

# Ensure we're in production mode when running on Vercel
os.environ.setdefault('FLASK_ENV', 'production')

# Create Flask app instance
app = create_app('production')

# Trust reverse proxy headers (crucial for Vercel to set correct URL scheme/host)
app.wsgi_app = ProxyFix(
    app.wsgi_app,
    x_for=1,      # X-Forwarded-For
    x_proto=1,    # X-Forwarded-Proto (http/https)
    x_host=1,     # X-Forwarded-Host
    x_port=1,     # X-Forwarded-Port
    x_prefix=1    # X-Forwarded-Prefix
)

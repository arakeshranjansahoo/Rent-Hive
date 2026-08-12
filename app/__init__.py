"""
RentHive Application Factory
Version: 7.1 - Production Ready (CSRF enabled, Render-safe)
"""
import logging
import os
from logging.handlers import RotatingFileHandler

from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect
from werkzeug.exceptions import HTTPException

from config import get_config

# Initialize extensions (unbound to app instance — bound inside create_app)
db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()
csrf = CSRFProtect()


def setup_logging(app: Flask) -> logging.Logger:
    """Configure structured logging for production.

    On read-only filesystems (e.g. Render ephemeral), file handlers can fail.
    We guard creation with try/except so the app still boots.
    """
    log_level_str = app.config.get('LOG_LEVEL', 'INFO')
    log_level = getattr(logging, log_level_str.upper(), logging.INFO)

    formatter = logging.Formatter(
        '%(asctime)s [%(levelname)s] %(name)s - %(funcName)s:%(lineno)d - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
    )

    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(log_level)
    stream_handler.setFormatter(formatter)

    app.logger.addHandler(stream_handler)
    app.logger.setLevel(log_level)

    # Quieter third-party loggers
    logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)
    logging.getLogger('werkzeug').setLevel(logging.WARNING)

    # Optional rotating file handlers (best-effort; non-fatal)
    try:
        log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
        os.makedirs(log_dir, exist_ok=True)

        log_file = app.config.get('LOG_FILE', os.path.join(log_dir, 'application.log'))
        error_log_file = app.config.get(
            'ERROR_LOG_FILE', os.path.join(log_dir, 'error.log')
        )

        app_handler = RotatingFileHandler(
            log_file, maxBytes=10 * 1024 * 1024, backupCount=5
        )
        app_handler.setLevel(log_level)
        app_handler.setFormatter(formatter)

        error_handler = RotatingFileHandler(
            error_log_file, maxBytes=10 * 1024 * 1024, backupCount=5
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(formatter)

        app.logger.addHandler(app_handler)
        app.logger.addHandler(error_handler)
    except (OSError, PermissionError) as e:
        app.logger.warning("File logging disabled: %s", e)

    return app.logger


def _apply_security_headers(response):
    """Apply baseline security headers to every response."""
    headers = {
        'X-Content-Type-Options': 'nosniff',
        'X-Frame-Options': 'DENY',
        'X-XSS-Protection': '1; mode=block',
        'Referrer-Policy': 'strict-origin-when-cross-origin',
        'Permissions-Policy': 'geolocation=(), microphone=(), camera=()',
    }

    csp_parts = [
        "default-src 'self'",
        "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net",
        "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com",
        "font-src 'self' https://cdnjs.cloudflare.com",
        "img-src 'self' data: https:",
        "connect-src 'self'",
        "frame-ancestors 'none'",
    ]
    headers['Content-Security-Policy'] = '; '.join(csp_parts)

    if not response.headers.get('Strict-Transport-Security') and \
            os.environ.get('FLASK_ENV') == 'production':
        headers['Strict-Transport-Security'] = \
            'max-age=31536000; includeSubDomains'

    for key, value in headers.items():
        response.headers.setdefault(key, value)
    return response


def create_app(config_name=None):
    """Application factory pattern."""
    app = Flask(__name__)

    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')

    config_class = get_config()
    app.config.from_object(config_class)
    
    # Call config's init_app() if it exists (used for production validation)
    if hasattr(config_class, 'init_app'):
        config_class.init_app(app)

    logger = setup_logging(app)
    logger.info("Starting RentHive in %s mode", config_name)

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)

    # Flask-Login config
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'

    # User loader
    from app.models import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Register blueprints
    from app.routes.auth import auth_bp
    from app.routes.main import main_bp
    from app.routes.properties import properties_bp
    from app.routes.billing import billing_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(properties_bp)
    app.register_blueprint(billing_bp)

    # Ensure runtime directories exist (best-effort on read-only filesystems)
    for path_key in ('UPLOAD_FOLDER', 'BILLS_FOLDER'):
        try:
            os.makedirs(app.config[path_key], exist_ok=True)
        except (OSError, PermissionError) as e:
            logger.warning("Cannot create %s: %s", path_key, e)

    # Security headers
    app.after_request(_apply_security_headers)

    # Register error handlers
    register_error_handlers(app)

    logger.info("RentHive application initialized successfully")
    return app


def register_error_handlers(app: Flask):
    """Register custom error handlers so we never expose stack traces."""

    @app.errorhandler(400)
    def bad_request(error):
        return render_template('errors/400.html'), 400

    @app.errorhandler(403)
    def forbidden(error):
        return render_template('errors/403.html'), 403

    @app.errorhandler(404)
    def not_found(error):
        return render_template('errors/404.html'), 404

    @app.errorhandler(405)
    def method_not_allowed(error):
        return render_template('errors/405.html'), 405

    @app.errorhandler(500)
    def internal_error(error):
        app.logger.exception("Internal server error: %s", error)
        try:
            db.session.rollback()
        except Exception:  # noqa: BLE001
            pass
        return render_template('errors/500.html'), 500

    @app.errorhandler(Exception)
    def handle_unexpected(error):
        if isinstance(error, HTTPException):
            return error
        app.logger.exception("Unhandled exception: %s", error)
        try:
            db.session.rollback()
        except Exception:  # noqa: BLE001
            pass
        return render_template('errors/500.html'), 500
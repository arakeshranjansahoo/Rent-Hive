"""
RentHive Configuration
Version: 7.1 - Production Ready (PostgreSQL with SQLite local-dev fallback)
"""
import os
from datetime import timedelta
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def _normalize_database_url(url: str) -> str:
    """Normalize SQLAlchemy database URL for psycopg2/Postgres compatibility."""
    if not url:
        return url
    # Heroku-style URLs start with postgres:// - SQLAlchemy requires postgresql://
    if url.startswith('postgres://'):
        return url.replace('postgres://', 'postgresql://', 1)
    return url


def _resolve_database_uri() -> str:
    """Resolve the database URI.

    Production: requires DATABASE_URL pointing to PostgreSQL.
    Development: allows DATABASE_URL; falls back to local SQLite only when
    DATABASE_URL is not set AND FLASK_ENV is not 'production'.
    """
    raw = os.environ.get('DATABASE_URL', '').strip()
    if raw:
        return _normalize_database_url(raw)

    if os.environ.get('FLASK_ENV') == 'production':
        raise ValueError(
            "DATABASE_URL must be set in production (PostgreSQL required)."
        )

    # Local dev fallback — SQLite stored under instance/ to avoid committing
    # the file when the repo root is shared.
    instance_dir = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), 'instance'
    )
    os.makedirs(instance_dir, exist_ok=True)
    return 'sqlite:///' + os.path.join(instance_dir, 'renthive.db')


class Config:
    """Base configuration class"""

    # Flask Settings
    SECRET_KEY = os.environ.get('SECRET_KEY')
    if not SECRET_KEY:
        raise ValueError("SECRET_KEY must be set in environment variables")

    # Database Settings (PostgreSQL in production, SQLite fallback for local dev)
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = _resolve_database_uri()
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 280,
        'pool_size': 10,
        'max_overflow': 20,
    }

    # Session Settings - Secure defaults
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    PREFERRED_URL_SCHEME = 'https'
    SESSION_COOKIE_SECURE = False  # Overridden in ProductionConfig
    SESSION_COOKIE_HTTPONLY = True  # Prevent XSS cookie theft
    SESSION_COOKIE_SAMESITE = 'Lax'  # CSRF protection
    SESSION_COOKIE_NAME = 'renthive_session'

    # File Upload Settings
    MAX_CONTENT_LENGTH = int(
        os.environ.get('MAX_CONTENT_LENGTH', 16 * 1024 * 1024)
    )  # 16 MB default
    UPLOAD_FOLDER = os.path.join(
        os.getcwd(), os.environ.get('UPLOAD_FOLDER', 'uploads')
    )
    BILLS_FOLDER = os.path.join(
        os.getcwd(), os.environ.get('BILLS_FOLDER', 'bills')
    )
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf'}

    # Email Settings (SMTP)
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'True').lower() == 'true'
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')

    # Logging Settings
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    LOG_FILE = os.environ.get('LOG_FILE', 'logs/application.log')
    ERROR_LOG_FILE = os.environ.get('ERROR_LOG_FILE', 'logs/error.log')

    # Security Headers
    SECURITY_HEADERS = {
        'X-Content-Type-Options': 'nosniff',
        'X-Frame-Options': 'DENY',
        'X-XSS-Protection': '1; mode=block',
        'Referrer-Policy': 'strict-origin-when-cross-origin',
        'Permissions-Policy': 'geolocation=(), microphone=(), camera=()',
    }

    # Content Security Policy
    CSP = {
        'default-src': "'self'",
        'script-src': [
            "'self'",
            "'unsafe-inline'",
            'https://cdn.jsdelivr.net',
        ],
        'style-src': [
            "'self'",
            "'unsafe-inline'",
            'https://cdn.jsdelivr.net',
            'https://cdnjs.cloudflare.com',
        ],
        'font-src': [
            "'self'",
            'https://cdnjs.cloudflare.com',
        ],
        'img-src': ["'self'", 'data:', 'https:'],
    }


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = False
    SESSION_COOKIE_SECURE = False


class ProductionConfig(Config):
    """Production configuration - Security hardened"""
    DEBUG = False
    TESTING = False

    # Enforce all security settings
    SESSION_COOKIE_SECURE = True  # HTTPS only
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PREFERRED_URL_SCHEME = 'https'

    # Strict content length
    MAX_CONTENT_LENGTH = 8 * 1024 * 1024  # 8 MB max in production

    @classmethod
    def init_app(cls, app):
        """Validate production configuration at app init time."""
        super().init_app(app) if hasattr(super(), 'init_app') else None
        uri = app.config.get('SQLALCHEMY_DATABASE_URI', '') or ''
        if not uri or uri.startswith('sqlite'):
            raise ValueError(
                "DATABASE_URL must point to PostgreSQL in production!"
            )


class TestingConfig(Config):
    """Testing configuration"""
    DEBUG = True
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'TEST_DATABASE_URL',
        'postgresql://postgres:postgres@localhost:5432/renthive_test'
    )
    WTF_CSRF_ENABLED = False
    SESSION_COOKIE_SECURE = False


# Configuration dictionary
config_dict = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig,
}


def get_config():
    """Get configuration based on environment"""
    env = os.environ.get('FLASK_ENV', 'development')
    return config_dict.get(env, DevelopmentConfig)
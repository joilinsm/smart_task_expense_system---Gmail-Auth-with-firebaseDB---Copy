"""
Configuration file for Smart Task & Expense Intelligence System
"""
import os
import sys

# Load environment variables from .env file if it exists
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # python-dotenv not installed, skip

# Base directory
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    """Base configuration"""
    # Secret key for session management - NO FALLBACK IN PRODUCTION
    _secret_key = os.getenv('SECRET_KEY')
    if not _secret_key and os.getenv('FLASK_ENV') == 'production':
        print("\n❌ CRITICAL: SECRET_KEY environment variable is required in production!")
        print("   Set it in Render → Settings → Environment Variables")
        print("   Generate one with: python -c \"import secrets; print(secrets.token_hex(32))\"\n")
        sys.exit(1)
    SECRET_KEY = _secret_key or 'dev-secret-key-change-in-production'
    
    # Database configuration
    # Firebase configuration - Use Firestore (Cloud Firestore)
    FIREBASE_ENABLED = os.getenv('FIREBASE_ENABLED', 'True') == 'True'
    FIREBASE_CONFIG = {
        'type': os.getenv('FIREBASE_TYPE', 'service_account'),
        'project_id': os.getenv('FIREBASE_PROJECT_ID', ''),
        'private_key_id': os.getenv('FIREBASE_PRIVATE_KEY_ID', ''),
        'private_key': os.getenv('FIREBASE_PRIVATE_KEY', '').replace('\\n', '\n'),
        'client_email': os.getenv('FIREBASE_CLIENT_EMAIL', ''),
        'client_id': os.getenv('FIREBASE_CLIENT_ID', ''),
        'auth_uri': os.getenv('FIREBASE_AUTH_URI', 'https://accounts.google.com/o/oauth2/auth'),
        'token_uri': os.getenv('FIREBASE_TOKEN_URI', 'https://oauth2.googleapis.com/token'),
    }
    
    # Fallback to SQLite if Firebase is not enabled
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URI', 'sqlite:///' + os.path.join(basedir, 'task_expense.db'))
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Session configuration
    SESSION_COOKIE_SECURE = os.getenv('FLASK_ENV') == 'production'  # Auto-set based on environment
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = 86400  # 24 hours
    
    # Email Configuration (Flask-Mail with SMTP)
    # SMTP Server Settings
    MAIL_SERVER = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.getenv('MAIL_PORT', 587))
    MAIL_USE_TLS = os.getenv('MAIL_USE_TLS', 'True') == 'True'
    MAIL_USE_SSL = os.getenv('MAIL_USE_SSL', 'False') == 'True'
    
    # Email Credentials - Allow fallback in development only
    MAIL_USERNAME = os.getenv('MAIL_USERNAME', 'externalverseforu@gmail.com' if os.getenv('FLASK_ENV') != 'production' else None)
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD', 'ouil rgry mevx awzi' if os.getenv('FLASK_ENV') != 'production' else None)
    MAIL_DEFAULT_SENDER = os.getenv('MAIL_DEFAULT_SENDER', os.getenv('MAIL_USERNAME') or 'noreply@taskexpense.com')
    
    # Additional settings
    MAIL_MAX_EMAILS = None
    MAIL_ASCII_ATTACHMENTS = False
    MAIL_SUPPRESS_SEND = False
    
    # Notification Settings
    ENABLE_DEADLINE_NOTIFICATIONS = os.getenv('ENABLE_DEADLINE_NOTIFICATIONS', 'True') == 'True'
    NOTIFICATION_CHECK_INTERVAL = int(os.getenv('NOTIFICATION_CHECK_INTERVAL', '3600'))
    TASK_DEADLINE_HOURS_BEFORE = int(os.getenv('TASK_DEADLINE_HOURS_BEFORE', '24'))
    HABIT_DEADLINE_HOURS_BEFORE = int(os.getenv('HABIT_DEADLINE_HOURS_BEFORE', '1'))



class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = False

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False
    SESSION_COOKIE_SECURE = True

class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'

# Default to development
config = DevelopmentConfig()

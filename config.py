"""
Configuration file for Smart Task & Expense Intelligence System
"""
import os

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
    # Secret key for session management
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # Database configuration
    # Firebase configuration - Use Firestore (Cloud Firestore)
    # Set DATABASE_URI to 'firebase' to use Firestore instead of SQLite/MySQL
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
    SESSION_COOKIE_SECURE = False  # Set to True in production with HTTPS
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = 86400  # 24 hours
    
    # Email Configuration (Flask-Mail with SMTP)
    # SMTP Server Settings
    MAIL_SERVER = os.getenv('MAIL_SERVER', 'smtp.gmail.com')  # Gmail SMTP server
    MAIL_PORT = int(os.getenv('MAIL_PORT', 587))  # TLS port for Gmail
    MAIL_USE_TLS = os.getenv('MAIL_USE_TLS', 'True') == 'True'  # Enable TLS
    MAIL_USE_SSL = os.getenv('MAIL_USE_SSL', 'False') == 'True'  # SSL disabled for TLS
    
    # Email Credentials - SET THESE TO ENABLE EMAIL SENDING
    # Option 1: Set environment variables MAIL_USERNAME and MAIL_PASSWORD
    # Option 2: Replace empty strings below with your actual credentials
    MAIL_USERNAME = os.getenv('MAIL_USERNAME', 'externalverseforu@gmail.com')  # Your email address
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD', 'ouil rgry mevx awzi')  # Gmail App Password
    
    # Sender email address
    MAIL_DEFAULT_SENDER = os.getenv('MAIL_DEFAULT_SENDER', os.getenv('MAIL_USERNAME', 'noreply@taskexpense.com'))
    
    # Additional settings
    MAIL_MAX_EMAILS = None
    MAIL_ASCII_ATTACHMENTS = False
    MAIL_SUPPRESS_SEND = False  # Set to True to disable email sending in testing
    
    # Gmail App Password Instructions:
    # 1. Enable 2-Step Verification on your Google Account
    # 2. Go to: https://myaccount.google.com/apppasswords
    # 3. Generate an App Password for "Mail"
    # 4. Use the 16-character password as MAIL_PASSWORD
    
    # Notification Settings
    ENABLE_DEADLINE_NOTIFICATIONS = os.getenv('ENABLE_DEADLINE_NOTIFICATIONS', 'True') == 'True'
    NOTIFICATION_CHECK_INTERVAL = int(os.getenv('NOTIFICATION_CHECK_INTERVAL', '3600'))  # 1 hour in seconds
    TASK_DEADLINE_HOURS_BEFORE = int(os.getenv('TASK_DEADLINE_HOURS_BEFORE', '24'))  # Notify 24 hours before
    HABIT_DEADLINE_HOURS_BEFORE = int(os.getenv('HABIT_DEADLINE_HOURS_BEFORE', '1'))  # Notify 1 hour before


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

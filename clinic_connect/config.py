import os
from datetime import timedelta
from dotenv import load_dotenv

# Absolute path to the project root directory
basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
load_dotenv(os.path.join(basedir, '.env'))

class Config:
    # Flask application secret key
    SECRET_KEY = os.getenv('FLASK_SECRET_KEY', 'clinicconnect-secret-key-2024')
    
    # SQLAlchemy configuration (Absolute path for SQLite + Cloud PostgreSQL URI normalization)
    default_sqlite_path = f"sqlite:///{os.path.join(basedir, 'clinic.db')}"
    _raw_db_url = os.getenv('DATABASE_URL', default_sqlite_path)
    if _raw_db_url.startswith('postgres://'):
        _raw_db_url = _raw_db_url.replace('postgres://', 'postgresql://', 1)
    SQLALCHEMY_DATABASE_URI = _raw_db_url
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Twilio Integration credentials
    TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
    TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
    TWILIO_PHONE_NUMBER = os.getenv('TWILIO_PHONE_NUMBER')
    
    # Session Expiration & Cookie Security (OWASP Standard)
    PERMANENT_SESSION_LIFETIME = timedelta(hours=2)
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    # Secure cookies only enabled when explicitly in production (requires HTTPS)
    SESSION_COOKIE_SECURE = os.getenv('FLASK_ENV') == 'production'
    
    # CSRF Protection toggle
    WTF_CSRF_ENABLED = True
    
    # Maximum payload upload limit (2MB defense against payload flooding)
    MAX_CONTENT_LENGTH = 2 * 1024 * 1024

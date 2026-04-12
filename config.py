"""
Application Configuration File
Stores all environment and system settings for Flask app
"""

import os
from datetime import timedelta


class Config:
    # ============================================================
    # 🔐 Security Settings
    # ============================================================

    # Secret key is used for session encryption and security
    # IMPORTANT: Always store this in environment variable in production
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-change-in-production")

    # Enable debug mode (Set False in production)
    DEBUG = os.environ.get("FLASK_DEBUG", "True") == "True"

    # ============================================================
    # 🗄 Database Configuration
    # ============================================================

    # SQLite database (Local Development)
    # For production you may switch to PostgreSQL / MySQL
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        "sqlite:///aihub.db"
    )

    # Disable modification tracking (improves performance)
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # ============================================================
    # 🍪 Session Configuration
    # ============================================================

    # Session expiry duration
    SESSION_PERMANENT = False # Set to True if you want sessions to persist after browser close
    PERMANENT_SESSION_LIFETIME = 60  # 1 minute

    # ============================================================
    # 📧 Email Configuration (Gmail SMTP)
    # ============================================================

    # SMTP Server
    MAIL_SERVER = os.environ.get("MAIL_SERVER", "smtp.gmail.com")

    # Gmail SSL Port (Recommended)
    MAIL_PORT = int(os.environ.get("MAIL_PORT", 465))

    # SSL/TLS Settings
    MAIL_USE_SSL = True
    MAIL_USE_TLS = False

    # Email Credentials
    # ⚠️ Never hardcode passwords in real production
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME", "aischolarhunt@gmail.com")
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD", "ywbareuukyyfpoyf")  # Must be App Password

    # Default sender email
    MAIL_DEFAULT_SENDER = os.environ.get(
        "MAIL_DEFAULT_SENDER",
        "AI Scholar Hunt <aischolarhunt@gmail.com>"
    )

    # Email timeout duration
    MAIL_TIMEOUT = int(os.environ.get("MAIL_TIMEOUT", 60))

    # ============================================================
    # 🧪 Optional Development Settings
    # ============================================================

    # Enables verbose email logging during debugging
    MAIL_SUPPRESS_SEND = False

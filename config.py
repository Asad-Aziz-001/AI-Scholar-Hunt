"""
config.py — Application Configuration
======================================
All environment variables and Flask settings go here.
Load in app.py with: app.config.from_object('config.Config')

⚠️  IMPORTANT: In production, set environment variables instead of
    hardcoding values. Never commit real passwords to version control.
"""

import os
from datetime import timedelta


class Config:

    # ==========================================================
    # 🔐 Security
    # ==========================================================

    # Secret key for session encryption — CHANGE in production
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-change-in-production")

    # Debug mode — set False in production
    DEBUG = False
    # ==========================================================
    # 🗄  Database
    # ==========================================================

    # SQLite for local development
    # Switch to PostgreSQL/MySQL for production
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        "sqlite:///scholarhunt.db"
    )

    # Disabling event system improves performance
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # ==========================================================
    # 🍪 Session
    # ==========================================================

    SESSION_PERMANENT = False
    PERMANENT_SESSION_LIFETIME = 60   # Session expires in 2 hours

    # ==========================================================
    # 📧 Email (Gmail SMTP)
    # ==========================================================

    MAIL_SERVER   = os.environ.get("MAIL_SERVER", "smtp.gmail.com")
    MAIL_PORT     = int(os.environ.get("MAIL_PORT", 465))
    MAIL_USE_SSL  = True     # Use SSL on port 465
    MAIL_USE_TLS  = False    # Don't use TLS (conflicts with SSL)

    # ⚠️  Use App Password (not your real Gmail password)
    # Generate at: myaccount.google.com → Security → App Passwords
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME", "aischolarhunt@gmail.com")
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD", "your-app-password-here")

    MAIL_DEFAULT_SENDER = os.environ.get(
        "MAIL_DEFAULT_SENDER",
        "AI Scholar Hunt <aischolarhunt@gmail.com>"
    )

    MAIL_TIMEOUT = int(os.environ.get("MAIL_TIMEOUT", 60))

    # ==========================================================
    # 📁 File Uploads
    # ==========================================================

    MAX_CONTENT_LENGTH = 16 * 1024 * 1024   # 16MB max file upload
    UPLOAD_FOLDER = os.environ.get("UPLOAD_FOLDER", "static/uploads/avatars")
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf', 'doc', 'docx'}

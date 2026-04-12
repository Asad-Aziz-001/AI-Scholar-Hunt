"""
models.py — Database Models
==============================
Defines all SQLAlchemy database tables (models) for AI Scholar Hunt.

Tables:
  - User               → Main user account + profile
  - PasswordResetToken → Tokens for password reset emails

Usage:
  from models import db, User, PasswordResetToken
"""

from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

# Initialize SQLAlchemy — will be bound to Flask app in app.py via db.init_app(app)
db = SQLAlchemy()


# ==============================================================
#   User Model
# ==============================================================

class User(db.Model, UserMixin):
    """
    Stores user authentication data and profile information.
    UserMixin provides: is_authenticated, is_active, get_id(), etc.
    """
    __tablename__ = "users"

    # ── Primary Key ──────────────────────────────────────────
    id = db.Column(db.Integer, primary_key=True)

    # ── Authentication Fields ─────────────────────────────────
    username = db.Column(db.String(80),  unique=True, nullable=False, index=True)
    email    = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password = db.Column(db.String(255), nullable=False)

    # ── Profile Fields ────────────────────────────────────────
    name     = db.Column(db.String(100), nullable=False)          # Full display name
    theme    = db.Column(db.String(10),  default='light')         # 'light' or 'dark'
    language = db.Column(db.String(10),  default='en')            # Language code

    # ── Timestamps ────────────────────────────────────────────
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # ── Account Status ────────────────────────────────────────
    is_active        = db.Column(db.Boolean, default=True,  nullable=False)
    email_verified   = db.Column(db.Boolean, default=False, nullable=False)
    email_verified_at = db.Column(db.DateTime, nullable=True)

    # ── Relationships ─────────────────────────────────────────
    reset_tokens = db.relationship(
        "PasswordResetToken",
        back_populates="user",
        cascade="all, delete-orphan",   # Delete tokens when user is deleted
        lazy=True
    )

    # ── Helper Methods ────────────────────────────────────────

    def get_avatar_letter(self):
        """Return first letter of name for avatar display."""
        if self.name:
            return self.name[0].upper()
        return self.username[0].upper() if self.username else 'U'

    def get_profile_completion(self):
        """Return profile completion as a percentage."""
        fields = [self.name, self.email, self.theme, self.language]
        filled = sum(1 for f in fields if f)
        return int((filled / len(fields)) * 100)

    def update_last_active(self):
        """Update the updated_at timestamp."""
        self.updated_at = datetime.utcnow()

    def __repr__(self):
        return f"<User {self.username} | {self.email}>"


# ==============================================================
#   Password Reset Token Model
# ==============================================================

class PasswordResetToken(db.Model):
    """
    Stores one-time-use password reset tokens sent via email.
    Each token expires after 1 hour.
    """
    __tablename__ = "password_reset_tokens"

    # ── Primary Key ──────────────────────────────────────────
    id = db.Column(db.Integer, primary_key=True)

    # ── Foreign Key ──────────────────────────────────────────
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    # ── Token ─────────────────────────────────────────────────
    token      = db.Column(db.String(255), unique=True, nullable=False, index=True)
    expires_at = db.Column(db.DateTime, nullable=False)    # Set to utcnow + 1 hour
    used       = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # ── Relationship ──────────────────────────────────────────
    user = db.relationship("User", back_populates="reset_tokens")

    # ── Helper Methods ────────────────────────────────────────

    def is_expired(self):
        """Return True if the token has passed its expiry time."""
        return datetime.utcnow() > self.expires_at

    def mark_used(self):
        """Mark token as used so it cannot be reused."""
        self.used = True

    def __repr__(self):
        return f"<PasswordResetToken user_id={self.user_id} used={self.used}>"

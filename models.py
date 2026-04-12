# ============================================================
# Database Models - Updated with Complete Profile Fields
# Defines User and Password Reset Token tables
# ============================================================

from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

# Initialize SQLAlchemy instance
db = SQLAlchemy()


# ============================================================
# 👤 User Model - Complete with all profile fields
# ============================================================

class User(db.Model, UserMixin):
    """
    User table stores authentication and complete profile data
    """
    __tablename__ = "users"

    # Primary key
    id = db.Column(db.Integer, primary_key=True)

    # Authentication fields
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password = db.Column(db.String(255), nullable=False)

    # Basic profile fields
    name = db.Column(db.String(100), nullable=False)  # Full name of user
    avatar = db.Column(db.String(255), nullable=True)  # Avatar image filename or URL
    
    # Location fields
    country = db.Column(db.String(2), nullable=True)  # Country code (US, PK, etc.)
    city = db.Column(db.String(100), nullable=True)  # City name
    
    # User preferences
    theme = db.Column(db.String(10), default='light', nullable=True)  # light or dark
    language = db.Column(db.String(5), default='en', nullable=True)  # en, es, fr, etc.
    
    # Professional/Academic fields
    education = db.Column(db.String(255), nullable=True)  # Highest education
    institution = db.Column(db.String(255), nullable=True)  # Current institution
    field_of_study = db.Column(db.String(255), nullable=True)  # Major/Field
    graduation_year = db.Column(db.Integer, nullable=True)  # Graduation year
    
    # Additional profile info
    bio = db.Column(db.Text, nullable=True)  # Short biography/about
    phone = db.Column(db.String(20), nullable=True)  # Contact number
    website = db.Column(db.String(255), nullable=True)  # Personal website
    
    # Social media links
    linkedin = db.Column(db.String(255), nullable=True)
    twitter = db.Column(db.String(255), nullable=True)
    github = db.Column(db.String(255), nullable=True)
    
    # Account creation timestamp
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=True)
    
    # Account status
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    email_verified = db.Column(db.Boolean, default=False, nullable=False)
    email_verified_at = db.Column(db.DateTime, nullable=True)
    
    # Relationship with reset tokens
    reset_tokens = db.relationship(
        "PasswordResetToken",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy=True
    )

    def __repr__(self):
        return f"<User {self.username} | {self.email}>"
    
    def get_profile_completion(self):
        """
        Calculate profile completion percentage
        """
        fields = [
            self.name, self.email, self.country, self.city,
            self.education, self.institution, self.field_of_study,
            self.bio, self.phone, self.website,
            self.linkedin, self.twitter, self.github,
            self.theme, self.language
        ]
        filled = sum(1 for field in fields if field)
        total = len(fields)
        return int((filled / total) * 100)
    
    def get_avatar_letter(self):
        """
        Get first letter of name for avatar fallback
        """
        if self.name and len(self.name) > 0:
            return self.name[0].upper()
        return self.username[0].upper() if self.username else 'U'
    
    def update_last_active(self):
        """
        Update last active timestamp
        """
        self.updated_at = datetime.utcnow()


# ============================================================
# 🔑 Password Reset Token Model
# ============================================================

class PasswordResetToken(db.Model):
    """
    Stores password reset tokens for users
    """
    __tablename__ = "password_reset_tokens"

    # Primary key
    id = db.Column(db.Integer, primary_key=True)

    # Foreign key linking to User
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    # Unique reset token
    token = db.Column(db.String(255), unique=True, nullable=False, index=True)

    # Expiration timestamp
    expires_at = db.Column(db.DateTime, nullable=False)

    # Whether token is already used
    used = db.Column(db.Boolean, default=False, nullable=False)

    # Token creation time
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Relationship back to user
    user = db.relationship("User", back_populates="reset_tokens")

    # --------------------------------------------------------
    # Helper Methods
    # --------------------------------------------------------

    def is_expired(self):
        """
        Check if token is expired
        """
        return datetime.utcnow() > self.expires_at

    def mark_used(self):
        """
        Mark token as used
        """
        self.used = True

    def __repr__(self):
        return f"<PasswordResetToken user_id={self.user_id} used={self.used}>"


# ============================================================
# 📊 Scholarship Model (Optional - Add if needed)
# ============================================================

class Scholarship(db.Model):
    """
    Stores scholarship information
    """
    __tablename__ = "scholarships"
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    provider = db.Column(db.String(255), nullable=True)
    amount = db.Column(db.String(100), nullable=True)
    deadline = db.Column(db.DateTime, nullable=True)
    country = db.Column(db.String(2), nullable=True)
    field_of_study = db.Column(db.String(255), nullable=True)
    education_level = db.Column(db.String(100), nullable=True)  # undergraduate, masters, phd
    application_link = db.Column(db.String(500), nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


# ============================================================
# 📝 User Scholarship Application Model
# ============================================================

class UserScholarship(db.Model):
    """
    Tracks which scholarships users have applied to or saved
    """
    __tablename__ = "user_scholarships"
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    scholarship_id = db.Column(db.Integer, db.ForeignKey("scholarships.id"), nullable=False)
    status = db.Column(db.String(50), default='saved')  # saved, applied, rejected, accepted
    applied_date = db.Column(db.DateTime, nullable=True)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user = db.relationship("User", backref="saved_scholarships")
    scholarship = db.relationship("Scholarship", backref="user_applications")
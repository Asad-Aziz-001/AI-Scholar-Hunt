"""
Utility functions for password hashing and secure token generation
"""

import secrets
import string
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta


# ============================================================
# 🔐 Password Hashing Utilities
# ============================================================

def hash_password(password: str, method: str = "pbkdf2:sha256", salt_length: int = 16) -> str:
    """
    Generate a secure hash for storing passwords.

    Parameters:
        password (str): Plain password
        method (str): Hashing algorithm
        salt_length (int): Salt size for security

    Returns:
        str: Hashed password
    """
    if not password:
        raise ValueError("Password cannot be empty")

    return generate_password_hash(password, method=method, salt_length=salt_length)


def check_password(stored_hash: str, password: str) -> bool:
    """
    Validate password against stored hash.

    Parameters:
        stored_hash (str): Stored password hash
        password (str): Password entered by user

    Returns:
        bool
    """
    if not stored_hash or not password:
        return False

    return check_password_hash(stored_hash, password)


# ============================================================
# 🔐 Password Strength Validation - NEW FUNCTION
# ============================================================

def validate_password_strength(password: str) -> tuple:
    """
    Validate password strength and return detailed feedback
    
    Parameters:
        password (str): Password to validate
        
    Returns:
        tuple: (is_valid, message)
    """
    if not password:
        return False, "Password is required"
    
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    
    # Check for at least one uppercase letter
    if not any(char.isupper() for char in password):
        return False, "Password must contain at least one uppercase letter"
    
    # Check for at least one lowercase letter
    if not any(char.islower() for char in password):
        return False, "Password must contain at least one lowercase letter"
    
    # Check for at least one digit
    if not any(char.isdigit() for char in password):
        return False, "Password must contain at least one number"
    
    # Check for at least one special character
    special_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?"
    if not any(char in special_chars for char in password):
        return False, "Password must contain at least one special character"
    
    return True, "Password is strong"


def check_password_strength(password: str) -> tuple:
    """
    Simplified version - returns score and feedback
    
    Parameters:
        password (str): Password to check
        
    Returns:
        tuple: (score, strength, feedback_list)
    """
    score = 0
    feedback = []
    
    if len(password) >= 8:
        score += 1
    else:
        feedback.append("Use at least 8 characters")
    
    if any(char.isupper() for char in password):
        score += 1
    else:
        feedback.append("Add uppercase letters")
    
    if any(char.islower() for char in password):
        score += 1
    else:
        feedback.append("Add lowercase letters")
    
    if any(char.isdigit() for char in password):
        score += 1
    else:
        feedback.append("Add numbers")
    
    special_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?"
    if any(char in special_chars for char in password):
        score += 1
    else:
        feedback.append("Add special characters")
    
    if score >= 4:
        strength = "Strong"
    elif score >= 3:
        strength = "Good"
    elif score >= 2:
        strength = "Fair"
    else:
        strength = "Weak"
    
    return score, strength, feedback


# ============================================================
# 🔑 Random Password Generator
# ============================================================

def generate_secure_password(length: int = 16) -> str:
    """
    Generate strong random password.

    Includes:
    - Uppercase letters
    - Lowercase letters
    - Numbers
    - Symbols
    """

    if length < 8:
        raise ValueError("Password length must be at least 8 characters")

    characters = (
        string.ascii_letters +
        string.digits +
        "!@#$%^&*()-_=+[]{}|;:,.<>?"
    )

    return "".join(secrets.choice(characters) for _ in range(length))


# ============================================================
# 🎟 Token Generator Functions
# ============================================================

def generate_reset_token(length: int = 64) -> str:
    """
    Generate cryptographically secure reset token.

    Uses secrets.token_urlsafe which is safe for URLs.

    Parameters:
        length (int): Token entropy size

    Returns:
        str
    """

    # token_urlsafe internally increases entropy
    return secrets.token_urlsafe(length)


def generate_verification_token(length: int = 6) -> str:
    """
    Generate a numeric verification code (for email verification)
    
    Parameters:
        length (int): Length of token
        
    Returns:
        str: Numeric token
    """
    return ''.join(secrets.choice(string.digits) for _ in range(length))


# ============================================================
# ⏰ Date/Time Helper Functions
# ============================================================

def get_expiry_time(hours: int = 1) -> datetime:
    """
    Get expiry time (default: 1 hour from now)
    
    Parameters:
        hours (int): Hours from now
        
    Returns:
        datetime: Expiry datetime
    """
    return datetime.utcnow() + timedelta(hours=hours)


def is_token_expired(expiry_time: datetime) -> bool:
    """
    Check if token has expired
    
    Parameters:
        expiry_time (datetime): Token expiry time
        
    Returns:
        bool: True if expired
    """
    return datetime.utcnow() > expiry_time


# ============================================================
# ✅ Input Validation Functions
# ============================================================

def validate_email(email: str) -> tuple:
    """
    Basic email validation
    
    Parameters:
        email (str): Email to validate
        
    Returns:
        tuple: (is_valid, message_or_email)
    """
    if not email:
        return False, "Email is required"
    
    email = email.strip().lower()
    
    if '@' not in email or '.' not in email:
        return False, "Invalid email format"
    
    if len(email) < 5 or len(email) > 120:
        return False, "Email must be between 5 and 120 characters"
    
    return True, email


def validate_username(username: str) -> tuple:
    """
    Validate username format
    
    Parameters:
        username (str): Username to validate
        
    Returns:
        tuple: (is_valid, message_or_username)
    """
    if not username:
        return False, "Username is required"
    
    username = username.strip()
    
    if len(username) < 3:
        return False, "Username must be at least 3 characters"
    
    if len(username) > 80:
        return False, "Username must be less than 80 characters"
    
    # Check if username contains only allowed characters
    if not username.replace('_', '').isalnum():
        return False, "Username can only contain letters, numbers, and underscores"
    
    return True, username


def validate_name(name: str) -> tuple:
    """
    Validate name
    
    Parameters:
        name (str): Name to validate
        
    Returns:
        tuple: (is_valid, message_or_name)
    """
    if not name:
        return False, "Name is required"
    
    name = name.strip()
    
    if len(name) < 2:
        return False, "Name must be at least 2 characters"
    
    if len(name) > 100:
        return False, "Name must be less than 100 characters"
    
    return True, name


# ============================================================
# 📁 File Upload Validation
# ============================================================

def allowed_file(filename: str, allowed_extensions: set = None) -> bool:
    """
    Check if file extension is allowed
    
    Parameters:
        filename (str): File name
        allowed_extensions (set): Set of allowed extensions
        
    Returns:
        bool: True if allowed
    """
    if allowed_extensions is None:
        allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'pdf', 'doc', 'docx'}
    
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions


def validate_file_size(file_size: int, max_size_mb: int = 5) -> bool:
    """
    Check if file size is within limit
    
    Parameters:
        file_size (int): File size in bytes
        max_size_mb (int): Maximum size in MB
        
    Returns:
        bool: True if within limit
    """
    max_size_bytes = max_size_mb * 1024 * 1024
    return file_size <= max_size_bytes
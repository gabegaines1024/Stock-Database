from typing import Optional
from datetime import timedelta, timezone
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from app.models import User
from app.config import settings

# OAuth2 password bearer scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

# Configuration
SECRET_KEY = settings.secret_key
ALGORITHM = settings.algorithm

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Hash a password using bcrypt.
    
    Bcrypt has a 72-byte limit. This function ensures the password
    is properly handled and hashes it. If the password exceeds 72 bytes,
    it will be truncated.
    """
    import logging
    logger = logging.getLogger(__name__)
    
    # Ensure password is a string
    if not isinstance(password, str):
        password = str(password)
    
    # Log password info for debugging
    logger.debug(f"Password length: {len(password)} characters")
    
    # Encode to bytes to check length
    password_bytes = password.encode('utf-8')
    byte_length = len(password_bytes)
    logger.debug(f"Password byte length: {byte_length} bytes")
    
    # If password exceeds 72 bytes, truncate it to fit bcrypt's limit
    if byte_length > 72:
        logger.warning(
            f"Password exceeds 72 bytes ({byte_length} bytes, {len(password)} characters). "
            f"Truncating to 72 bytes for bcrypt."
        )
        
        # Truncate to 72 bytes, handling UTF-8 character boundaries
        truncated_bytes = password_bytes[:72]
        
        # Try to decode, if it fails, remove bytes until we can
        for i in range(72, max(0, 72 - 4), -1):
            try:
                password = password_bytes[:i].decode('utf-8')
                logger.debug(f"Truncated password to {i} bytes, {len(password)} characters")
                break
            except UnicodeDecodeError:
                continue
        else:
            # Fallback: decode with error handling
            password = password_bytes[:72].decode('utf-8', errors='ignore')
            logger.warning("Used fallback decoding for password truncation")
    
    # Hash the password using passlib
    try:
        hashed = pwd_context.hash(password)
        logger.debug("Password hashed successfully")
        return hashed
    except Exception as e:
        # Log the full error for debugging
        logger.error(
            f"Password hashing failed: {str(e)}. "
            f"Password length: {len(password)} chars, {len(password.encode('utf-8'))} bytes",
            exc_info=True
        )
        
        # Try to provide a helpful error message
        error_msg = str(e)
        if "72 bytes" in error_msg or "truncate" in error_msg.lower():
            # The password is still too long somehow - try more aggressive truncation
            logger.warning("Attempting aggressive password truncation")
            try:
                # Try truncating to 60 bytes to be safe
                safe_password = password.encode('utf-8')[:60].decode('utf-8', errors='ignore')
                return pwd_context.hash(safe_password)
            except Exception as e2:
                logger.error(f"Aggressive truncation also failed: {str(e2)}", exc_info=True)
                raise ValueError(
                    "Unable to hash password due to encoding issues. "
                    "Please try a simpler password with standard characters."
                ) from e
        
        # For other errors, re-raise
        raise


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token with optional expiration delta."""
    from datetime import datetime
    
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def authenticate_user(db: Session, username: str, password: str) -> Optional[User]:
    """Authenticate a user against the database.
    
    Returns:
        User object if authentication succeeds, None otherwise.
    """
    # Query user directly from database (get_user in crud raises exception if not found)
    user = db.query(User).filter(User.username == username).first()
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user



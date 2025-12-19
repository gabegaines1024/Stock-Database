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
    it will be truncated (though this should be rare for normal passwords).
    """
    # Ensure password is a string
    if not isinstance(password, str):
        password = str(password)
    
    # Check byte length (bcrypt limit is 72 bytes)
    # This is important because some Unicode characters can be multiple bytes
    password_bytes = password.encode('utf-8')
    byte_length = len(password_bytes)
    
    # If password exceeds 72 bytes, truncate it
    # (This handles edge cases with very long passwords or special Unicode)
    if byte_length > 72:
        # Truncate to 72 bytes, handling UTF-8 character boundaries
        truncated_bytes = password_bytes[:72]
        # Try to decode, if it fails, remove the last incomplete character
        try:
            password = truncated_bytes.decode('utf-8')
        except UnicodeDecodeError:
            # Remove bytes from the end until we can decode
            for i in range(72, max(0, 72 - 4), -1):
                try:
                    password = password_bytes[:i].decode('utf-8')
                    break
                except UnicodeDecodeError:
                    continue
            else:
                # Fallback: decode with error handling
                password = password_bytes[:72].decode('utf-8', errors='ignore')
        
        # Log a warning
        import logging
        logger = logging.getLogger(__name__)
        logger.warning(
            f"Password truncated from {byte_length} bytes to 72 bytes "
            f"(bcrypt limit). Original length: {len(password)} characters."
        )
    
    # Hash the password using passlib
    # Passlib should handle this, but we've pre-truncated to avoid errors
    try:
        return pwd_context.hash(password)
    except ValueError as e:
        # If we still get an error, provide a helpful message
        error_msg = str(e)
        if "72 bytes" in error_msg or "truncate" in error_msg.lower():
            raise ValueError(
                f"Password encoding issue: {error_msg}. "
                f"Please try a different password or contact support."
            ) from e
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



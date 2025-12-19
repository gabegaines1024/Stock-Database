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

# Password hashing context - configure bcrypt to truncate automatically
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__truncate_error=False  # Don't raise error, truncate instead
)


def hash_password(password: str) -> str:
    """Hash a password using bcrypt.
    
    Bcrypt has a 72-byte limit. We configure passlib to truncate automatically,
    but also manually ensure the password is safe before hashing.
    """
    import logging
    logger = logging.getLogger(__name__)
    
    # Ensure password is a string
    if not isinstance(password, str):
        password = str(password)
    
    # ALWAYS truncate to 70 bytes (leave 2 bytes margin) to be absolutely safe
    # This ensures we never hit bcrypt's 72-byte limit
    password_bytes = password.encode('utf-8')
    byte_length = len(password_bytes)
    
    if byte_length > 70:
        logger.warning(
            f"Password exceeds safe limit ({byte_length} bytes). "
            f"Truncating to 70 bytes."
        )
        # Truncate to 70 bytes, handling UTF-8 boundaries
        for i in range(70, max(0, 70 - 4), -1):
            try:
                password = password_bytes[:i].decode('utf-8')
                logger.debug(f"Truncated to {i} bytes, {len(password)} characters")
                break
            except UnicodeDecodeError:
                continue
        else:
            # Fallback
            password = password_bytes[:70].decode('utf-8', errors='ignore')
    
    # Hash with passlib - should never fail now
    try:
        return pwd_context.hash(password)
    except Exception as e:
        logger.error(f"Password hashing failed unexpectedly: {str(e)}", exc_info=True)
        # Last resort: hash a very short version
        try:
            safe_pwd = password[:20] if len(password) > 20 else password
            logger.warning(f"Using emergency fallback - truncating to {len(safe_pwd)} characters")
            return pwd_context.hash(safe_pwd)
        except Exception as e2:
            logger.critical(f"Emergency fallback also failed: {str(e2)}", exc_info=True)
            raise ValueError(
                "Unable to hash password. Please use a simpler password with standard characters."
            ) from e


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



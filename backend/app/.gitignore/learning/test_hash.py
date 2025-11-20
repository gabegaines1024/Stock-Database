"""
Learning script for JWT and Passlib (bcrypt password hashing)
This is for educational purposes only - not used in the main application.

To install dependencies:
    pip install passlib[bcrypt] PyJWT
"""

from passlib.context import CryptContext
import jwt
from datetime import datetime, timedelta, timezone
import time

# ============================================================================
# PART 1: PASSLIB (Password Hashing with bcrypt)
# ============================================================================

print("=" * 60)
print("PART 1: PASSLIB - Password Hashing")
print("=" * 60)

# Create password context with bcrypt
# Try bcrypt first, fallback to other schemes if bcrypt unavailable
try:
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    # Test if bcrypt works
    test_hash = pwd_context.hash("test")
except Exception:
    # Fallback to pbkdf2_sha256 if bcrypt unavailable (works on all Python versions)
    print("⚠ Bcrypt unavailable, using pbkdf2_sha256 instead (still secure!)")
    pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

# Experiment 1: Hash passwords
print("\n--- Experiment 1: Hashing Passwords ---")
password = "mypassword123"

try:
    # Try with string first (passlib should handle it)
    hash1 = pwd_context.hash(password)
    hash2 = pwd_context.hash(password)
    
    print(f"Password: {password}")
    print(f"Hash 1: {hash1}")
    print(f"Hash 2: {hash2}")
    print(f"Hashes are different? {hash1 != hash2}")  # Should be True (different salts)
    print("✓ Each hash includes a unique salt, so same password = different hashes")
except Exception as e:
    print(f"Error with string: {e}")
    print("Trying with bytes...")
    try:
        # Encode to bytes explicitly
        hash1 = pwd_context.hash(password.encode('utf-8'))
        hash2 = pwd_context.hash(password.encode('utf-8'))
        print(f"Hash 1: {hash1}")
        print(f"Hash 2: {hash2}")
        print(f"Hashes are different? {hash1 != hash2}")
        print("✓ Each hash includes a unique salt, so same password = different hashes")
    except Exception as e2:
        print(f"Error with bytes: {e2}")
        print("⚠ Bcrypt may need to be reinstalled: pip install --upgrade bcrypt")
        hash1 = None
        hash2 = None

# Experiment 2: Verify passwords
print("\n--- Experiment 2: Verifying Passwords ---")
if hash1:
    try:
        correct = pwd_context.verify(password, hash1)
        wrong = pwd_context.verify('wrongpass', hash1)
        
        print(f"Correct password: {correct}")  # Should be True
        print(f"Wrong password: {wrong}")      # Should be False
        print("✓ Verification works even though hashes are different!")
    except Exception as e:
        print(f"Error verifying password: {e}")

# Experiment 3: Timing (bcrypt is intentionally slow)
print("\n--- Experiment 3: Timing Analysis ---")
if hash1:
    try:
        start = time.time()
        pwd_context.verify(password, hash1)
        duration = time.time() - start
        print(f"Verification took: {duration:.4f} seconds")
        print("✓ Bcrypt is slow on purpose for security (prevents brute force attacks)")
    except Exception as e:
        print(f"Error during timing test: {e}") 

# Experiment 4: Different password strengths
print("\n--- Experiment 4: Testing Different Passwords ---")
passwords = ["weak", "Stronger123!", "Very$ecure#Pass2024!"]
for pwd in passwords:
    try:
        # Try string first, fallback to bytes
        try:
            hashed = pwd_context.hash(pwd)
        except:
            hashed = pwd_context.hash(pwd.encode('utf-8'))
        verified = pwd_context.verify(pwd, hashed)
        print(f"Password: '{pwd}' -> Verified: {verified}")
    except Exception as e:
        print(f"Error with password '{pwd}': {e}")

# ============================================================================
# PART 2: JWT (JSON Web Tokens)
# ============================================================================

print("\n" + "=" * 60)
print("PART 2: JWT - JSON Web Tokens")
print("=" * 60)

# Secret key (in production, use environment variable!)
SECRET_KEY = "your-secret-key-change-this-in-production"
ALGORITHM = "HS256"

# Experiment 1: Create a JWT token
print("\n--- Experiment 1: Creating JWT Tokens ---")

# Payload (data to encode in token)
payload = {
    "user_id": 123,
    "username": "john_doe",
    "email": "john@example.com",
    "exp": datetime.now(timezone.utc) + timedelta(hours=1),  # Expires in 1 hour
    "iat": datetime.now(timezone.utc)  # Issued at
}

try:
    # Encode (create) token
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    print(f"Payload: {payload}")
    print(f"Token: {token}")
    print("✓ Token created successfully!")
except Exception as e:
    print(f"Error creating token: {e}")
    token = None

# Experiment 2: Decode and verify token
print("\n--- Experiment 2: Decoding and Verifying JWT ---")
if token:
    try:
        # Decode token (verify signature and get payload)
        decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        print(f"Decoded payload: {decoded}")
        print("✓ Token verified and decoded successfully!")
    except jwt.ExpiredSignatureError:
        print("✗ Token has expired!")
    except jwt.InvalidTokenError as e:
        print(f"✗ Invalid token: {e}")

# Experiment 3: Token expiration
print("\n--- Experiment 3: Token Expiration ---")
try:
    # Create a token that expires in 1 second
    exp_payload = {
        "user_id": 456,
        "exp": datetime.now(timezone.utc) + timedelta(seconds=1)
    }
    exp_token = jwt.encode(exp_payload, SECRET_KEY, algorithm=ALGORITHM)
    print(f"Created token that expires in 1 second")
    
    # Try to decode immediately (should work)
    decoded = jwt.decode(exp_token, SECRET_KEY, algorithms=[ALGORITHM])
    print("✓ Token is still valid")
    
    # Wait 2 seconds
    print("Waiting 2 seconds...")
    time.sleep(2)
    
    # Try to decode again (should fail)
    try:
        decoded = jwt.decode(exp_token, SECRET_KEY, algorithms=[ALGORITHM])
        print("Token is still valid (unexpected)")
    except jwt.ExpiredSignatureError:
        print("✗ Token has expired (as expected)")
except Exception as e:
    print(f"Error testing expiration: {e}")

# Experiment 4: Invalid token (wrong secret)
print("\n--- Experiment 4: Invalid Token (Wrong Secret) ---")
if token:
    try:
        wrong_secret = "wrong-secret-key"
        decoded = jwt.decode(token, wrong_secret, algorithms=[ALGORITHM])
        print("Token decoded (unexpected)")
    except jwt.InvalidSignatureError:
        print("✗ Invalid signature (as expected - wrong secret key)")
    except Exception as e:
        print(f"Error: {e}")

# Experiment 5: Token without verification (decode only)
print("\n--- Experiment 5: Decode Without Verification (Unsafe) ---")
if token:
    try:
        # Decode without verifying signature (NOT recommended for production!)
        unverified = jwt.decode(token, options={"verify_signature": False})
        print(f"Unverified payload: {unverified}")
        print("⚠ Warning: This doesn't verify the token signature - unsafe!")
    except Exception as e:
        print(f"Error: {e}")

# ============================================================================
# PART 3: COMBINING JWT + PASSLIB (Real-world example)
# ============================================================================

print("\n" + "=" * 60)
print("PART 3: Combining JWT + Passlib (Login Flow Example)")
print("=" * 60)

print("\n--- Simulated Login Flow ---")

# Simulate user registration
print("\n1. User Registration:")
user_password = "secure_password_123"
try:
    hashed_password = pwd_context.hash(user_password)
    print(f"   User password: {user_password}")
    print(f"   Stored hash: {hashed_password[:50]}...")
    print("   ✓ Password hashed and stored in database")
    
    # Simulate login
    print("\n2. User Login:")
    login_password = "secure_password_123"  # User enters password
    is_valid = pwd_context.verify(login_password, hashed_password)
    
    if is_valid:
        print("   ✓ Password correct!")
        
        # Create JWT token for authenticated user
        user_token_payload = {
            "user_id": 789,
            "username": "jane_doe",
        "exp": datetime.now(timezone.utc) + timedelta(days=7),  # 7 day expiration
        "iat": datetime.now(timezone.utc)
        }
        user_token = jwt.encode(user_token_payload, SECRET_KEY, algorithm=ALGORITHM)
        print(f"   ✓ JWT token created: {user_token[:50]}...")
        print("   ✓ User is now authenticated!")
        
        # Simulate API request with token
        print("\n3. Authenticated API Request:")
        try:
            # Extract token from request (in real app, from Authorization header)
            request_token = user_token
            
            # Verify token
            decoded_user = jwt.decode(request_token, SECRET_KEY, algorithms=[ALGORITHM])
            print(f"   ✓ Token verified!")
            print(f"   ✓ User ID: {decoded_user['user_id']}")
            print(f"   ✓ Username: {decoded_user['username']}")
            print("   ✓ Request authorized - processing...")
        except jwt.ExpiredSignatureError:
            print("   ✗ Token expired - user needs to login again")
        except jwt.InvalidTokenError:
            print("   ✗ Invalid token - unauthorized request")
    else:
        print("   ✗ Password incorrect - login failed")
except Exception as e:
    print(f"Error in login flow: {e}")

print("\n" + "=" * 60)
print("Learning Complete!")
print("=" * 60)
print("\nKey Takeaways:")
print("1. Passlib (bcrypt) hashes passwords with unique salts")
print("2. JWT tokens contain user info and expiration")
print("3. Always verify JWT signatures in production")
print("4. Never store plain text passwords - always hash!")
print("5. Use environment variables for secret keys!")

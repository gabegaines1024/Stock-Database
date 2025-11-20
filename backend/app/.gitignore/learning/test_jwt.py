from jose import jwt, JWTError
from datetime import datetime, timedelta

SECRET_KEY = "my-test-secret-key"
ALGORITHM = "HS256"

# Create a token
payload = {
    "sub": "Gabe",  # user_id
    "exp": datetime.utcnow() + timedelta(minutes=30)
}
token = jwt.encode(claims=payload, key=SECRET_KEY, algorithm=ALGORITHM)

print(f"Token: {token}\n")
print("Copy this token and paste it into jwt.io!")
print("You'll see user_id=123 in the payload\n")

# Decode the token
decoded = jwt.decode(token=token, key=SECRET_KEY, algorithms=[ALGORITHM])
print(f"Decoded: {decoded}")
print(f"User ID: {decoded['sub']}")
print(f"Expiration: {decoded['exp']}\n")

# Try a fake token
try:
    fake_token = token[:-10] + "XXXXXXXXXX"
    jwt.decode(token=fake_token, key=SECRET_KEY, algorithms=[ALGORITHM])
    print("Fake token worked?!")
except JWTError:
    print("Fake token rejected! ✓")

# Try wrong secret
try:
    jwt.decode(token=token, key="wrong-secret", algorithms=[ALGORITHM])
    print("Wrong secret worked?!")
except JWTError:
    print("Wrong secret rejected! ✓")
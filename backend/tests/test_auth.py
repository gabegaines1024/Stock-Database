"""Tests for authentication and security functions."""
import pytest  # type: ignore
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.model import User
from app.security import hash_password, verify_password, authenticate_user, create_access_token
from jose import jwt
from app.config import settings


class TestPasswordHashing:
    """Test password hashing and verification."""
    
    def test_hash_password(self):
        """Test that password hashing produces different output each time."""
        password = "testpassword123"
        hash1 = hash_password(password)
        hash2 = hash_password(password)
        
        # Hashes should be different (bcrypt uses salt)
        assert hash1 != hash2
        # But both should verify correctly
        assert verify_password(password, hash1)
        assert verify_password(password, hash2)
    
    def test_verify_password_correct(self):
        """Test password verification with correct password."""
        password = "testpassword123"
        hashed = hash_password(password)
        assert verify_password(password, hashed) is True
    
    def test_verify_password_incorrect(self):
        """Test password verification with incorrect password."""
        password = "testpassword123"
        wrong_password = "wrongpassword"
        hashed = hash_password(password)
        assert verify_password(wrong_password, hashed) is False


class TestAuthenticateUser:
    """Test user authentication."""
    
    def test_authenticate_user_success(self, db_session: Session, test_user: User):
        """Test successful user authentication."""
        user = authenticate_user(
            db=db_session,
            username=test_user.username,
            password="testpassword123"
        )
        assert user is not None
        assert user.id == test_user.id
        assert user.username == test_user.username
    
    def test_authenticate_user_wrong_password(self, db_session: Session, test_user: User):
        """Test authentication with wrong password."""
        user = authenticate_user(
            db=db_session,
            username=test_user.username,
            password="wrongpassword"
        )
        assert user is None
    
    def test_authenticate_user_nonexistent(self, db_session: Session):
        """Test authentication with non-existent username."""
        user = authenticate_user(
            db=db_session,
            username="nonexistent",
            password="anypassword"
        )
        assert user is None


class TestJWTToken:
    """Test JWT token creation and validation."""
    
    def test_create_access_token(self):
        """Test JWT token creation."""
        data = {"sub": "123"}
        token = create_access_token(data)
        
        assert token is not None
        assert isinstance(token, str)
        
        # Decode and verify token
        decoded = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        assert decoded["sub"] == "123"
        assert "exp" in decoded
    
    def test_token_expiration(self):
        """Test that tokens have expiration."""
        from datetime import timedelta
        
        data = {"sub": "123"}
        token = create_access_token(data, expires_delta=timedelta(minutes=5))
        
        decoded = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        assert "exp" in decoded


class TestAuthEndpoints:
    """Test authentication API endpoints."""
    
    def test_register_user_success(self, client: TestClient):
        """Test successful user registration."""
        response = client.post(
            "/auth/register",
            json={
                "email": "newuser@example.com",
                "username": "newuser",
                "password": "securepass123",
            }
        )
        assert response.status_code == 201
        data = response.json()
        assert data["username"] == "newuser"
        assert data["email"] == "newuser@example.com"
        assert "id" in data
        assert "hashed_password" not in data  # Password should not be returned
    
    def test_register_user_duplicate_username(self, client: TestClient, test_user: User):
        """Test registration with duplicate username."""
        response = client.post(
            "/auth/register",
            json={
                "email": "different@example.com",
                "username": test_user.username,  # Duplicate
                "password": "securepass123",
            }
        )
        assert response.status_code == 400
        assert "already registered" in response.json()["detail"].lower()
    
    def test_register_user_duplicate_email(self, client: TestClient, test_user: User):
        """Test registration with duplicate email."""
        response = client.post(
            "/auth/register",
            json={
                "email": test_user.email,  # Duplicate
                "username": "differentuser",
                "password": "securepass123",
            }
        )
        assert response.status_code == 400
        assert "already registered" in response.json()["detail"].lower()
    
    def test_login_success(self, client: TestClient, test_user: User):
        """Test successful login."""
        response = client.post(
            "/auth/login",
            data={
                "username": test_user.username,
                "password": "testpassword123",
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
    
    def test_login_wrong_password(self, client: TestClient, test_user: User):
        """Test login with wrong password."""
        response = client.post(
            "/auth/login",
            data={
                "username": test_user.username,
                "password": "wrongpassword",
            }
        )
        assert response.status_code == 401
    
    def test_login_nonexistent_user(self, client: TestClient):
        """Test login with non-existent user."""
        response = client.post(
            "/auth/login",
            data={
                "username": "nonexistent",
                "password": "anypassword",
            }
        )
        assert response.status_code == 401
    
    def test_get_current_user(self, client: TestClient, auth_headers: dict, test_user: User):
        """Test getting current user info with valid token."""
        response = client.get("/auth/me", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_user.id
        assert data["username"] == test_user.username
    
    def test_get_current_user_no_token(self, client: TestClient):
        """Test getting current user without token."""
        response = client.get("/auth/me")
        assert response.status_code == 401
    
    def test_get_current_user_invalid_token(self, client: TestClient):
        """Test getting current user with invalid token."""
        response = client.get(
            "/auth/me",
            headers={"Authorization": "Bearer invalid_token"}
        )
        assert response.status_code == 401


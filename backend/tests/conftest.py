"""Pytest configuration and shared fixtures."""
import pytest  # type: ignore
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient
from typing import Generator

from app.database import get_db
from app.main import app
from app.models.model import Base, User, Portfolio, Stock, Transaction
from app.security import hash_password


# Use in-memory SQLite database for testing
TEST_DATABASE_URL = "sqlite:///:memory:"

# Create test engine with StaticPool for in-memory database
test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

# Create test session factory
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture(scope="function")
def db_session() -> Generator[Session, None, None]:
    """Create a fresh database session for each test."""
    # Create all tables
    Base.metadata.create_all(bind=test_engine)
    
    # Create session
    session = TestingSessionLocal()
    
    try:
        yield session
    finally:
        session.close()
        # Drop all tables after test
        Base.metadata.drop_all(bind=test_engine)


@pytest.fixture(scope="function")
def client(db_session: Session) -> Generator[TestClient, None, None]:
    """Create a test client with database dependency override."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()


@pytest.fixture
def test_user(db_session: Session) -> User:
    """Create a test user."""
    user = User(
        email="test@example.com",
        username="testuser",
        hashed_password=hash_password("testpassword123"),
        disabled=False,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def test_user2(db_session: Session) -> User:
    """Create a second test user."""
    user = User(
        email="test2@example.com",
        username="testuser2",
        hashed_password=hash_password("testpassword123"),
        disabled=False,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def test_portfolio(db_session: Session, test_user: User) -> Portfolio:
    """Create a test portfolio for test_user."""
    portfolio = Portfolio(
        name="Test Portfolio",
        user_id=test_user.id,
    )
    db_session.add(portfolio)
    db_session.commit()
    db_session.refresh(portfolio)
    return portfolio


@pytest.fixture
def test_stock(db_session: Session) -> Stock:
    """Create a test stock."""
    stock = Stock(
        ticker_symbol="AAPL",
        company_name="Apple Inc.",
        sector="Technology",
    )
    db_session.add(stock)
    db_session.commit()
    db_session.refresh(stock)
    return stock


@pytest.fixture
def test_transaction_buy(
    db_session: Session, test_portfolio: Portfolio, test_stock: Stock
) -> Transaction:
    """Create a test buy transaction."""
    transaction = Transaction(
        portfolio_id=test_portfolio.id,
        ticker_symbol=test_stock.ticker_symbol,
        transaction_type="buy",
        quantity=10.0,
        price=150.0,
    )
    db_session.add(transaction)
    db_session.commit()
    db_session.refresh(transaction)
    return transaction


@pytest.fixture
def auth_headers(client: TestClient, test_user: User) -> dict:
    """Get authentication headers for test_user."""
    response = client.post(
        "/auth/login",
        data={
            "username": test_user.username,
            "password": "testpassword123",
        },
    )
    assert response.status_code == 200
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


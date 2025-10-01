"""
Test configuration for the Epic Events CRM system.

This module sets up a SQLite in-memory database for testing purposes,
providing a clean and isolated environment for unit and integration tests.
It includes a pytest fixture to create and manage database sessions.
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from ...models import Base, User, Client

# Create an in-memory SQLite engine for testing.
# This avoids affecting the production database and ensures tests run in isolation.
engine = create_engine("sqlite:///:memory:")

# Configure a sessionmaker bound to the test engine.
# autocommit=False and autoflush=False are typical settings for testing.
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture()
def db_session():
    """
    Pytest fixture that provides a database session for testing.

    This fixture:
    1. Creates all database tables before each test.
    2. Yields a database session to the test.
    3. Ensures all changes are rolled back and tables are dropped after the test.

    Yields:
        Session: A SQLAlchemy session bound to the test database.
    """
    # Create all tables in the test database
    Base.metadata.create_all(engine)

    # Create and yield a new session
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        # Close the session and drop all tables to ensure a clean state for the next test
        db.close()
        Base.metadata.drop_all(engine)


@pytest.fixture()
def test_user(db_session):
    """Fixture to create a test user."""
    user = User.create_user(
        db=db_session,
        username="test_user",
        first_name="Test",
        last_name="User",
        email="test@example.com",
        role="commercial"
    )
    return user


@pytest.fixture()
def test_client(db_session, test_user):
    """Fixture to create a test client linked to the test user."""
    client = Client.create(
        db=db_session,
        first_name="Test",
        last_name="Client",
        email="test.client@example.com",
        commercial_contact_id=test_user.user_id
    )
    return client

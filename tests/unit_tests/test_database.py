import pytest
from sqlalchemy import text
from ...database import engine, SessionLocal


def test_database_connection():
    """
    Test the database connection to ensure it is properly configured and accessible.
    """
    try:
        with engine.connect() as connection:
            # Assert that the connection is not None
            assert connection is not None, "Database connection failed: connection is None"

            # Execute a simple query and assert the result
            result = connection.execute(text("SELECT 1;"))
            assert result.scalar() == 1, "Database query failed: expected 1, got {result.scalar()}"

        print("✅ Database connection successful!")
    except Exception as e:
        pytest.fail(f"❌ Database connection error: {e}")


def test_session_creation():
    """
    Test the creation of a SQLAlchemy session to ensure it can be instantiated and closed properly.
    """
    try:
        # Create a session and assert it is not None
        session = SessionLocal()
        assert session is not None, "Session creation failed: session is None"

        # Test a simple query to ensure the session works
        result = session.execute(text("SELECT 1;"))
        assert result.scalar() == 1, "Session query failed: expected 1, got {result.scalar()}"

        session.close()  # Explicitly close the session
        print("✅ SQLAlchemy session created and closed successfully!")
    except Exception as e:
        pytest.fail(f"❌ Session creation error: {e}")

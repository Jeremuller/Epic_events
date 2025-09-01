import pytest
from sqlalchemy import text
from ...database import engine, SessionLocal

def test_database_connection():
    """
    Test the database connection to ensure it is properly configured and accessible.

    This test attempts to execute a simple SQL query ("SELECT 1") to verify that:
    - The database engine is correctly initialized.
    - The connection credentials (user, password, host, etc.) are valid.
    - The database server is reachable.

    Raises:
        pytest.fail: If the connection fails or the query does not return the expected result.
    """
    try:
        # Attempt to connect to the database and execute a simple query
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1;"))
            assert result.scalar() == 1  # Expected result: 1
        print("✅ Database connection successful!")  # Success message
    except Exception as e:
        # Fail the test if an error occurs
        pytest.fail(f"❌ Database connection error: {e}")

def test_session_creation():
    """
    Test the creation of a SQLAlchemy session to ensure it can be instantiated and closed properly.

    This test verifies that:
    - The SQLAlchemy session factory is correctly configured.
    - A session can be created and closed without errors.
    - The database connection pool is functional.

    Raises:
        pytest.fail: If the session creation or closure fails.
    """
    try:
        # Attempt to create and close a SQLAlchemy session
        session = SessionLocal()
        session.close()  # Explicitly close the session to free resources
        print("✅ SQLAlchemy session created and closed successfully!")  # Success message
    except Exception as e:
        # Fail the test if an error occurs
        pytest.fail(f"❌ Session creation error: {e}")

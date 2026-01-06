import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

from database import init_db

load_dotenv()


def create_database_if_not_exists():
    """
        Ensure that the application database exists.

        This function connects to the MySQL server (without selecting
        a specific database) and creates the target database if it
        does not already exist.

        This step is required because SQLAlchemy can create tables,
        but cannot create the database itself.

        The database connection parameters are loaded from environment
        variables defined in the .env file.
    """
    db_name = os.getenv("DB_NAME")
    if not db_name:
        raise RuntimeError("DB_NAME environment variable is not set")

    root_url = (
        f"mysql+mysqlconnector://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}"
        f"@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}"
    )

    engine = create_engine(root_url)

    with engine.connect() as connection:
        connection.execute(
            text(f"CREATE DATABASE IF NOT EXISTS {db_name}")
        )

    print(f"Database '{db_name}' is ready. ✅")


def main():
    """
        Initialize the application database.

        This script performs the full database initialization workflow:
            1. Creates the database if it does not exist.
            2. Creates all application tables using SQLAlchemy metadata.

        It is designed to be executed as a standalone script and can be
        safely re-run multiple times without side effects.
    """
    print("Starting database initialization...")

    create_database_if_not_exists()
    init_db()

    print("Database initialization complete 🎉")


if __name__ == "__main__":
    main()

"""
Bootstrap script to create the first management user.

This script is intended to be executed once during the initial setup
of the CRM application. It allows the creation of the first user with
the 'management' role, which is required to manage other users.

Security principles:
- Uses the same validation and password hashing mechanisms as the application
- Refuses to run if a user already exists
- Requires an initialized database
- Not accessible from the main application workflow
"""

import sys

import click
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session

from epic_events.database import SessionLocal
from epic_events.models import User
from epic_events.auth import hash_password


def get_db_session() -> Session:
    """
    Create and return a database session.

    Raises:
        RuntimeError: If the database does not exist or is unreachable.

    Returns:
        Session: An active SQLAlchemy session.
    """
    try:
        return SessionLocal()
    except OperationalError as exc:
        raise RuntimeError(
            "Database connection failed. "
            "Make sure the database exists and has been initialized."
        ) from exc


def user_exists(db: Session) -> bool:
    """

    Check whether at least one user already exists in the database.

    Args:
        db (Session): SQLAlchemy database session.

    Returns:
        bool: True if a user exists, False otherwise.
    """
    return db.query(User).first() is not None


@click.command()
@click.option(
    "--username",
    prompt=True,
    help="Username for the management account."
)
@click.option(
    "--email",
    prompt=True,
    help="Email address for the management account."
)
@click.option(
    "--password",
    prompt=True,
    hide_input=True,
    confirmation_prompt=True,
    help="Password for the management account."
)
def create_first_manager(username: str, email: str, password: str) -> None:
    """
    Create the first management user.

    This command will:
    - Verify that the database is accessible
    - Check that no user already exists
    - Hash the provided password
    - Create the user using the application's domain model

    The operation is intentionally irreversible and will refuse to run
    if a management user is already present.
    """
    try:
        db = get_db_session()
    except RuntimeError as error:
        click.echo(f"❌ {error}")
        sys.exit(1)

    try:
        if user_exists(db):
            click.echo(
                "❌ At least one user already exists. "
                "Bootstrap operation aborted."
            )
            sys.exit(1)

        password_hash = hash_password(password)

        user = User.create(
            db=db,
            username=username,
            first_name="System",
            last_name="Administrator",
            email=email,
            role="management",
            password_hash=password_hash,
        )

        db.add(user)
        db.commit()

        click.echo("✅ First management user successfully created.")

    except ValueError as error:
        db.rollback()
        click.echo(f"❌ User creation failed: {error}")

    except OperationalError:
        db.rollback()
        click.echo(
            "❌ Database operation failed. "
            "Ensure that the database schema has been initialized."
        )

    finally:
        db.close()


if __name__ == "__main__":
    create_first_manager()

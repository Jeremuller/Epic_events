import click
from database import SessionLocal
from models import User


@click.group()
def cli():
    """
    Main CLI entry point for the Epic Events CRM system.

    This command group organizes all subcommands related to user, client, contract,
    and event management. Use `--help` with any subcommand for more details.
    """
    pass


@cli.command()
@click.option("--first-name", prompt="User's first name", help="First name of the user (max 100 characters).")
@click.option("--last-name", prompt="User's last name", help="Last name of the user (max 100 characters).")
@click.option("--email", prompt="User's email", help="Unique email address of the user.")
@click.option("--role", prompt="User's role", type=click.Choice(["commercial", "management", "support"]),
              help="Role of the user in the system.")
def create_user_cli(first_name, last_name, email, role):
    """
    Creates a new user in the CRM system.

    This command prompts for user details (first name, last name, email, and role)
    and creates a new user record in the database. The password is set to a default value
    and should be updated later via a secure method.

    Args:
        first_name (str): User's first name.
        last_name (str): User's last name.
        email (str): Unique email address.
        role (str): User's role (commercial/management/support).
    """
    db = SessionLocal()
    try:
        # Create the user using the class method (note: password is set to default here)
        user = User.create_user(
            db=db,
            username=f"{first_name.lower()}_{last_name.lower()}",
            first_name=first_name,
            last_name=last_name,
            email=email,
            role=role,
            password="default_hashed_password"
        )
        click.echo(f"✅ User created: {user.first_name} {user.last_name} (ID: {user.user_id}, Role: {user.role})")
    except Exception as e:
        click.echo(f"❌ Error: {e}")
        db.rollback()  # Rollback in case of error
    finally:
        db.close()


if __name__ == "__main__":
    cli()

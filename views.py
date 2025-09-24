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


@cli.command()
def list_users():
    """
    Lists all users in the CRM system.

    This command retrieves and displays all users from the database,
    including their ID, full name, email, and role.
    """
    db = SessionLocal()
    try:
        users = User.get_all(db)
        if not users:
            click.echo("No users found in the database.")
            return

        click.echo("\n=== List of Users ===")
        for user in users:
            click.echo(f"ID: {user.user_id} | | {user.username} | {user.first_name} {user.last_name} | Email: {user.email} | Role: {user.role}")
    except Exception as e:
        click.echo(f"❌ Error: {e}")
    finally:
        db.close()


@cli.command()
@click.argument("user_id", type=int)
def update_user(user_id):
    """
    Updates an existing user in the CRM system.

    This command prompts for new values for the user's first name, last name, email, and role.
    The user is identified by their ID.

    Args:
        user_id (int): The ID of the user to update.
    """
    db = SessionLocal()
    try:
        user = User.get_by_id(db, user_id)
        if not user:
            click.echo(f"❌ User with ID {user_id} not found.")
            return

        click.echo(f"Updating user: {user.first_name} {user.last_name} (ID: {user.user_id})")
        first_name = click.prompt("New first name", default=user.first_name)
        last_name = click.prompt("New last name", default=user.last_name)
        email = click.prompt("New email", default=user.email)
        role = click.prompt("New role", type=click.Choice(["commercial", "management", "support"]), default=user.role)

        user.update(db, first_name=first_name, last_name=last_name, email=email, role=role)
        click.echo(f"✅ User updated: {user.first_name} {user.last_name} (ID: {user.user_id})")
    except Exception as e:
        click.echo(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()


@cli.command()
@click.argument("user_id", type=int)
def delete_user(user_id):
    """Deletes a user using User.get_by_id() and User.delete()."""
    db = SessionLocal()
    try:
        user = User.get_by_id(db, user_id)  # Utilisation de la nouvelle méthode
        if not user:
            click.echo(f"❌ User with ID {user_id} not found.")
            return

        click.echo(f"⚠️ You are about to delete user: {user.first_name} {user.last_name} (ID: {user.user_id})")
        if not click.confirm("Do you want to continue?"):
            click.echo("🔄 Operation cancelled.")
            return

        user.delete(db)
        click.echo(f"✅ User deleted: {user.first_name} {user.last_name} (ID: {user.user_id})")
    except Exception as e:
        click.echo(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    cli()

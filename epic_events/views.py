import click
from epic_events.models import User, Client, Contract
from epic_events.database import SessionLocal
from sqlalchemy.exc import OperationalError, ProgrammingError, InternalError

ERROR_MESSAGES = {
    "username_taken": "This username is already taken.",
    "email_taken": "This email is already registered.",
    "required_fields_empty": "Required fields cannot be empty or whitespace.",
    "invalid_role": "Invalid role. Must be one of: commercial, management, support.",
    "delete_failed": "Failed to delete user. Dependencies may be locked.",
    "database_error": "A technical error occurred. Please try again later.",
    "contact_not_found": "The contact mentioned does not exists.",
    "inferior_total_price": "Total price can't be inferior to rest to pay.",
    "invalid_total_price": "Total_price can't be <= 0.",
    "negative_rest_to_pay": "Rest to pay can't be < 0.",
    "contract_not_found": "The specified contract does not exist.",
}


@click.group()
def cli():
    """
    Main CLI entry point for the Epic Events CRM system.

    This command group organizes all subcommands related to user, client, contract,
    and event management. Use `--help` with any subcommand for more details.
    """
    pass


@cli.command()
@click.option("--username", prompt="Username", help="Unique username for authentication (max 100 characters).")
@click.option("--first-name", prompt="User's first name", help="First name of the user (max 100 characters).")
@click.option("--last-name", prompt="User's last name", help="Last name of the user (max 100 characters).")
@click.option("--email", prompt="User's email", help="Unique email address of the user.")
@click.option("--role", prompt="User's role", type=click.Choice(["commercial", "management", "support"]),
              help="Role of the user in the system.")
def create_user(username, first_name, last_name, email, role):
    """
    Creates a new user in the CRM system.

    This command prompts for user details (first name, last name, email, and role)
    and creates a new user record in the database. The password is set to a default value
    and should be updated later via a secure method.

    Args:
        username (str): Unique username for authentication.
        first_name (str): User's first name.
        last_name (str): User's last name.
        email (str): Unique email address.
        role (str): User's role (commercial/management/support).
    """
    db = click.get_current_context().obj['db']
    try:
        # Create the user using the class method (note: password is set to default here)
        user = User.create_user(
            db=db,
            username=username,
            first_name=first_name,
            last_name=last_name,
            email=email,
            role=role,
            password="default_hashed_password"
        )
        click.echo(
            f"✅ User created: {user.first_name} {user.last_name} (ID: {user.user_id},"
            f"Username: {user.username}, Role: {user.role})")

    except ValueError as e:
        error_key = str(e)
        click.echo(f"❌ Error: {ERROR_MESSAGES.get(error_key, ERROR_MESSAGES['database_error'])}")
    except Exception:
        click.echo(f"❌ Error: {ERROR_MESSAGES['database_error']}")
        raise

    finally:
        db.close()


@cli.command()
def list_users():
    """
    Lists all users in the CRM system.

    This command retrieves and displays all users from the database,
    including their ID, username, full name, email, and role.
    """
    db = click.get_current_context().obj['db']
    try:
        users = User.get_all(db)
        if not users:
            click.echo("No users found in the database.")
            return

        click.echo("\n=== List of Users ===")
        for user in users:
            click.echo(
                f"ID: {user.user_id} | {user.username} | {user.first_name} {user.last_name} | "
                f"Email: {user.email} | Role: {user.role}")
    except (OperationalError, ProgrammingError, InternalError):
        click.echo(f"❌ Database error: {ERROR_MESSAGES['database_error']}")
    except Exception:
        click.echo(f"❌ Unexpected error: {ERROR_MESSAGES['database_error']}")
        raise
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
    db = click.get_current_context().obj['db']
    try:
        user = User.get_by_id(db, user_id)
        if not user:
            click.echo(f"❌ User with ID {user_id} not found.")
            return

        click.echo(f"Updating user: {user.first_name} {user.last_name} (ID: {user.user_id})")
        username = click.prompt("New username", default=user.username)
        first_name = click.prompt("New first name", default=user.first_name)
        last_name = click.prompt("New last name", default=user.last_name)
        email = click.prompt("New email", default=user.email)
        role = click.prompt("New role", type=click.Choice(["commercial", "management", "support"]), default=user.role)

        user.update(db, username=username, first_name=first_name, last_name=last_name, email=email, role=role)
        click.echo(f"✅ User updated: {user.username} | {user.first_name} {user.last_name} (ID: {user.user_id})")
    except ValueError as e:
        error_key = str(e)
        click.echo(f"❌ Error: {ERROR_MESSAGES.get(error_key, ERROR_MESSAGES['database_error'])}")
    except Exception:
        click.echo(f"❌ Error: {ERROR_MESSAGES['database_error']}")
        raise
    finally:
        db.close()


@cli.command()
@click.argument("user_id", type=int)
def delete_user(user_id):
    """
    Deletes an existing user from the CRM system.
    This command prompts for confirmation before permanently deleting a user identified by their ID.
    The user's associated clients, contracts, and events will have their references set to None.
    Args:
        user_id (int): The ID of the user to delete.
    """
    db = click.get_current_context().obj['db']
    try:
        user = User.get_by_id(db, user_id)
        if not user:
            click.echo(f"❌ User with ID {user_id} not found.")
            return

        click.echo(f"⚠️ You are about to delete user: {user.first_name} {user.last_name} (ID: {user.user_id})")
        if not click.confirm("Do you want to continue?"):
            click.echo("🔄 Operation cancelled.")
            return

        user.delete(db)
        click.echo(f"✅ User deleted: {user.first_name} {user.last_name} (ID: {user.user_id})")

    except ValueError as e:
        error_key = str(e)
        click.echo(f"❌ Error: {ERROR_MESSAGES.get(error_key, ERROR_MESSAGES['database_error'])}")
    except Exception:
        click.echo(f"❌ Error: {ERROR_MESSAGES['database_error']}")
        raise

    finally:
        db.close()


@cli.command()
@click.option("--first-name", prompt="First name", help="Client's first name.")
@click.option("--last-name", prompt="Last name", help="Client's last name.")
@click.option("--email", prompt="Email", help="Client's email address.")
@click.option("--commercial-id", prompt="Commercial user ID", type=int, help="ID of the commercial user.")
@click.option("--business-name", prompt="Business name (optional)", default=None, help="Client's business name.")
@click.option("--telephone", prompt="Telephone (optional)", default=None, help="Client's phone number.")
def create_client(first_name, last_name, email, commercial_id, business_name, telephone):
    """
    Creates a new client in the CRM system.
    This command prompts for client details (first name, last name, email, commercial contact ID,
    and optional business name/telephone) and creates a new client record in the database.
    Args:
        first_name (str): Client's first name.
        last_name (str): Client's last name.
        email (str): Unique email address of the client.
        commercial_id (int): ID of the commercial user responsible for the client.
        business_name (str, optional): Client's business name.
        telephone (str, optional): Client's phone number.
    """
    db = click.get_current_context().obj['db']
    try:
        client = Client.create(
            db=db,
            first_name=first_name,
            last_name=last_name,
            email=email,
            commercial_contact_id=commercial_id,
            business_name=business_name,
            telephone=telephone
        )
        click.echo(f"✅ Client created: {client.first_name} {client.last_name} (ID: {client.client_id})")
    except ValueError as e:
        error_key = str(e)
        click.echo(f"❌ Error: {ERROR_MESSAGES.get(error_key, ERROR_MESSAGES['database_error'])}")
    except (OperationalError, ProgrammingError, InternalError):
        click.echo(f"❌ Database error: {ERROR_MESSAGES['database_error']}")
    except Exception:
        click.echo(f"❌ Unexpected error: {ERROR_MESSAGES['database_error']}")
        raise
    finally:
        db.close()


@cli.command()
def list_clients():
    """
    Lists all clients in the CRM system.

    This command retrieves and displays all users from the database,
    including their ID, full name, email, contact and business name.
    If no clients exist, a message is displayed to inform the user.
    """
    db = click.get_current_context().obj['db']
    try:
        clients = Client.get_all(db)
        if not clients:
            click.echo("No clients found in the database.")
            return

        click.echo("\n=== List of Clients ===")
        for client in clients:
            contact = f"{client.commercial_contact.first_name} {client.commercial_contact.last_name}" \
                if client.commercial_contact else "None"
            click.echo(
                f"ID: {client.client_id} | "
                f"{client.first_name} {client.last_name} | "
                f"Email: {client.email} | "
                f"Commercial: {contact} | "
                f"Business: {client.business_name or 'N/A'}"
            )
    except (OperationalError, ProgrammingError, InternalError):
        click.echo(f"❌ Database error: {ERROR_MESSAGES['database_error']}")
    except Exception:
        click.echo(f"❌ Unexpected error: {ERROR_MESSAGES['database_error']}")
        raise
    finally:
        db.close()


@cli.command()
@click.argument("client_id", type=int)
def update_client(client_id):
    """
        Updates a client's information in the CRM system via interactive prompts.
        This command retrieves a client by their ID, prompts for new values (first name, last name, email,
        business name, telephone, and commercial contact ID), and applies the changes using Client.update().
        If the client does not exist, an error message is displayed.
        Args:
            client_id (int): The ID of the client to update.
        """
    db = click.get_current_context().obj['db']
    try:
        client = Client.get_by_id(db, client_id)
        if not client:
            click.echo(f"❌ Client with ID {client_id} not found.")
            return

        click.echo(f"Updating client: {client.first_name} {client.last_name} (ID: {client.client_id})")

        # Prompt for new values
        first_name = click.prompt("First name", default=client.first_name)
        last_name = click.prompt("Last name", default=client.last_name)
        email = click.prompt("Email", default=client.email)
        business_name = click.prompt("Business name (optional)", default=client.business_name or None)
        telephone = click.prompt("Telephone (optional)", default=client.telephone or None)
        commercial_contact_id = click.prompt("Commercial contact ID (optional)",
                                             default=str(
                                                 client.commercial_contact_id)
                                             if client.commercial_contact_id else "None",
                                             type=int)

        # Update the client
        client.update(
            db=db,
            first_name=first_name,
            last_name=last_name,
            email=email,
            business_name=business_name or None,
            telephone=telephone or None,
            commercial_contact_id=commercial_contact_id
        )

        click.echo(f"✅ Client updated: {client.first_name} {client.last_name} (ID: {client.client_id})")
    except ValueError as e:
        error_key = str(e)
        click.echo(f"❌ Error: {ERROR_MESSAGES.get(error_key, ERROR_MESSAGES['database_error'])}")
    except (OperationalError, ProgrammingError, InternalError):
        click.echo(f"❌ Database error: {ERROR_MESSAGES['database_error']}")
    except Exception:
        click.echo(f"❌ Unexpected error: {ERROR_MESSAGES['database_error']}")
        raise
    finally:
        db.close()


@cli.command()
@click.option("--total-price", prompt="Total price", type=float, help="Total amount of the contract (e.g., 1000.00).")
@click.option("--rest-to-pay", prompt="Rest to pay", type=float, help="Remaining amount to be paid.")
@click.option("--client-id", prompt="Client ID", type=int, help="ID of the associated client.")
@click.option("--commercial-id", prompt="Commercial user ID", type=int, help="ID of the commercial user.")
def create_contract(total_price, rest_to_pay, client_id, commercial_id):
    """
    Creates a new contract in the CRM system.
    This command prompts for contract details (total price, rest to pay, client ID, and commercial user ID)
    and creates a new contract record in the database.
    Args:
        total_price (float): Total amount of the contract (must be > 0).
        rest_to_pay (float): Remaining amount to be paid (must be ≥ 0 and ≤ total_price).
        client_id (int): ID of the associated client.
        commercial_id (int): ID of the commercial user responsible for the contract.
    """
    db = click.get_current_context().obj['db']
    try:
        contract = Contract.create(
            db=db,
            total_price=total_price,
            rest_to_pay=rest_to_pay,
            client_id=client_id,
            commercial_contact_id=commercial_id
        )
        click.echo(
            f"✅ Contract created: ID {contract.contract_id} "
            f"(Total: {contract.total_price}, Rest to Pay: {contract.rest_to_pay})"
        )
    except ValueError as e:
        error_key = str(e)
        click.echo(f"❌ Error: {ERROR_MESSAGES.get(error_key, ERROR_MESSAGES['database_error'])}")
    except (OperationalError, ProgrammingError, InternalError):
        click.echo(f"❌ Database error: {ERROR_MESSAGES['database_error']}")
    except Exception:
        click.echo(f"❌ Unexpected error: {ERROR_MESSAGES['database_error']}")
        raise
    finally:
        db.close()


@cli.command()
def list_contracts():
    """
    Lists all contracts in the CRM system.
    This command retrieves and displays all contracts from the database,
    including their ID, total price, rest to pay, client, and commercial contact.
    If no contracts exist, a message is displayed to inform the user.
    """
    db = click.get_current_context().obj['db']
    try:
        contracts = Contract.get_all(db)
        if not contracts:
            click.echo("No contracts found in the database.")
            return
        click.echo("\n=== List of Contracts ===")
        for contract in contracts:
            client_name = f"{contract.client.first_name} {contract.client.last_name}" if contract.client else "N/A"
            commercial_name = (
                f"{contract.commercial_contact.first_name} {contract.commercial_contact.last_name}"
                if contract.commercial_contact else "N/A"
            )
            click.echo(
                f"ID: {contract.contract_id} | "
                f"Total: {contract.total_price} | "
                f"Rest to Pay: {contract.rest_to_pay} | "
                f"Client: {client_name} (ID: {contract.client_id}) | "
                f"Commercial: {commercial_name} (ID: {contract.commercial_contact_id}) | "
                f"Signed: {contract.signed}"
            )
    except (OperationalError, ProgrammingError, InternalError):
        click.echo(f"❌ Database error: {ERROR_MESSAGES['database_error']}")
    except Exception:
        click.echo(f"❌ Unexpected error: {ERROR_MESSAGES['database_error']}")
        raise
    finally:
        db.close()


@cli.command()
@click.argument("contract_id", type=int)
def update_contract(contract_id):
    """
    Updates an existing contract in the CRM system.
    This command retrieves a contract by its ID, prompts for new values (total price, rest to pay, signed status),
    and applies the changes using Contract.update().
    If the contract does not exist, an error message is displayed.
    Args:
        contract_id (int): The ID of the contract to update.
    """
    db = click.get_current_context().obj['db']
    try:
        contract = Contract.get_by_id(db, contract_id)
        if not contract:
            click.echo(f"❌ Contract with ID {contract_id} not found.")
            return
        click.echo(
            f"Updating contract: ID {contract.contract_id} "
            f"(Total: {contract.total_price}, Rest to Pay: {contract.rest_to_pay})"
        )

        # Prompt for new values
        total_price = click.prompt("Total price", type=float, default=contract.total_price)
        rest_to_pay = click.prompt("Rest to pay", type=float, default=contract.rest_to_pay)
        signed = click.prompt("Is the contract signed?", type=bool, default=contract.signed)

        contract.update(
            db=db,
            total_price=total_price,
            rest_to_pay=rest_to_pay,
            signed=signed
        )
        click.echo(f"✅ Contract updated: ID {contract.contract_id}")
    except ValueError as e:
        error_key = str(e)
        click.echo(f"❌ Error: {ERROR_MESSAGES.get(error_key, ERROR_MESSAGES['database_error'])}")
    except (OperationalError, ProgrammingError, InternalError):
        click.echo(f"❌ Database error: {ERROR_MESSAGES['database_error']}")
    except Exception:
        click.echo(f"❌ Unexpected error: {ERROR_MESSAGES['database_error']}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    db = SessionLocal()
    try:
        cli(obj={"db": db})
    finally:
        db.close()

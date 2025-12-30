from epic_events.models import User, Client, Contract, Event
from epic_events.utils import ErrorMessages, validate_length
from datetime import datetime
import click


class DisplayMessages:
    @staticmethod
    def display_success(message):
        """Displays a success message."""
        click.echo(f"✅ {message}")

    @staticmethod
    def display_error(message_key):
        """Displays error message using our ErrorMessages class."""
        click.echo(f"❌ Error: {ErrorMessages.get_message(message_key)}")

    @staticmethod
    def display_invalid_choice(menu_name):
        """Displays an error message for invalid menu choices."""
        print(f"Invalid choice. Please enter a valid number for the {menu_name} menu.")

    @staticmethod
    def display_goodbye():
        """Displays a goodbye message when exiting the CRM."""
        print("Exiting CRM. Goodbye!")


class MenuView:
    """Static methods for displaying menus and capturing user choices."""

    @staticmethod
    def display_main_menu():
        """Displays the main menu and captures user choice."""
        print("\n=== CRM Main Menu ===")
        print("1. Manage Users")
        print("2. Manage Clients")
        print("3. Manage Contracts")
        print("4. Manage Events")
        print("5. Quit")
        return input("Enter your choice (1-5): ")

    @staticmethod
    def display_users_menu():
        """Displays the Users submenu and captures user choice."""
        print("\n=== Users Menu ===")
        print("1. Create User")
        print("2. Update User")
        print("3. Delete User")
        print("4. Back to Main Menu")
        return input("Enter your choice (1-4): ")

    @staticmethod
    def display_clients_menu():
        """Displays the Clients submenu and captures user choice."""
        print("\n=== Clients Menu ===")
        print("1. List Clients")
        print("2. Create Client")
        print("3. Update Client")
        print("4. Back to Main Menu")
        return input("Enter your choice (1-4): ")

    @staticmethod
    def display_contracts_menu():
        """Displays the Contracts submenu and captures user choice."""
        print("\n=== Contracts Menu ===")
        print("1. List Contracts")
        print("2. Create Contract")
        print("3. Update Contract")
        print("4. Back to Main Menu")
        return input("Enter your choice (1-4): ")

    @staticmethod
    def display_events_menu():
        """Displays the Events submenu and captures user choice."""
        print("\n=== Events Menu ===")
        print("1. List Events")
        print("2. Create Event")
        print("3. Update Event")
        print("4. Back to Main Menu")
        return input("Enter your choice (1-4): ")

    @staticmethod
    def prompt_for_id(entity_name):
        """
        Prompts the user for an entity ID (generic method for any entity).
        Args:
            entity_name (str): Name of the entity (e.g., "user", "client").
        Returns:
            int: The ID entered by the user.
        """
        return click.prompt(f"Enter the ID of the {entity_name} to update/delete", type=int)

    @staticmethod
    def prompt_for_contact_id(entity_name):
        """
        Prompts the user for an entity ID (generic method for any entity).
        Args:
            entity_name (str): Name of the entity (e.g., "user", "client").
        Returns:
            int: The ID entered by the user.
        """
        return click.prompt(f"Enter the ID of the {entity_name}", type=int)


class LoginView:
    @staticmethod
    def prompt_login():
        """
        Prompt the user for login credentials.

        Returns:
            dict: Dictionary containing username and password.
        """
        username = click.prompt("Username")
        password = click.prompt("Password")

        return {
            "username": username,
            "password": password
        }


class UserView:
    """Static methods for user-related view operations."""

    @staticmethod
    def display_user_id_list(users):
        print("\nAvailable users:")
        print("ID | Username")
        print("----------")
        for user in users:
            print(f"{user.user_id} | {user.username}")

    @staticmethod
    def prompt_user_creation():
        """
        Prompts the user to enter details for creating a new user.
        Uses Click for input validation.
        Returns:
            dict: User details (username, first_name, last_name, email, role).
        """
        username = validate_length("Username (max 100 chars)", 100)
        first_name = validate_length("First name (max 100 chars)", 100)
        last_name = validate_length("Last name (max 100 chars)", 100)
        email = click.prompt("Email")
        role = click.prompt(
            "Role",
            type=click.Choice(["commercial", "management", "support"], case_sensitive=False)
        )
        password = click.prompt("Password")
        return {
            "username": username,
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
            "role": role,
            "password": password
        }

    @staticmethod
    def prompt_update(user):
        """
        Prompts the user to update an existing user's information.
        Args:
            user (User): The user object to update.
        Returns:
            dict: Updated fields (only non-empty fields are included).
                  Example: {"first_name": "NewName", "email": "new@example.com"}
        """
        click.echo(f"Updating user: {user.first_name} {user.last_name} (ID: {user.user_id})")

        # Prompt for each field with current value as default
        username = click.prompt("New username", default=user.username)
        first_name = click.prompt("New first name", default=user.first_name)
        last_name = click.prompt("New last name", default=user.last_name)
        email = click.prompt("New email", default=user.email)
        role = click.prompt(
            "New role",
            type=click.Choice(["commercial", "management", "support"]),
            default=user.role
        )

        # Return only fields that were actually changed
        updated_data = {}
        if username != user.username:
            updated_data["username"] = username
        if first_name != user.first_name:
            updated_data["first_name"] = first_name
        if last_name != user.last_name:
            updated_data["last_name"] = last_name
        if email != user.email:
            updated_data["email"] = email
        if role != user.role:
            updated_data["role"] = role

        return updated_data

    @staticmethod
    def prompt_delete_confirmation(user):
        """
        Prompts the user for confirmation before deleting a user.
        Args:
            user (User): The user object to delete.
        Returns:
            bool: True if the user confirms deletion, False otherwise.
        """
        return click.confirm(
            f"Are you sure you want to delete user {user.username} "
            f"(ID: {user.user_id})? This action cannot be undone."
        )


class ClientView:
    """Static methods for client-related view operations."""

    @staticmethod
    def list_clients(clients):
        """
        Displays a list of clients in the CRM system.

        Args:
            clients (list[Client]): List of Client objects to display.
                                    If empty, a message is shown.
        """
        if not clients:
            print("No clients found in the database.")
            return

        print("\n=== List of Clients ===")
        for client in clients:
            # Format the dates for better readability
            first_contact = client.first_contact.strftime("%Y-%m-%d %H:%M") if client.first_contact else "N/A"
            last_update = client.last_update.strftime("%Y-%m-%d %H:%M") if client.last_update else "N/A"

            # Get commercial contact name if available
            commercial_name = (
                f"{client.commercial_contact.first_name} {client.commercial_contact.last_name}"
                if client.commercial_contact else "None"
            )

            print(
                f"ID: {client.client_id} | "
                f"Name: {client.first_name} {client.last_name} | "
                f"Business: {client.business_name} | "
                f"Email: {client.email} | "
                f"Phone: {client.telephone} | "
                f"First Contact: {first_contact} | "
                f"Last Update: {last_update} | "
                f"Commercial: {commercial_name}"
            )

    @staticmethod
    def prompt_client_creation():
        """
        Prompts the user for new client information.

        Returns:
            dict: Client data including:
                  - first_name (str)
                  - last_name (str)
                  - email (str)
                  - business_name (str, optional)
                  - telephone (str, optional)
        """

        # Prompt for other client details
        return {
            "first_name": click.prompt("First name", type=str),
            "last_name": click.prompt("Last name", type=str),
            "email": click.prompt("Email", type=str),
            "business_name": click.prompt("Business name (optional)", default="", type=str) or None,
            "telephone": click.prompt("Phone (optional)", default="", type=str) or None
        }

    @staticmethod
    def prompt_update(client):
        """
        Prompts the user to update an existing client's information.
        Only returns fields that were actually modified by the user.
        Args:
            client (Client): The client object to update.
        Returns:
            dict: Updated fields (only modified fields are included).
        """
        print(
            f"\nUpdating client: {client.business_name or f'{client.first_name} {client.last_name}'} "
            f"(ID: {client.client_id})")

        # Prompt for each field with current value as default
        updated_data = {
            "first_name": click.prompt("First name", default=client.first_name),
            "last_name": click.prompt("Last name", default=client.last_name),
            "email": click.prompt("Email", default=client.email),
            "commercial_contact_id": click.prompt("Commercial contact", type=int),
            "business_name": click.prompt("Business name (optional)", default=client.business_name or ""),
            "telephone": click.prompt("Phone (optional)", default=client.telephone or ""),
        }

        # Filter out fields that were not modified (user pressed Enter without typing)
        return {
            key: value for key, value in updated_data.items()
            if value != getattr(client, key) and value != ""  # Ignore empty strings unless the original was None
        }


class ContractView:
    """Static methods for contract-related view operations."""

    @staticmethod
    def list_contracts(contracts):
        """
        Displays a list of contracts in the CRM system.

        Args:
            contracts (list[Contract]): List of Contract objects to display.
                                       If empty, a message is shown.
        """
        if not contracts:
            print("No contracts found in the database.")
            return

        print("\n=== List of Contracts ===")
        for contract in contracts:
            # Format client and commercial names
            client_name = f"{contract.client.first_name} {contract.client.last_name}" if contract.client else "N/A"
            commercial_name = (
                f"{contract.commercial_contact.first_name} {contract.commercial_contact.last_name}"
                if contract.commercial_contact else "N/A"
            )

            print(
                f"ID: {contract.contract_id} | "
                f"Client: {client_name} | "
                f"Commercial: {commercial_name} | "
                f"Total: {contract.total_price}€ | "
                f"Remaining: {contract.rest_to_pay}€ | "
                f"Signed: {'Yes' if contract.signed else 'No'} | "
                f"Created: {contract.creation.strftime('%Y-%m-%d %H:%M') if contract.creation else 'N/A'}"
            )

    @staticmethod
    def prompt_contract_creation():
        """
        Prompts the user for new contract information.

        Returns:
            dict: Contract data including:
                  - total_price (float): Total amount of the contract.
                  - rest_to_pay (float): Remaining amount to be paid.
                  - client_id (int): ID of the associated client.
                  - commercial_contact_id (int): ID of the commercial user responsible.
                  - signed (bool, optional): Whether the contract is signed. Defaults to False.
        """
        return {
            "total_price": float(click.prompt("Total price (€)", type=float)),
            "rest_to_pay": float(click.prompt("Remaining amount to pay (€)", type=float)),
            "client_id": click.prompt("Client", type=int),
            "commercial_contact_id": click.prompt("Commercial contact", type=int),
            "signed": click.confirm("Is the contract already signed?", default=False)
        }

    @staticmethod
    def prompt_update(contract):
        """
        Prompts the user to update an existing contract's information.
        Only returns fields that were actually modified by the user.

        Args:
            contract (Contract): The contract object to update.

        Returns:
            dict: Updated fields (only modified fields are included).
        """
        print(f"\nUpdating contract ID: {contract.contract_id}")
        print(f"Current client: {contract.client.business_name if contract.client else 'N/A'}")
        print(f"Current commercial: {contract.commercial_contact.first_name if contract.commercial_contact else 'N/A'}")

        # Prompt for each field with current value as default
        updated_data = {
            "total_price": click.prompt("Total price (€)", default=contract.total_price, type=float),
            "rest_to_pay": click.prompt("Remaining amount to pay (€)", default=contract.rest_to_pay, type=float),
            "client_id": click.prompt("Client ID", default=contract.client_id, type=int),
            "commercial_contact_id": click.prompt("Commercial contact ID", default=contract.commercial_contact_id,
                                                  type=int),
            "signed": click.confirm("Is the contract signed?", default=contract.signed)
        }

        # Filter out fields that were not modified
        return {
            key: value for key, value in updated_data.items()
            if value != getattr(contract, key)
        }


class EventView:
    """Static methods for event-related view operations."""

    @staticmethod
    def list_events(events):
        """
        Displays a list of events in the CRM system.

        Args:
            events (list[Event]): List of Event objects to display.
        """
        if not events:
            print("No events found in the database.")
            return

        print("\n=== List of Events ===")
        for event in events:
            # Format client and support contact names
            client_name = f"{event.client.business_name}" if event.client else "N/A"
            support_name = (
                f"{event.support_contact.first_name} {event.support_contact.last_name}"
                if event.support_contact else "N/A"
            )

            print(
                f"ID: {event.event_id} | "
                f"Name: {event.name} | "
                f"Client: {client_name} | "
                f"Support: {support_name} | "
                f"Start: {event.start_datetime} | "
                f"End: {event.end_datetime} | "
                f"Location: {event.location} | "
                f"Attendees: {event.attendees}"
            )

    @staticmethod
    def display_unassigned_events(events):
        """
        Displays a list of events that have no support assigned.

        Args:
            events (List[Event]): List of Event objects to display.
        """
        if not events:
            print("No unassigned events found.")
            return

        print("\nUnassigned Events:")
        for e in events:
            print(f"- ID: {e.event_id}, Name: {e.name}, Client: {e.client.business_name if e.client else 'N/A'}, "
                  f"Start: {e.start_datetime}, End: {e.end_datetime}, Location: {e.location}")

    @staticmethod
    def prompt_event_creation():
        """
        Prompts the user for new event information.
        Handles datetime input parsing and validation.

        Returns:
            dict: Event data including:
                  - name (str)
                  - notes (str, optional)
                  - start_datetime (datetime)
                  - end_datetime (datetime)
                  - location (str, optional)
                  - attendees (int)
                  - client_id (int)
                  - support_contact_id (int)
        """

        # Handle datetime format
        def parse_datetime(prompt_text):
            """Helper to parse datetime input from user."""
            while True:
                try:
                    return datetime.strptime(
                        click.prompt(prompt_text + " (YYYY-MM-DD HH:MM)"),
                        "%Y-%m-%d %H:%M"
                    )
                except ValueError:
                    print("Invalid format. Please use YYYY-MM-DD HH:MM (e.g., 2023-12-25 14:30).")

        return {
            "name": click.prompt("Event name", type=str),
            "notes": click.prompt("Notes (optional)", default="", type=str) or None,
            "start_datetime": parse_datetime("Start date and time"),
            "end_datetime": parse_datetime("End date and time"),
            "location": click.prompt("Location (optional)", default="", type=str) or None,
            "attendees": click.prompt("Number of attendees", type=int),
            "client_id": click.prompt("client", type=int)
        }

    @staticmethod
    def prompt_update(event):
        """
        Prompts the user to update an existing event's information.
        Only returns fields that were actually modified by the user.

        Args:
            event (Event): The event object to update.

        Returns:
            dict: Updated fields (only modified fields are included).
        """
        from datetime import datetime

        print(f"\nUpdating event: {event.name} (ID: {event.event_id})")

        def parse_datetime(prompt_text, current_value):
            """Helper to parse datetime input from user."""
            if not click.confirm(f"Update {prompt_text}?", default=False):
                return current_value
            while True:
                try:
                    return datetime.strptime(
                        click.prompt(f"New {prompt_text} (YYYY-MM-DD HH:MM)"),
                        "%Y-%m-%d %H:%M"
                    )
                except ValueError:
                    print("Invalid format. Please use YYYY-MM-DD HH:MM.")

        # Prompt for each field with current value as default
        updated_data = {
            "name": click.prompt("Event name", default=event.name),
            "notes": click.prompt("Notes (optional)", default=event.notes or ""),
            "start_datetime": parse_datetime("start date and time", event.start_datetime),
            "end_datetime": parse_datetime("end date and time", event.end_datetime),
            "location": click.prompt("Location (optional)", default=event.location or ""),
            "attendees": click.prompt("Number of attendees", default=event.attendees, type=int),
            "client_id": click.prompt("Client ID", default=event.client_id, type=int),
            "support_contact_id": click.prompt("Support contact ID", default=event.support_contact_id, type=int)
        }

        # Filter out fields that were not modified
        return {
            key: value for key, value in updated_data.items()
            if value != getattr(event, key)
        }

import click
from utils import ErrorMessages
from models import User, Client, Contract, Event
from views import (list_users, list_clients, list_contracts, list_events, prompt_user_creation,
                   display_error, display_success)

from epic_events.database import SessionLocal

db = SessionLocal()


def display_main_menu():
    """Display the main menu and handle user navigation."""
    while True:
        print("\n=== CRM Main Menu ===")
        print("1. Manage Users")
        print("2. Manage Clients")
        print("3. Manage Contracts")
        print("4. Manage Events")
        print("5. Quit")

        choice = input("Enter your choice (1-5): ")

        if choice == "1":
            manage_users()
        elif choice == "2":
            manage_clients()
        elif choice == "3":
            manage_contracts()
        elif choice == "4":
            manage_events()
        elif choice == "5":
            print("Exiting CRM. Goodbye!")
            break
        else:
            print("Invalid choice. Please enter a number between 1 and 5.")


def manage_users():
    """Display the Users submenu and handle user actions."""
    while True:
        print("\n=== Users Menu ===")
        print("1. List Users")
        print("2. Create User")
        print("3. Update User")
        print("4. Delete User")
        print("5. Back to Main Menu")

        choice = input("Enter your choice (1-5): ")

        if choice == "1":
            try:
                users = User.get_all(db)
                list_users(users)
            except Exception as e:
                print(f"Error fetching users: {e}")
        elif choice == "2":
            create_user(db)
        elif choice == "3":
            update_user()
        elif choice == "4":
            delete_user()
        elif choice == "5":
            break
        else:
            print("Invalid choice. Please enter a number between 1 and 5.")


def manage_clients():
    """Display the Clients submenu and handle user actions."""
    while True:
        print("\n=== Clients Menu ===")
        print("1. List Clients")
        print("2. Create Client")
        print("3. Update Client")
        print("4. Back to Main Menu")

        choice = input("Enter your choice (1-4): ")

        if choice == "1":
            clients = Client.get_all(db)
            list_clients(clients)
        elif choice == "2":
            create_client()
        elif choice == "3":
            update_client()
        elif choice == "4":
            break
        else:
            print("Invalid choice. Please enter a number between 1 and 4.")


def manage_contracts():
    """Display the Contracts submenu and handle user actions."""
    while True:
        print("\n=== Contracts Menu ===")
        print("1. List Contracts")
        print("2. Create Contract")
        print("3. Update Contract")
        print("4. Back to Main Menu")

        choice = input("Enter your choice (1-4): ")

        if choice == "1":
            contracts = Contract.get_all(db)
            list_contracts(contracts)
        elif choice == "2":
            create_contract()
        elif choice == "3":
            update_contract()
        elif choice == "4":
            break
        else:
            print("Invalid choice. Please enter a number between 1 and 4.")


def manage_events():
    """Display the Events submenu and handle user actions."""
    while True:
        print("\n=== Events Menu ===")
        print("1. List Events")
        print("2. Create Event")
        print("3. Update Event")
        print("4. Back to Main Menu")

        choice = input("Enter your choice (1-4): ")

        if choice == "1":
            events = Event.get_all(db)
            list_events(events)
        elif choice == "2":
            create_event()
        elif choice == "3":
            update_event()
        elif choice == "4":
            break
        else:
            print("Invalid choice. Please enter a number between 1 and 4.")


def create_user(db):
    """
    Controller function to orchestrate the creation of a new user.
    Steps:
      1. Prompts the user for input via the view layer.
      2. Validates and creates the user via the model layer.
      3. Handles success/error feedback via the view layer.

    Args:
        db (sqlalchemy.orm.Session): Active database session.

    Notes:
        - All user interaction is delegated to the view layer.
        - All business logic and data operations are delegated to the model layer.
        - Error handling is centralized here, with display delegated to the view.
    """
    try:
        # Step 1: Delegate user input to the view
        user_data = prompt_user_creation()

        # Step 2: Delegate user creation to the model
        user = User.create_user(
            db=db,
            username=user_data["username"],
            first_name=user_data["first_name"],
            last_name=user_data["last_name"],
            email=user_data["email"],
            role=user_data["role"],
            password="default_hashed_password"  # Note: Replace with secure password logic
        )

        # Step 3: Delegate success feedback to the view
        display_user_creation_success(user)

    except ValueError as e:
        # Delegate error display to the view
        display_validation_error(str(e))
    except Exception as e:
        # Delegate database error display to the view
        display_database_error(str(e))
        raise  # Re-raise for logging or further handling


if __name__ == "__main__":
    display_main_menu()

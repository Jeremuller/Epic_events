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
    Controller function to orchestrate the creation of a new user in the CRM system.
    This function acts as an intermediary between the view (user interaction) and the model (business logic).
    It handles transaction management (commit/rollback) and error feedback.

    Args:
        db (sqlalchemy.orm.Session): Active database session for persistence operations.

    Workflow:
        1. Delegates user input collection to the view layer (`prompt_user_creation`).
        2. Delegates user validation and object creation to the model layer (`User.create_user`).
        3. Manages database persistence (commit/rollback) based on operation success/failure.
        4. Delegates success/error feedback to the view layer (`display_success`/`display_error`).

    Transaction Management:
        - Commits changes to the database if the operation succeeds.
        - Rolls back changes if any error occurs (validation or database error).
        - Ensures data consistency by handling exceptions explicitly.

    Error Handling:
        - Catches `ValueError` for business logic validation errors (e.g., duplicate username/email).
        - Catches generic `Exception` for database/technical errors.
        - Delegates error display to the view layer with appropriate error keys.

    """
    try:
        # Step 1: Delegate user input to the view layer
        user_data = prompt_user_creation()

        # Step 2: Delegate user validation and object creation to the model layer
        user = User.create_user(
            db=db,
            username=user_data["username"],
            first_name=user_data["first_name"],
            last_name=user_data["last_name"],
            email=user_data["email"],
            role=user_data["role"],
            password="default_hashed_password"
        )

        # Step 3: Persist the user (controller responsibility)
        db.add(user)
        db.commit()
        db.refresh(user)

        # Step 4: Delegate success feedback to the view layer
        display_success(f"User created: {user.first_name} {user.last_name} (ID: {user.user_id})")

    except ValueError as e:
        # Handle business logic validation errors
        db.rollback()
        display_error(str(e))

    except Exception:
        # Handle database/technical errors
        db.rollback()
        display_error("DATABASE_ERROR")
        raise


if __name__ == "__main__":
    display_main_menu()

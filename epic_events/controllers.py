from models import User, Client, Contract, Event
from views import (DisplayMessages, UserView, MenuView)

from epic_events.database import SessionLocal

db = SessionLocal()


class MenuController:
    """Static methods for handling menu navigation and controller delegation."""

    @staticmethod
    def run_main_menu(db):
        """
        Runs the main menu loop and delegates actions to submenus.
        Args:
            db (sqlalchemy.orm.Session): Database session for data operations.
        """
        while True:
            choice = MenuView.display_main_menu()
            if choice == "1":
                MenuController.run_users_menu(db)
            elif choice == "2":
                MenuController.run_clients_menu(db)
            elif choice == "3":
                MenuController.run_contracts_menu(db)
            elif choice == "4":
                MenuController.run_events_menu(db)
            elif choice == "5":
                DisplayMessages.display_goodbye()
                break
            else:
                DisplayMessages.display_invalid_choice("main")

    @staticmethod
    def run_users_menu(db):
        """Runs the Users submenu loop and delegates actions to UserController."""
        while True:
            choice = MenuView.display_users_menu()
            if choice == "1":
                UserController.list_users(db)
            elif choice == "2":
                UserController.create_user(db)
            elif choice == "3":
                UserController.update_user(db)
            elif choice == "4":
                UserController.delete_user(db)
            elif choice == "5":
                break
            else:
                DisplayMessages.display_invalid_choice("users")

    @staticmethod
    def run_clients_menu(db):
        """Runs the Clients submenu loop and delegates actions to ClientController."""
        while True:
            choice = MenuView.display_clients_menu()
            if choice == "1":
                ClientController.list_clients(db)
            elif choice == "2":
                ClientController.create_client(db)
            elif choice == "3":
                ClientController.update_client(db)
            elif choice == "4":
                break
            else:
                DisplayMessages.display_invalid_choice("clients")

    @staticmethod
    def run_contracts_menu(db):
        """Runs the Contracts submenu loop and delegates actions to ContractController."""
        while True:
            choice = MenuView.display_contracts_menu()
            if choice == "1":
                ContractController.list_contracts(db)
            elif choice == "2":
                ContractController.create_contract(db)
            elif choice == "3":
                ContractController.update_contract(db)
            elif choice == "4":
                break
            else:
                DisplayMessages.display_invalid_choice("contracts")

    @staticmethod
    def run_events_menu(db):
        """Runs the Events submenu loop and delegates actions to EventController."""
        while True:
            choice = MenuView.display_events_menu()
            if choice == "1":
                EventController.list_events(db)
            elif choice == "2":
                EventController.create_event(db)
            elif choice == "3":
                EventController.update_event(db)
            elif choice == "4":
                break
            else:
                DisplayMessages.display_invalid_choice("events")


class UserController:
    """Static methods for user-related controller operations."""

    @staticmethod
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
            user_data = UserView.prompt_user_creation()

            # Step 2: Delegate user validation and object creation to the model layer
            user = User.create(
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
            DisplayMessages.display_success(f"User created: {user.first_name} {user.last_name} (ID: {user.user_id})")

        except ValueError as e:
            # Handle business logic validation errors
            db.rollback()
            DisplayMessages.display_error(str(e))

        except Exception:
            # Handle database/technical errors
            db.rollback()
            DisplayMessages.display_error("DATABASE_ERROR")
            raise

    @staticmethod
    def list_users(db):
        """
            Controller method to list all users in the CRM system.
            This method orchestrates the retrieval of user data from the database,
            handles potential errors, and delegates the display to the view layer.

            Args:
                db (sqlalchemy.orm.Session): Active SQLAlchemy database session for data retrieval.

            Error Handling:
                - Catches unexpected errors and provides a generic error message.
                - Uses ErrorMessages enum for consistent error messaging across the application.
            """
        try:
            # Step 1: Retrieve users from the database (model layer)
            users = User.get_all(db)

            # Step 2: Delegate display to the view layer
            UserView.list_users(users)

        except Exception:
            # Handle unexpected errors
            DisplayMessages.display_error("DATABASE_ERROR")
            raise

    @staticmethod
    def update(db):
        """
        Orchestrates the update of a user in the CRM system.
        Steps:
          1. Prompts the user for the user ID and updated data (via UserView).
          2. Retrieves the user from the database (via User.get_by_id).
          3. Updates the user (via User.update).
          4. Handles database transactions (commit/rollback).
          5. Delegates success/error feedback to the view.

        Args:
            db (sqlalchemy.orm.Session): Active database session.
        """
        try:
            # Step 1: Prompt for user ID and updated data (view layer)
            user_id = click.prompt("Enter the ID of the user to update", type=int)
            user = User.get_by_id(db, user_id)
            if not user:
                DisplayMessages.display_error("USER_NOT_FOUND")
                return

            # Step 2: Get updated data from the user (view layer)
            updated_data = UserView.prompt_update(user)

            # Step 3: Update the user (model layer)
            user.update(db, **updated_data)

            # Step 4: Commit changes (controller responsibility)
            db.commit()
            db.refresh(user)

            # Step 5: Display success (view layer)
            DisplayMessages.display_success(f"User updated: {user.username} (ID: {user.user_id})")

        except ValueError as e:
            # Handle validation errors (e.g., duplicate email/username)
            db.rollback()
            DisplayMessages.display_error(str(e))

        except Exception:
            # Handle unexpected errors
            db.rollback()
            DisplayMessages.display_error("DATABASE_ERROR")


if __name__ == "__main__":
    MenuController.run_main_menu(db)

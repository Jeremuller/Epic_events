from epic_events.models import User, Client, Contract, Event
from epic_events.views import (DisplayMessages, UserView, ClientView, ContractView, EventView, MenuView, LoginView)
from epic_events.auth import hash_password, verify_password, SessionContext
from epic_events.database import SessionLocal
from epic_events.permissions import requires_authentication, management_only, support_only, commercial_only, \
    role_permission

db = SessionLocal()


class MenuController:
    """Static methods for handling menu navigation and controller delegation."""

    @staticmethod
    @requires_authentication
    def run_main_menu(db, session):
        """
        Runs the main menu loop and delegates actions to submenus.
        Args:
            db (sqlalchemy.orm.Session): Database session for data operations.
            session (SessionContext):
            Authentication context of the currently logged-in user.
            Contains identity and role information used for permission checks.
        """
        while True:
            choice = MenuView.display_main_menu()
            if choice == "1":
                MenuController.run_users_menu(db, session)
            elif choice == "2":
                MenuController.run_clients_menu(db, session)
            elif choice == "3":
                MenuController.run_contracts_menu(db, session)
            elif choice == "4":
                MenuController.run_events_menu(db, session)
            elif choice == "5":
                if LoginController.logout(session):
                    DisplayMessages.display_goodbye()
                    break
            else:
                DisplayMessages.display_invalid_choice("main")

    @staticmethod
    @requires_authentication
    def run_users_menu(db, session):
        """Runs the Users submenu loop and delegates actions to UserController."""
        while True:
            choice = MenuView.display_users_menu()
            if choice == "1":
                UserController.create_user(db, session)
            elif choice == "2":
                UserController.update_user(db, session)
            elif choice == "3":
                UserController.delete_user(db, session)
            elif choice == "4":
                break
            else:
                DisplayMessages.display_invalid_choice("users")

    @staticmethod
    @requires_authentication
    def run_clients_menu(db, session):
        """Runs the Clients submenu loop and delegates actions to ClientController."""
        while True:
            choice = MenuView.display_clients_menu()
            if choice == "1":
                ClientController.list_clients(db, session)
            elif choice == "2":
                ClientController.create_client(db, session)
            elif choice == "3":
                ClientController.update_client(db, session)
            elif choice == "4":
                break
            else:
                DisplayMessages.display_invalid_choice("clients")

    @staticmethod
    @requires_authentication
    def run_contracts_menu(db, session):
        """Runs the Contracts submenu loop and delegates actions to ContractController."""
        while True:
            choice = MenuView.display_contracts_menu()
            if choice == "1":
                ContractController.list_contracts(db, session)
            elif choice == "2":
                ContractController.create_contract(db, session)
            elif choice == "3":
                ContractController.update_contract(db, session)
            elif choice == "4":
                break
            else:
                DisplayMessages.display_invalid_choice("contracts")

    @staticmethod
    @requires_authentication
    def run_events_menu(db, session):
        """Runs the Events submenu loop and delegates actions to EventController."""
        while True:
            choice = MenuView.display_events_menu()
            if choice == "1":
                EventController.list_events(db, session)
            elif choice == "2":
                EventController.create_event(db, session)
            elif choice == "3":
                EventController.update_event(db, session)
            elif choice == "4":
                break
            else:
                DisplayMessages.display_invalid_choice("events")


class LoginController:
    @staticmethod
    def login(db):
        """
        Authenticate a user using username and password.

        This controller method orchestrates the full login process:
        - Prompts the user for credentials via the view layer
        - Retrieves the user from the database
        - Verifies the provided password against the stored hash
        - Returns a SessionContext object upon successful authentication

        Args:
            db (Session): SQLAlchemy database session.

        Returns:
            SessionContext | None:
                - A SessionContext instance if authentication succeeds
                - None if authentication fails (invalid credentials)

        Security notes:
            - Password verification is delegated to the auth layer (bcrypt-based)
            - No User ORM object is returned to avoid leaking database entities
            - Error messages are generic to prevent user enumeration
        """

        credentials = LoginView.prompt_login()
        username = credentials["username"]
        password = credentials["password"]

        user = User.get_by_username(db, username)

        if not user:
            DisplayMessages.display_error("INVALID_CREDENTIALS")
            return None

        if not verify_password(password, user.password_hash):
            DisplayMessages.display_error("INVALID_CREDENTIALS")
            return None

        session = SessionContext(
            username=user.username,
            user_id=user.user_id,
            role=user.role,
            is_authenticated=True
        )

        DisplayMessages.display_success(
            f"Authentication succeeded. Welcome {session.username}."
        )

        return session

    @staticmethod
    def logout(session):
        """
        Logs out the current user with a confirmation prompt.

        Workflow:
            1. Asks the user to confirm logout via SessionView.
            2. Returns True if confirmed, False otherwise.
            3. Display of goodbye message is handled by the menu.

        Args:
            session (SessionContext): The current user's session context.

        Returns:
            bool: True if logout confirmed, False otherwise.
        """
        # Ask the user for confirmation using the view
        confirm = MenuView.logout_confirmation()
        return confirm


class UserController:
    """Static methods for user-related controller operations."""

    @staticmethod
    @management_only
    def create_user(db, session):
        """
        Controller function to orchestrate the creation of a new user in the CRM system.
        This function acts as an intermediary between the view (user interaction) and the model (business logic).
        It handles transaction management (commit/rollback) and error feedback.

        Args:
            db (sqlalchemy.orm.Session): Active database session for persistence operations.
            session (SessionContext):
            Authentication context of the currently logged-in user.
            Contains identity and role information used for permission checks.

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

            # Step 2: Hash the plaintext password
            password_hash = hash_password(user_data["password"])

            # Step 3: Delegate user validation and object creation to the model layer
            user = User.create(
                db=db,
                username=user_data["username"],
                first_name=user_data["first_name"],
                last_name=user_data["last_name"],
                email=user_data["email"],
                role=user_data["role"],
                password_hash=password_hash,
            )

            # Step 3: Persist the user
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
    @management_only
    def update_user(db, session):
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
            session (SessionContext):
            Authentication context of the currently logged-in user.
            Contains identity and role information used for permission checks.
        """
        try:
            # Step 1: Prompt for user ID and updated data
            users = User.get_all(db)
            UserView.display_user_id_list(users)
            user_id = MenuView.prompt_for_id("user")
            user = User.get_by_id(db, user_id)
            if not user:
                DisplayMessages.display_error("USER_NOT_FOUND")
                return

            # Step 2: Get updated data from the user
            updated_data = UserView.prompt_update(user)

            # Step 3: Update the user
            user.update(db, **updated_data)

            # Step 4: Commit changes
            db.commit()
            db.refresh(user)

            # Step 5: Display success
            DisplayMessages.display_success(f"User updated: {user.username} (ID: {user.user_id})")

        except ValueError as e:
            # Handle validation errors (e.g., duplicate email/username)
            db.rollback()
            DisplayMessages.display_error(str(e))

        except Exception:
            # Handle unexpected errors
            db.rollback()
            DisplayMessages.display_error("DATABASE_ERROR")
            raise

    @staticmethod
    @management_only
    def delete_user(db, session):
        """
        Orchestrates the deletion of a user in the CRM system.
        Steps:
          1. Prompts the user for the user ID (via MenuView.prompt_for_id).
          2. Retrieves the user from the database (via User.get_by_id).
          3. Asks for confirmation (via UserView.prompt_delete_confirmation).
          4. Deletes the user (via db.delete) and handles transactions.
          5. Delegates success/error feedback to the view.

        Args:
            db (sqlalchemy.orm.Session): Active database session.
            session (SessionContext):
            Authentication context of the currently logged-in user.
            Contains identity and role information used for permission checks.
        """
        try:
            # Step 1: Prompt for user ID
            users = User.get_all(db)
            UserView.display_user_id_list(users)
            user_id = MenuView.prompt_for_id("user")

            # Step 2: Retrieve the user
            user = User.get_by_id(db, user_id)
            if not user:
                DisplayMessages.display_error("USER_NOT_FOUND")
                return

            # Step 3: Ask for confirmation
            if not UserView.prompt_delete_confirmation(user):
                DisplayMessages.display_success("Deletion cancelled.")
                return

            # Step 4: Handle dependencies
            user.delete(db)

            # Step 5: Delete the user and handle transaction
            db.delete(user)
            db.commit()

            # Step 6: Display success
            DisplayMessages.display_success(
                f"User deleted: {user.username} (ID: {user.user_id})"
            )

        except ValueError as e:
            # Handle model-specific errors (e.g., dependency handling failed)
            db.rollback()
            DisplayMessages.display_error(str(e))

        except Exception:
            # Rollback on any error
            db.rollback()
            DisplayMessages.display_error("DATABASE_ERROR")
            raise


class ClientController:
    """Static methods for client-related controller operations."""

    @staticmethod
    @requires_authentication
    def list_clients(db, session):
        """
        Controller method to list all clients in the CRM system.
        This method orchestrates the retrieval of client data from the database,
        handles potential errors, and delegates the display to the view layer.

        Args:
            db (sqlalchemy.orm.Session): Active SQLAlchemy database session for data retrieval.
            session (SessionContext):
            Authentication context of the currently logged-in user.
            Contains identity and role information used for permission checks.

        Workflow:
            1. Retrieves all clients from the database (via Client.get_all).
            2. Delegates the display of clients to the view layer (via ClientView.list_clients).
            3. Handles any unexpected errors and provides feedback via DisplayMessages.

        Error Handling:
            - Catches unexpected errors (e.g., database issues) and displays a generic error message.
            - Uses ErrorMessages enum for consistent error messaging across the application.
            - Re-raises the exception for potential higher-level handling (e.g., logging).
        """

        try:
            # Step 1: Retrieve clients from the database (model layer)
            clients = Client.get_all(db)

            # Step 2: Delegate display to the view layer
            ClientView.list_clients(clients)

        except Exception:
            # Handle unexpected errors
            DisplayMessages.display_error("DATABASE_ERROR")
            raise

    @staticmethod
    @commercial_only
    def create_client(db, session):
        """
        Controller function to orchestrate the creation of a new client in the CRM system.
        This function acts as an intermediary between the view (user interaction) and the model (business logic).
        It handles transaction management (commit/rollback) and error feedback.

        Args:
            db (sqlalchemy.orm.Session): Active database session for persistence operations.
            session (SessionContext):
            Authentication context of the currently logged-in user.
            Contains identity and role information used for permission checks.

        Workflow:
            1. Delegates client input collection to the view layer (`prompt_client_creation`).
            2. Delegates client validation and object creation to the model layer (`Client.create`).
            3. Manages database persistence (commit/rollback) based on operation success/failure.
            4. Delegates success/error feedback to the view layer (`display_success`/`display_error`).

        Transaction Management:
            - Commits changes to the database if the operation succeeds.
            - Rolls back changes if any error occurs (validation or database error).
            - Ensures data consistency by handling exceptions explicitly.

        Error Handling:
            - Catches `ValueError` for business logic validation errors (e.g., duplicate email, missing fields).
            - Catches generic `Exception` for database/technical errors.
            - Delegates error display to the view layer with appropriate error keys.
        """
        try:
            # Step 1: Delegate client input to the view layer
            client_data = ClientView.prompt_client_creation()

            # Step 2: Delegate client validation and object creation to the model layer
            client = Client.create(
                db=db,
                first_name=client_data["first_name"],
                last_name=client_data["last_name"],
                email=client_data["email"],
                commercial_contact_id=session.user_id,
                business_name=client_data.get("business_name"),
                telephone=client_data.get("telephone")
            )

            # Step 3: Persist the client (controller responsibility)
            db.add(client)
            db.commit()
            db.refresh(client)

            # Step 4: Delegate success feedback to the view layer
            DisplayMessages.display_success(
                f"Client created: {client.business_name or f'{client.first_name} {client.last_name}'} "
                f"(ID: {client.client_id})"
            )

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
    @commercial_only
    def update_client(db, session):
        """
            Orchestrates the update of a client in the CRM system.
            Steps:
              1. Prompts the user for the client ID (via MenuView).
              1b. Check if the commercial is assigned to this client for permission purposes.
              2. Retrieves the client from the database (via Client.get_by_id).
              3. Prompts for updated client data (via ClientView).
              4. Validates and updates the client (via Client.update).
              5. Handles database transactions (commit/rollback).
              6. Delegates success/error feedback to the view.

            Args:
                db (sqlalchemy.orm.Session): Active database session.
                session (SessionContext):
                Authentication context of the currently logged-in user.
                Contains identity and role information used for permission checks.
            """
        try:
            # Step 1: Prompt for client ID
            client_id = MenuView.prompt_for_id("client")
            client = Client.get_by_id(db, client_id)
            if not client:
                DisplayMessages.display_error("CLIENT_NOT_FOUND")
                return
            # Step 1b: Verify commercial is assigned to this client
            if client.commercial_contact_id != session.user_id:
                DisplayMessages.display_error("ACCESS_DENIED")
                return
            # Step 2: Get updated data from the user
            updated_data = ClientView.prompt_update(client)

            # Step 3: Update the client (model layer)
            client.update(db, **updated_data)

            # Step 4: Commit changes (controller responsibility)
            db.commit()
            db.refresh(client)

            # Step 5: Display success
            DisplayMessages.display_success(
                f"Client updated: {client.business_name or f'{client.first_name} {client.last_name}'} "
                f"(ID: {client.client_id})"
            )

        except ValueError as e:
            # Handle validation errors (e.g., duplicate email)
            db.rollback()
            DisplayMessages.display_error(str(e))

        except Exception:
            # Handle unexpected errors
            db.rollback()
            DisplayMessages.display_error("DATABASE_ERROR")
            raise


class ContractController:
    """Static methods for contract-related controller operations."""

    @staticmethod
    @requires_authentication
    def list_contracts(db, session):
        """
        Controller method to list all contracts in the CRM system.
        This method orchestrates the retrieval of contract data from the database,
        handles potential errors, and delegates the display to the view layer.

        Args:
            db (sqlalchemy.orm.Session): Active SQLAlchemy database session for data retrieval.
            session (SessionContext):
            Authentication context of the currently logged-in user.
            Contains identity and role information used for permission checks.

        Workflow:
            1. Retrieves all contracts from the database (via Contract.get_all).
            2. Delegates the display of contracts to the view layer (via ContractView.list_contracts).
            3. Handles any unexpected errors and provides feedback via DisplayMessages.

        Error Handling:
            - Catches unexpected errors (e.g., database issues) and displays a generic error message.
            - Uses ErrorMessages enum for consistent error messaging across the application.
            - Re-raises the exception for potential higher-level handling (e.g., logging).
        """
        try:
            # Step 1: Retrieve contracts from the database (model layer)
            contracts = Contract.get_all(db)

            # Step 2: Delegate display to the view layer
            ContractView.list_contracts(contracts)

        except Exception:
            # Handle unexpected errors
            DisplayMessages.display_error("DATABASE_ERROR")
            raise

    @staticmethod
    @commercial_only
    def list_pending_contracts(db, session):
        """
        Lists all pending contracts for the commercial user.
        Calls the model to retrieve data and displays them using list_contracts.
        """
        contracts = Contract.get_pending_contracts(db)
        ContractView.list_contracts(contracts)

    @staticmethod
    @management_only
    def create_contract(db, session):
        """
        Controller function to orchestrate the creation of a new contract in the CRM system.
        This function acts as an intermediary between the view (user interaction) and the model (business logic).
        It handles transaction management (commit/rollback) and error feedback.

        Args:
            db (sqlalchemy.orm.Session): Active database session for persistence operations.
            session (SessionContext):
            Authentication context of the currently logged-in user.
            Contains identity and role information used for permission checks.

        Workflow:
            1. Delegates contract input collection to the view layer (`prompt_contract_creation`).
            2. Delegates contract validation and object creation to the model layer (`Contract.create`).
            3. Manages database persistence (commit/rollback) based on operation success/failure.
            4. Delegates success/error feedback to the view layer (`display_success`/`display_error`).

        Transaction Management:
            - Commits changes to the database if the operation succeeds.
            - Rolls back changes if any error occurs (validation or database error).
            - Ensures data consistency by handling exceptions explicitly.

        Error Handling:
            - Catches `ValueError` for business logic validation errors (e.g., invalid client/commercial contact).
            - Catches generic `Exception` for database/technical errors.
            - Delegates error display to the view layer with appropriate error keys.
        """
        try:
            # Step 1: Delegate contract input to the view layer
            contract_data = ContractView.prompt_contract_creation()

            # Step 2: Delegate contract validation and object creation to the model layer
            contract = Contract.create(
                db=db,
                total_price=contract_data["total_price"],
                rest_to_pay=contract_data["rest_to_pay"],
                client_id=contract_data["client_id"],
                commercial_contact_id=contract_data["commercial_contact_id"],
                signed=contract_data.get("signed", False)
            )

            # Step 3: Persist the contract (controller responsibility)
            db.add(contract)
            db.commit()
            db.refresh(contract)

            # Step 4: Delegate success feedback to the view layer
            DisplayMessages.display_success(
                f"Contract created: ID {contract.contract_id} | "
                f"Client: {contract.client.business_name if contract.client else 'N/A'} | "
                f"Total: {contract.total_price}€"
            )

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
    @role_permission(["management", "commercial"])
    def update_contract(db, session):
        """
        Orchestrates the update of a contract in the CRM system.
        Steps:
          1. Prompts the user for the contract ID (via MenuView).
          2. Retrieves the contract from the database (via Contract.get_by_id).
          3. Prompts for updated contract data (via ContractView).
          4. Validates and updates the contract (via Contract.update).
          5. Handles database transactions (commit/rollback).
          6. Delegates success/error feedback to the view.

        Args:
            db (sqlalchemy.orm.Session): Active database session.
            session (SessionContext):
            Authentication context of the currently logged-in user.
            Contains identity and role information used for permission checks.
        """
        try:
            # Step 1: Prompt for contract ID
            contract_id = MenuView.prompt_for_id("contract")
            contract = Contract.get_by_id(db, contract_id)
            if not contract:
                DisplayMessages.display_error("CONTRACT_NOT_FOUND")
                return
            # Step 1b: Role-specific assignment check
            if session.role == "commercial":
                if contract.client.commercial_contact_id != session.user_id:
                    DisplayMessages.display_error("ACCESS_DENIED")
                    return
            # Step 2: Get updated data from the user
            updated_data = ContractView.prompt_update(contract)

            # Step 3: Update the contract (model layer)
            contract.update(db, **updated_data)

            # Step 4: Commit changes (controller responsibility)
            db.commit()
            db.refresh(contract)

            # Step 5: Display success
            DisplayMessages.display_success(
                f"Contract updated: ID {contract.contract_id} | "
                f"Client: {contract.client.business_name if contract.client else 'N/A'} | "
                f"Total: {contract.total_price}€"
            )

        except ValueError as e:
            # Handle validation errors
            db.rollback()
            DisplayMessages.display_error(str(e))

        except Exception:
            # Handle unexpected errors
            db.rollback()
            DisplayMessages.display_error("DATABASE_ERROR")
            raise


class EventController:
    """Static methods for event-related controller operations."""

    @staticmethod
    @requires_authentication
    def list_events(db, session):
        """
        Controller method to list all events in the CRM system.
        This method orchestrates the retrieval of event data from the database,
        handles potential errors, and delegates the display to the view layer.

        Args:
            db (sqlalchemy.orm.Session): Active SQLAlchemy database session for data retrieval.
            session (SessionContext):
            Authentication context of the currently logged-in user.
            Contains identity and role information used for permission checks.

        Workflow:
            1. Retrieves all events from the database (via Event.get_all).
            2. Delegates the display of events to the view layer (via EventView.list_events).
            3. Handles any unexpected errors and provides feedback via DisplayMessages.
        """
        try:
            # Step 1: Retrieve events from the database (model layer)
            events = Event.get_all(db)

            # Step 2: Delegate display to the view layer
            EventView.list_events(events)

        except Exception:
            # Handle unexpected errors
            DisplayMessages.display_error("DATABASE_ERROR")
            raise

    @staticmethod
    @support_only
    def list_my_events(db, session):
        """
        Retrieves and displays all events assigned to the logged-in support user.
        """
        events = Event.get_assigned_to_user(db, session.user_id)

        EventView.list_events(events)

    @staticmethod
    @management_only
    def show_unassigned_events(db, session):
        """
        Retrieves and displays events without a support contact assigned.
        Only accessible to management.

        Args:
            db (Session): SQLAlchemy database session.
            session (SessionContext): Current authenticated user session.
        """
        events = Event.get_unassigned_events(db)
        EventView.list_events(events)

    @staticmethod
    @commercial_only
    def create_event(db, session):
        """
        Controller function to orchestrate the creation of a new event in the CRM system.
        This function acts as an intermediary between the view (user interaction) and the model (business logic).
        It handles transaction management (commit/rollback) and error feedback.

        Args:
            db (sqlalchemy.orm.Session): Active database session for persistence operations.
            session (SessionContext):
            Authentication context of the currently logged-in user.
            Contains identity and role information used for permission checks.

        Workflow:
            1. Delegates event input collection to the view layer (`prompt_event_creation`).
            2. Delegates event validation and object creation to the model layer (`Event.create`).
            3. Manages database persistence (commit/rollback) based on operation success/failure.
            4. Delegates success/error feedback to the view layer.
        """
        try:
            # Step 1: Delegate event input to the view layer
            event_data = EventView.prompt_event_creation()

            # Step 1b: Check that the commercial is assigned to this client
            client = db.query(Client).filter_by(client_id=event_data["client_id"]).first()
            if not client:
                raise ValueError("CLIENT_NOT_FOUND")
            if client.commercial_contact_id != session.user_id:
                raise ValueError("ACCESS_DENIED")

            # Step 2: Delegate event validation and object creation to the model layer
            event = Event.create(
                db=db,
                name=event_data["name"],
                notes=event_data.get("notes"),
                start_datetime=event_data["start_datetime"],
                end_datetime=event_data["end_datetime"],
                location=event_data.get("location"),
                attendees=event_data["attendees"],
                client_id=event_data["client_id"]
            )

            # Step 3: Persist the event (controller responsibility)
            db.add(event)
            db.commit()
            db.refresh(event)

            # Step 4: Delegate success feedback
            DisplayMessages.display_success(
                f"Event created: {event.name} (ID: {event.event_id})"
            )

        except ValueError as e:
            db.rollback()
            DisplayMessages.display_error(str(e))

        except Exception:
            db.rollback()
            DisplayMessages.display_error("DATABASE_ERROR")
            raise

    @staticmethod
    @support_only
    def update_event(db, session):
        """
        Orchestrates the update of an event in the CRM system.
        Steps:
          1. Prompts the user for the event ID (via MenuView).
          2. Retrieves the event from the database (via Event.get_by_id).
          3. Prompts for updated event data (via EventView).
          4. Validates and updates the event (via Event.update).
          5. Handles database transactions (commit/rollback).
          6. Delegates success/error feedback to the view.

        Args:
            db (sqlalchemy.orm.Session): Active database session.
            session (SessionContext):
            Authentication context of the currently logged-in user.
            Contains identity and role information used for permission checks.
        """
        try:
            # Step 1: Prompt for event ID
            event_id = MenuView.prompt_for_id("event")
            event = Event.get_by_id(db, event_id)
            if not event:
                DisplayMessages.display_error("EVENT_NOT_FOUND")
                return
            # Step 2: Vérification “requires_assignment” inline
            if event.support_contact_id != session.user_id:
                raise ValueError("ACCESS_DENIED")
            # Step 3: Get updated data from the user
            updated_data = EventView.prompt_update(event)

            # Step 4: Update the event (model layer)
            event.update(db, **updated_data)

            # Step 5: Commit changes (controller responsibility)
            db.commit()
            db.refresh(event)

            # Step 6: Display success
            DisplayMessages.display_success(
                f"Event updated: {event.name} (ID: {event.event_id})"
            )

        except ValueError as e:
            # Handle validation errors
            db.rollback()
            DisplayMessages.display_error(str(e))

        except Exception:
            # Handle unexpected errors
            db.rollback()
            DisplayMessages.display_error("DATABASE_ERROR")
            raise

    @staticmethod
    @management_only
    def assign_support(db, session):
        """
    Allows a manager to assign or change a support contact for any event.

    Workflow:
        1. Prompts the user for the event ID (via MenuView).
        2. Retrieves the event from the database (via Event.get_by_id).
        3. Checks that the event exists.
        4. Prompts the user for the support contact ID (via MenuView).
        5. Validates that the support user exists.
        6. Updates the event with the new support_contact_id (via Event.update).
        7. Handles database transactions (commit/rollback).
        8. Displays success or error messages via DisplayMessages.

    Raises:
        ValueError: If the event is not found or the support user does not exist.
        Exception: For unexpected database errors.
    """
        try:
            event_id = MenuView.prompt_for_id("event")
            event = Event.get_by_id(db, event_id)
            if not event:
                raise ValueError("EVENT_NOT_FOUND")

            support_id = MenuView.prompt_for_contact_id("support user")
            support_user = db.query(User).filter_by(user_id=support_id).first()
            if not support_user:
                raise ValueError("CONTACT_NOT_FOUND")

            event.update(db, support_contact_id=support_id)

            db.commit()
            db.refresh(event)

            DisplayMessages.display_success(
                f"Support {support_user.username} assigned to event '{event.name}' (ID: {event.event_id})"
            )

        except ValueError as e:
            db.rollback()
            DisplayMessages.display_error(str(e))

        except Exception:
            db.rollback()
            DisplayMessages.display_error("DATABASE_ERROR")
            raise


if __name__ == "__main__":
    session = LoginController.login(db)

    if not session or not session.is_authenticated:
        DisplayMessages.display_error("AUTHENTICATION_REQUIRED")
        exit()

    MenuController.run_main_menu(db, session)

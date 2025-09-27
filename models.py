from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, DECIMAL, Boolean, Text, Enum
from sqlalchemy.orm import relationship, Session
from Epic_events.database import Base
from datetime import datetime
import pytest


class User(Base):
    """
        Represents a user in the CRM system (e.g., commercial, management, support).

        Attributes:
            user_id (int): Primary key and unique identifier for the user.
            first_name (str): User's first name (max 100 characters).
            last_name (str): User's last name (max 100 characters).
            username (str): Unique username for authentication (max 100 characters).
            password (str): Hashed password for authentication (max 100 characters).
            email (str): Unique email address of the user.
            role (str): Role of the user (commercial/management/support).

        Relationships:
            clients (list[Client]): List of clients managed by the user (one-to-many).
            contracts (list[Contract]): List of contracts managed by the user (one-to-many).
            events (list[Event]): List of events managed by the user (one-to-many).
        """

    __tablename__ = 'users'

    # Columns definition
    user_id = Column(Integer, primary_key=True, index=True, nullable=False)
    first_name = Column(String(100))
    last_name = Column(String(100))
    username = Column(String(100), unique=True)
    password = Column(String(100))
    email = Column(String(100), unique=True)
    role = Column(Enum('commercial', 'management', 'support'))

    # Relationships definition
    clients = relationship("Client", back_populates="commercial_contact")
    contracts = relationship("Contract", back_populates="commercial_contact")
    events = relationship("Event", back_populates="support_contact")

    @classmethod
    def create_user(cls, db: Session, username: str, first_name: str, last_name: str, email: str, role: str,
                    password: str = "default_hashed_password"):
        """
        Creates a new user in the database.

        Args:
            db (Session): SQLAlchemy database session.
            username (str): Unique username for authentication (max 100 characters).
            first_name (str): User's first name (max 100 characters).
            last_name (str): User's last name (max 100 characters).
            email (str): Unique email address of the user.
            role (str): Role of the user (commercial/management/support).
            password (str, optional): Hashed password for authentication.

        Returns:
            User: The newly created User object.
        """

        # Check for duplicate username
        if db.query(cls).filter_by(username=username).first():
            raise ValueError(f"Username '{username}' is already taken.")

        # Check for duplicate email
        if db.query(cls).filter_by(email=email).first():
            raise ValueError(f"Email '{email}' is already taken.")

        # Check for empty required fields
        if not username or not first_name or not last_name or not email or not role:
            raise ValueError("Required fields cannot be empty.")

        # Validate role
        valid_roles = ["commercial", "management", "support"]
        if role not in valid_roles:
            raise ValueError(f"Invalid role. Must be one of: {', '.join(valid_roles)}")

        user = cls(
            username=username,
            first_name=first_name,
            last_name=last_name,
            email=email,
            role=role,
            password=password
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    @classmethod
    def get_all(cls, db: Session):
        """
        Retrieves all users from the database.

        Args:
            db (Session): SQLAlchemy database session.

        Returns:
            list[User]: List of all User objects.
        """
        return db.query(cls).all()

    @classmethod
    def get_by_id(cls, db: Session, user_id: int):
        """
        Retrieves a user by their ID.

        Args:
            db (Session): SQLAlchemy database session.
            user_id (int): The ID of the user to retrieve.

        Returns:
            User: The User object if found, None otherwise.
        """
        return db.query(cls).filter_by(user_id=user_id).first()

    def update(self, db: Session, first_name: str = None, last_name: str = None, email: str = None, role: str = None):
        """
        Updates the user's information with uniqueness checks for email.

        Args:
            db (Session): SQLAlchemy database session.
            first_name (str, optional): New first name.
            last_name (str, optional): New last name.
            email (str, optional): New email address.
            role (str, optional): New role.

        Raises:
            ValueError: If the new email is already taken by another user.
        """
        if email:
            # Check if the new email is already taken by another user
            existing_user = db.query(User).filter(User.email == email, User.user_id != self.user_id).first()
            if existing_user:
                raise ValueError(f"Email '{email}' is already taken by another user.")

        if first_name:
            self.first_name = first_name
        if last_name:
            self.last_name = last_name
        if email:
            self.email = email
        if role:
            # Validate role if updated
            valid_roles = ["commercial", "management", "support"]
            if role not in valid_roles:
                raise ValueError(f"Invalid role. Must be one of: {', '.join(valid_roles)}")
            self.role = role

        db.commit()
        db.refresh(self)
        return self

    def delete(self, db: Session):
        """
        Deletes the user from the database after handling dependencies.

        Args:
            db (Session): SQLAlchemy database session.

        Notes:
            - Clients: Sets their commercial_contact_id to None.
            - Contracts: Sets their commercial_contact_id to None.
            - Events: Sets their support_contact_id to None.
        """
        # Handle clients: set commercial_contact_id to None
        for client in self.clients:
            client.commercial_contact_id = None

        # Handle contracts: set commercial_contact_id to None
        for contract in self.contracts:
            contract.commercial_contact_id = None

        # Handle events: set support_contact_id to None
        for event in self.events:
            event.support_contact_id = None

        db.commit()  # Save changes before deletion

        db.delete(self)
        db.commit()


class Client(Base):
    """
        Represents a client in the CRM system.

        This class maps to the 'clients' table in the database and defines the attributes
        and relationships of a client entity.

        Attributes:
            client_id (int): Primary key and unique identifier for the client.
            first_name (str): Client's first name (max 100 characters).
            last_name (str): Client's last name (max 100 characters).
            business_name (str): Name of the client's business (max 200 characters).
            telephone (str): Client's phone number (max 100 characters).
            email (str): Client's email address (unique, optional).
            first_contact (DateTime): Date and time of the first contact with the client.
            last_update (DateTime): Date and time of the last update for the client.
            commercial_contact_id (int): Foreign key referencing the commercial user responsible for the contract.

        Relationships:
            contracts (list[Contract]): One-to-many relationship with Contract.
                                   A client can have multiple contracts.
            commercial_contact (User): Many-to-one relationship with User.
                                   A client is managed by exactly one commercial user.
            events (list[Event]): One-to-many relationship with Event.
                             A client can have multiple events.
    """

    __tablename__ = 'clients'

    # Columns definition
    client_id = Column(Integer, primary_key=True, index=True, nullable=False)
    first_name = Column(String(100))
    last_name = Column(String(100))
    business_name = Column(String(200))
    telephone = Column(String(100))
    email = Column(String(100), unique=True)
    first_contact = Column(DateTime)
    last_update = Column(DateTime)
    commercial_contact_id = Column(Integer, ForeignKey('users.user_id'), nullable=True)

    # Relationship definition
    contracts = relationship("Contract", back_populates="client")
    commercial_contact = relationship("User", back_populates="clients")
    events = relationship("Event", back_populates="client")

    @classmethod
    def create(cls, db: Session, first_name: str, last_name: str, email: str, commercial_contact_id: int,
               business_name: str = None, telephone: str = None):
        """
        Creates a new client linked to a commercial user.

        Args:
            db (Session): SQLAlchemy database session.
            first_name (str): Client's first name.
            last_name (str): Client's last name.
            email (str): Client's email address.
            commercial_contact_id (int): ID of the commercial user responsible.
            business_name (str, optional): Client's business name.
            telephone (str, optional): Client's phone number.

        Returns:
            Client: The created Client object.
        """
        client = cls(
            first_name=first_name,
            last_name=last_name,
            email=email,
            commercial_contact_id=commercial_contact_id,
            business_name=business_name,
            telephone=telephone,
            first_contact=datetime.now(),
            last_update=datetime.now()
        )
        db.add(client)
        db.commit()
        db.refresh(client)
        return client

    def update(self, db: Session, first_name: str = None, last_name: str = None, email: str = None,
               business_name: str = None, telephone: str = None, commercial_contact_id: int = None):
        """
        Updates the client's information in the database.

        Args:
            db (Session): SQLAlchemy database session.
            first_name (str, optional): New first name.
            last_name (str, optional): New last name.
            email (str, optional): New email address.
            business_name (str, optional): New business name.
            telephone (str, optional): New phone number.
            commercial_contact_id (int, optional): New commercial contact ID.

        Returns:
            Client: The updated Client object.
        """
        if first_name:
            self.first_name = first_name
        if last_name:
            self.last_name = last_name
        if email:
            self.email = email
        if business_name:
            self.business_name = business_name
        if telephone:
            self.telephone = telephone
        if commercial_contact_id:
            self.commercial_contact_id = commercial_contact_id
        self.last_update = datetime.now()
        db.commit()
        db.refresh(self)
        return self

    @classmethod
    def get_all(cls, db: Session):
        """
        Retrieves all clients from the database.

        Args:
            db (Session): SQLAlchemy database session.

        Returns:
            list[Client]: List of all Client objects.
        """
        return db.query(cls).all()

    @classmethod
    def get_by_id(cls, db: Session, client_id: int):
        """
            Retrieves a client by their ID.

            Args:
            db (Session): SQLAlchemy database session.
            client_id (int): The ID of the client to retrieve.

            Returns:
            Client: The Client object if found, None otherwise.

        """

        return db.query(cls).filter_by(client_id=client_id).first()


class Contract(Base):
    """
        Represents a contract in the CRM system.

        This class maps to the 'contracts' table in the database and defines the attributes
        and relationships of a contract entity.

        Attributes:
            contract_id (int): Primary key and unique identifier for the contract.
            total_price (DECIMAL): Total amount of the contract (e.g., 1000.00).
            rest_to_pay (DECIMAL): Remaining amount to be paid by the client.
            creation (DateTime): Date and time when the contract was created.
            signed (Boolean): Status indicating whether the contract is signed (True/False).
            commercial_contact_id (int): Foreign key referencing the commercial user responsible for the contract.

        Relationships:
            client (Client): Many-to-one relationship with Client.
                        A contract belongs to exactly one client.
            commercial_contact (User): Many-to-one relationship with User.
                                       A contract is managed by exactly one commercial contact (user).
    """

    __tablename__ = 'contracts'

    # Columns definition
    contract_id = Column(Integer, primary_key=True, index=True, nullable=False)
    total_price = Column(DECIMAL(10, 2))
    rest_to_pay = Column(DECIMAL(10, 2))
    creation = Column(DateTime)
    signed = Column(Boolean, default=False)
    client_id = Column(Integer, ForeignKey('clients.client_id'), nullable=True)
    commercial_contact_id = Column(Integer, ForeignKey('users.user_id'), nullable=True)

    # Relationship definition

    client = relationship("Client", back_populates="contracts")
    commercial_contact = relationship("User", back_populates="contracts")

    @classmethod
    def get_all(cls, db: Session):
        """
        Retrieves all contracts from the database.

        Args:
            db (Session): SQLAlchemy database session.

        Returns:
            list[Contract]: List of all Contract objects.
        """
        return db.query(cls).all()

    @classmethod
    def get_by_id(cls, db: Session, contract_id: int):
        """
            Retrieves a contract by their ID.

            Args:
            db (Session): SQLAlchemy database session.
            contract_id (int): The ID of the contract to retrieve.

            Returns:
            Contract: The Contract object if found, None otherwise.

        """

        return db.query(cls).filter_by(contract_id=contract_id).first()


class Event(Base):
    """
    Represents an event in the CRM system (e.g., meetings, workshops, follow-ups).

    Attributes:
        event_id (int): Primary key and unique identifier for the event.
        name (str): Title/name of the event (max 200 characters).
        notes (str): Detailed description of the event (optional).
        start_datetime (DateTime): Start date and time of the event.
        end_datetime (DateTime): End date and time of the event.
        location (str): Physical or virtual location of the event (max 200 characters).
        attendees (int): Number off attendees for the event.
        client_id (int): Foreign key referencing the associated client.
        support_contact_id (int): Foreign key referencing the user (commercial/support) responsible for the event.


    Relationships:
        client (Client): Many-to-one relationship with Client.
                         An event is associated with exactly one client.
        contact (User): Many-to-one relationship with User.
                        An event is managed by exactly one user (commercial/support).
    """
    __tablename__ = 'events'

    # Columns definition
    event_id = Column(Integer, primary_key=True, index=True, nullable=False)
    name = Column(String(200), nullable=False)
    notes = Column(Text, nullable=True)
    start_datetime = Column(DateTime, nullable=False)
    end_datetime = Column(DateTime, nullable=False)
    location = Column(String(200))
    attendees = Column(Integer)
    client_id = Column(Integer, ForeignKey('clients.client_id'), nullable=True)
    support_contact_id = Column(Integer, ForeignKey('users.user_id'), nullable=True)

    # Relationships definition
    client = relationship("Client", back_populates="events")
    support_contact = relationship("User", back_populates="events")

    @classmethod
    def get_all(cls, db: Session):
        """
        Retrieves all events from the database.

        Args:
            db (Session): SQLAlchemy database session.

        Returns:
            list[Event]: List of all Events objects.
        """
        return db.query(cls).all()

    @classmethod
    def get_by_id(cls, db: Session, event_id: int):
        """
            Retrieves an event by their ID.

            Args:
            db (Session): SQLAlchemy database session.
            event_id (int): The ID of the event to retrieve.

            Returns:
            Event: The Event object if found, None otherwise.

        """

        return db.query(cls).filter_by(event_id=event_id).first()

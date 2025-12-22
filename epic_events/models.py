from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, DECIMAL, Boolean, Text, Enum
from sqlalchemy.orm import relationship, Session
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from epic_events.utils import ErrorMessages

Base = declarative_base()


class User(Base):
    """
        Represents a user in the CRM system (e.g., commercial, management, support).

        Attributes:
            user_id (int): Primary key and unique identifier for the user, auto-incremented.
            first_name (str): User's first name (max 100 characters).
            last_name (str): User's last name (max 100 characters).
            username (str): Unique username for authentication (max 100 characters).
            password_hash (str): Hashed password for authentication (max 100 characters).
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
    password_hash = Column(String(100), nullable=False)
    email = Column(String(100), unique=True)
    role = Column(Enum('commercial', 'management', 'support'))

    # Relationships definition
    clients = relationship("Client", back_populates="commercial_contact")
    contracts = relationship("Contract", back_populates="commercial_contact")
    events = relationship("Event", back_populates="support_contact")

    @classmethod
    def create(cls, db: Session, username: str, first_name: str, last_name: str, email: str, role: str,
               password_hash: str):
        """
        Creates a new user in the database.

        Args:
            db (Session): SQLAlchemy database session.
            username (str): Unique username for authentication (max 100 characters).
            first_name (str): User's first name (max 100 characters).
            last_name (str): User's last name (max 100 characters).
            If already taken, a suffix will be added (e.g., "john_doe_1").
            email (str): Unique email address of the user.
            role (str): Role of the user (commercial/management/support).
            password_hash (str, optional): Hashed password for authentication.

        Returns:
            User: The newly created User object.
        Raises:
            ValueError: If username/email is taken, fields are empty, or role is invalid.
        """

        # Check for duplicate username
        if db.query(cls).filter_by(username=username).first():
            raise ValueError(ErrorMessages.USERNAME_TAKEN.name)

        # Check for duplicate email
        if db.query(cls).filter_by(email=email).first():
            raise ValueError(ErrorMessages.EMAIL_TAKEN.name)

        if role:
            valid_roles = ["commercial", "management", "support"]
            if role not in valid_roles:
                raise ValueError(ErrorMessages.INVALID_ROLE.name)

        # Check for empty required fields
        required_fields = [username, password_hash, first_name, last_name, email, role]
        if not all(required_fields):
            raise ValueError(ErrorMessages.REQUIRED_FIELDS_EMPTY.name)

        return cls(
            username=username,
            first_name=first_name,
            last_name=last_name,
            email=email,
            role=role,
            password_hash=password_hash
        )

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

    def update(self, db: Session, username: str = None, first_name: str = None, last_name: str = None,
               email: str = None, role: str = None):
        """
        Updates the user's information with uniqueness checks for email.
        Only provided fields are updated.

        Args:
            db (Session): SQLAlchemy database session.
            username (str, optional): New username.
            first_name (str, optional): New first name.
            last_name (str, optional): New last name.
            email (str, optional): New email address.
            role (str, optional): New role.

        Raises:
            ValueError: If the new email is already taken by another user.
        """

        # Check for duplicate username (if provided and different from current)
        if username is not None and username != self.username:
            if db.query(User).filter(User.username == username, User.user_id != self.user_id).first():
                raise ValueError(ErrorMessages.USERNAME_TAKEN.name)

        # Check for duplicate email (if provided and different from current)
        if email is not None and email != self.email:
            if db.query(User).filter(User.email == email, User.user_id != self.user_id).first():
                raise ValueError(ErrorMessages.EMAIL_TAKEN.name)

        # Validate role if provided
        if role is not None:
            valid_roles = ["commercial", "management", "support"]
            if role not in valid_roles:
                raise ValueError(ErrorMessages.INVALID_ROLE.name)

        # Update fields
        if username:
            self.username = username
        if first_name:
            self.first_name = first_name
        if last_name:
            self.last_name = last_name
        if email:
            self.email = email
        if role:
            self.role = role

        return self

    def delete(self, db: Session):
        """
        Deletes the user from the database after handling dependencies.
        Dependencies automatically set no None.

        Args:
            db (Session): SQLAlchemy database session.

        Notes:
            - Clients: Sets their commercial_contact_id to None.
            - Contracts: Sets their commercial_contact_id to None.
            - Events: Sets their support_contact_id to None.
        """
        try:
            # Handle clients: set commercial_contact_id to None
            for client in self.clients:
                client.commercial_contact_id = None

            # Handle contracts: set commercial_contact_id to None
            for contract in self.contracts:
                contract.commercial_contact_id = None

            # Handle events: set support_contact_id to None
            for event in self.events:
                event.support_contact_id = None

            return self

        except Exception:
            db.rollback()
            raise ValueError(ErrorMessages.DELETE_FAILED.name)


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
    def create(cls, db: Session, first_name: str, last_name: str, email: str,
               commercial_contact_id: int, business_name: str = None,
               telephone: str = None):
        """
        Creates a new client with validation.
        Does NOT persist the client to the database (handled by the controller).

        Args:
            db (Session): SQLAlchemy database session (for validation only).
            first_name (str): Client's first name.
            last_name (str): Client's last name.
            email (str): Client's email address.
            commercial_contact_id (int): ID of the commercial user responsible.
            business_name (str, optional): Client's business name.
            telephone (str, optional): Client's phone number.

        Returns:
            Client: The created Client object (not persisted).

        Raises:
            ValueError: If validation fails (duplicate email, missing fields, invalid commercial contact).
        """
        # Check for duplicate email
        if db.query(cls).filter_by(email=email).first():
            raise ValueError(ErrorMessages.EMAIL_TAKEN.name)

        # Check for empty required fields
        if not all([first_name, last_name, email, commercial_contact_id]):
            raise ValueError(ErrorMessages.REQUIRED_FIELDS_EMPTY.name)

        # Check if commercial_contact_id exists
        if not db.query(User).filter_by(user_id=commercial_contact_id).first():
            raise ValueError(ErrorMessages.CONTACT_NOT_FOUND.name)

        # Create and return the client object (not persisted)
        return cls(
            first_name=first_name,
            last_name=last_name,
            email=email,
            commercial_contact_id=commercial_contact_id,
            business_name=business_name,
            telephone=telephone,
            first_contact=datetime.now(),
            last_update=datetime.now()
        )

    def update(self, db: Session, **kwargs):
        """
        Updates the client's information with validation.
        Only provided fields are updated. Optional fields (business_name, telephone) are set to None if empty.

        Args:
            db (Session): SQLAlchemy session for validation.
            **kwargs: Fields to update (e.g., email="new@example.com", telephone="1234567890").
                     Only provided fields are modified.

        Returns:
            Client: Updated client object (not persisted).

        Raises:
            ValueError: If email is already taken by another client.
        """
        # Validate email uniqueness if provided and different
        if "email" in kwargs and kwargs["email"] != self.email:
            if db.query(Client).filter(Client.email == kwargs["email"], Client.client_id != self.client_id).first():
                raise ValueError(ErrorMessages.EMAIL_TAKEN.name)

        # Update fields (only provided ones)
        for key, value in kwargs.items():
            if hasattr(self, key):
                # Handle empty strings for optional fields
                if value == "" and key in ["business_name", "telephone"]:
                    setattr(self, key, None)
                else:
                    setattr(self, key, value)

        # Update last_update timestamp
        self.last_update = datetime.now()

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
    def create(cls, db: Session, total_price: float, rest_to_pay: float,
               client_id: int, commercial_contact_id: int, signed: bool = False):
        """
        Creates a new contract with full validation.
        Does NOT persist the contract to the database (handled by the controller).

        Args:
            db (Session): SQLAlchemy database session (for validation only).
            total_price (float): Total amount of the contract (must be > 0).
            rest_to_pay (float): Remaining amount to be paid (must be ≥ 0 and ≤ total_price).
            client_id (int): ID of the associated client (must exist).
            commercial_contact_id (int): ID of the commercial user responsible (must exist).
            signed (bool, optional): Whether the contract is signed. Defaults to False.

        Returns:
            Contract: The created Contract object (not persisted).

        Raises:
            ValueError: If validation fails:
                        - INVALID_TOTAL_PRICE: total_price ≤ 0
                        - INFERIOR_TOTAL_PRICE: rest_to_pay > total_price
                        - NEGATIVE_REST_TO_PAY: rest_to_pay < 0
                        - CLIENT_NOT_FOUND: client_id does not exist
                        - CONTACT_NOT_FOUND: commercial_contact_id does not exist
        """
        # Validate total_price
        if total_price <= 0:
            raise ValueError(ErrorMessages.INVALID_TOTAL_PRICE.name)

        # Validate rest_to_pay
        if rest_to_pay < 0:
            raise ValueError(ErrorMessages.NEGATIVE_REST_TO_PAY.name)
        if rest_to_pay > total_price:
            raise ValueError(ErrorMessages.INFERIOR_TOTAL_PRICE.name)

        # Check if client exists
        if not db.query(Client).filter_by(client_id=client_id).first():
            raise ValueError(ErrorMessages.CLIENT_NOT_FOUND.name)

        # Check if commercial contact exists
        if not db.query(User).filter_by(user_id=commercial_contact_id).first():
            raise ValueError(ErrorMessages.CONTACT_NOT_FOUND.name)

        # Create and return the contract object (not persisted)
        return cls(
            total_price=total_price,
            rest_to_pay=rest_to_pay,
            creation=datetime.now(),
            client_id=client_id,
            commercial_contact_id=commercial_contact_id,
            signed=signed
        )

    def update(self, db: Session, total_price: float = None, rest_to_pay: float = None,
               client_id: int = None, commercial_contact_id: int = None, signed: bool = None):
        """
        Updates the contract's information with validation.
        Does NOT persist changes to the database (handled by the controller).

        Args:
            db (Session): SQLAlchemy database session (for validation only).
            total_price (float, optional): New total price (must be > 0).
            rest_to_pay (float, optional): New remaining amount (must be ≥ 0 and ≤ total_price).
            client_id (int, optional): New client ID (must exist).
            commercial_contact_id (int, optional): New commercial contact ID (must exist).
            signed (bool, optional): New signed status.

        Returns:
            Contract: The updated Contract object (not persisted).

        Raises:
            ValueError: If validations fail (invalid prices, IDs not found).
        """
        # Update total_price if provided
        if total_price is not None:
            if total_price <= 0:
                raise ValueError(ErrorMessages.INVALID_TOTAL_PRICE.name)
            self.total_price = total_price

        # Update rest_to_pay if provided
        if rest_to_pay is not None:
            current_total = self.total_price if total_price is None else total_price
            if rest_to_pay < 0:
                raise ValueError(ErrorMessages.NEGATIVE_REST_TO_PAY.name)
            if rest_to_pay > current_total:
                raise ValueError(ErrorMessages.INFERIOR_TOTAL_PRICE.name)
            self.rest_to_pay = rest_to_pay

        # Update client_id if provided
        if client_id is not None and client_id != self.client_id:
            if not db.query(Client).filter_by(client_id=client_id).first():
                raise ValueError(ErrorMessages.CLIENT_NOT_FOUND.name)
            self.client_id = client_id

        # Update commercial_contact_id if provided
        if commercial_contact_id is not None and commercial_contact_id != self.commercial_contact_id:
            if not db.query(User).filter_by(user_id=commercial_contact_id).first():
                raise ValueError(ErrorMessages.CONTACT_NOT_FOUND.name)
            self.commercial_contact_id = commercial_contact_id

        # Update signed status if provided
        if signed is not None:
            self.signed = signed

        return self

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
    def create(cls, db: Session, name: str, notes: str, start_datetime: datetime,
               end_datetime: datetime, location: str, attendees: int,
               client_id: int, support_contact_id: int):
        """
        Creates a new event with full validation.
        Does NOT persist the event to the database (handled by the controller).

        Args:
            db (Session): SQLAlchemy database session (for validation only).
            name (str): Event name.
            notes (str, optional): Event notes.
            start_datetime (datetime): Start date and time (must be in the future).
            end_datetime (datetime): End date and time (must be after start_datetime).
            location (str, optional): Event location.
            attendees (int): Number of attendees.
            client_id (int): ID of the associated client (must exist).
            support_contact_id (int): ID of the support contact (must exist).

        Returns:
            Event: The created Event object (not persisted).

        Raises:
            ValueError: If validation fails:
                        - CLIENT_NOT_FOUND: client_id does not exist
                        - CONTACT_NOT_FOUND: support_contact_id does not exist
                        - EVENT_DATE_IN_PAST: start_datetime is in the past
                        - END_BEFORE_START: end_datetime is before start_datetime
        """
        # Check if client exists
        if not db.query(Client).filter_by(client_id=client_id).first():
            raise ValueError(ErrorMessages.CLIENT_NOT_FOUND.name)

        # Check if support contact exists
        if not db.query(User).filter_by(user_id=support_contact_id).first():
            raise ValueError(ErrorMessages.CONTACT_NOT_FOUND.name)

        # Validate dates
        if start_datetime < datetime.now():
            raise ValueError(ErrorMessages.EVENT_DATE_IN_PAST.name)
        if end_datetime < start_datetime:
            raise ValueError(ErrorMessages.END_BEFORE_START.name)

        # Create and return the event object (not persisted)
        return cls(
            name=name,
            notes=notes,
            start_datetime=start_datetime,
            end_datetime=end_datetime,
            location=location,
            attendees=attendees,
            client_id=client_id,
            support_contact_id=support_contact_id
        )

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

    def update(self, db: Session, name: str = None, notes: str = None,
               start_datetime: datetime = None, end_datetime: datetime = None,
               location: str = None, attendees: int = None,
               client_id: int = None, support_contact_id: int = None):
        """
        Updates the event's information with validation.
        Does NOT persist changes to the database (handled by the controller).

        Args:
            db (Session): SQLAlchemy database session (for validation only).
            name (str, optional): New event name.
            notes (str, optional): New event notes.
            start_datetime (datetime, optional): New start date and time.
            end_datetime (datetime, optional): New end date and time.
            location (str, optional): New event location.
            attendees (int, optional): New number of attendees.
            client_id (int, optional): New client ID.
            support_contact_id (int, optional): New support contact ID.

        Returns:
            Event: The updated Event object (not persisted).

        Raises:
            ValueError: If validation fails:
                        - EVENT_DATE_IN_PAST: start_datetime is in the past
                        - END_BEFORE_START: end_datetime is before start_datetime
                        - CLIENT_NOT_FOUND: client_id does not exist
                        - CONTACT_NOT_FOUND: support_contact_id does not exist
        """
        # Update name if provided
        if name is not None:
            self.name = name

        # Update notes if provided
        if notes is not None:
            self.notes = notes

        # Update location if provided
        if location is not None:
            self.location = location

        # Update attendees if provided
        if attendees is not None:
            self.attendees = attendees

        # Update start_datetime if provided
        if start_datetime is not None:
            if start_datetime < datetime.now():
                raise ValueError(ErrorMessages.EVENT_DATE_IN_PAST.name)
            self.start_datetime = start_datetime

        # Update end_datetime if provided
        if end_datetime is not None:
            current_start = self.start_datetime if start_datetime is None else start_datetime
            if end_datetime < current_start:
                raise ValueError(ErrorMessages.END_BEFORE_START.name)
            self.end_datetime = end_datetime

        # Update client_id if provided
        if client_id is not None and client_id != self.client_id:
            if not db.query(Client).filter_by(client_id=client_id).first():
                raise ValueError(ErrorMessages.CLIENT_NOT_FOUND.name)
            self.client_id = client_id

        # Update support_contact_id if provided
        if support_contact_id is not None and support_contact_id != self.support_contact_id:
            if not db.query(User).filter_by(user_id=support_contact_id).first():
                raise ValueError(ErrorMessages.CONTACT_NOT_FOUND.name)
            self.support_contact_id = support_contact_id

        return self

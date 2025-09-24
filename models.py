from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, DECIMAL, Boolean, Text, Enum
from sqlalchemy.orm import relationship, Session
from database import Base


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
    commercial_contact_id = Column(Integer, ForeignKey('users.user_id'), nullable=False)

    # Relationship definition
    contracts = relationship("Contract", back_populates="client")
    commercial_contact = relationship("User", back_populates="clients")
    events = relationship("Event", back_populates="client")


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
    client_id = Column(Integer, ForeignKey('clients.client_id'), nullable=False)
    commercial_contact_id = Column(Integer, ForeignKey('users.user_id'), nullable=False)

    # Relationship definition

    client = relationship("Client", back_populates="contracts")
    commercial_contact = relationship("User", back_populates="contracts")


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
    client_id = Column(Integer, ForeignKey('clients.client_id'), nullable=False)
    support_contact_id = Column(Integer, ForeignKey('users.user_id'), nullable=False)

    # Relationships definition
    client = relationship("Client", back_populates="events")
    support_contact = relationship("User", back_populates="events")

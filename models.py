from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, DECIMAL, Boolean, Text
from sqlalchemy.orm import relationship
from database import Base


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

        Relationships:
            contract (Contract): One-to-one or one-to-many relationship with Contract.
            commercial_contact (User): Relationship with the commercial contact (User model).
                                       Note: This requires the 'User' model to be defined.
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

    # Relationship definition
    contract = relationship("Contract", back_populates="client")
    commercial_contact = relationship("User", back_populates="clients")


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
            client_id (int): Foreign key referencing the associated client.
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
    commercial_contact_id = Column(Integer, ForeignKey('users.id'), nullable=False)

    # Relationship definition

    client = relationship("Client", back_populates="contract")
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
        contact_id (int): Foreign key referencing the user (commercial/support) responsible for the event.


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
    contact_id = Column(Integer, ForeignKey('users.id'), nullable=False)

    # Relationships definition
    client = relationship("Client", back_populates="events")
    contact = relationship("User", back_populates="events")

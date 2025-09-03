from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Enum, DECIMAL, Boolean
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
    commercial_contact =relationship("User", back_populates="clients")



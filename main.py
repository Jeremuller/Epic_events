from sqlalchemy.orm import sessionmaker
from models import Base, User, Client, Contract, Event
from database import SessionLocal


# Create session
session = SessionLocal()

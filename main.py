from sqlalchemy.orm import sessionmaker
from models import User, Client, Contract, Event
from database import SessionLocal, Base


# Create session
session = SessionLocal()

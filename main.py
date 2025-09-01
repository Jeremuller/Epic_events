from sqlalchemy.orm import sessionmaker
from models import Base, User, Client, Contract, Event
from database import engine


# Create session
Session = sessionmaker(bind=engine)
session = Session()

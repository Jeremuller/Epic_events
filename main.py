from models import Client, Contract, Event
from database import SessionLocal, init_db


# Create session
session = SessionLocal()

if __name__ == "__main__":
    init_db()


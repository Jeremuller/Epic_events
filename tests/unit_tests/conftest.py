import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from ...database import Base

# Utilise SQLite en mémoire pour les tests
engine = create_engine("sqlite:///:memory:")
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture()
def db():
    # Crée toutes les tables
    Base.metadata.create_all(engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        # Supprime toutes les tables après les tests
        Base.metadata.drop_all(engine)

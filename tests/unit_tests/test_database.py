import pytest
from sqlalchemy import text
from ...database import engine, SessionLocal


def test_database_connection():
    """Teste que la connexion à la base de données fonctionne."""
    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1;"))
            assert result.scalar() == 1
        print("Connexion à la base de données réussie !")
    except Exception as e:
        pytest.fail(f" Erreur de connexion à la base de données : {e}")


def test_session_creation():
    """Teste que la session SQLAlchemy peut être créée."""
    try:
        session = SessionLocal()
        session.close()
        print("Session SQLAlchemy créée avec succès !")
    except Exception as e:
        pytest.fail(f" Erreur de création de session : {e}")

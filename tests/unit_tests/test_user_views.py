import pytest
from click.testing import CliRunner
from ...views import cli, create_user, list_users, update_user, delete_user
from ...models import User


@pytest.fixture
def runner():
    """Fixture to provide a CliRunner for testing CLI commands."""
    return CliRunner()


def test_create_user_command(runner, db_session):
    """Test the create_user CLI command with valid inputs."""
    # Simuler les entrées utilisateur (ordre : username, first_name, last_name, email, role)
    inputs = "judoe\nJules\nDoe\njules@example.com\ncommercial\n"

    # Appeler la commande avec les entrées simulées
    result = runner.invoke(
        create_user,
        input=inputs,
        obj={"db": db_session}  # Passer la session DB au contexte Click
    )

    # Vérifier que la commande a réussi
    assert result.exit_code == 0
    assert "✅ User created" in result.output

    # Vérifier que l'utilisateur a été ajouté en base
    users = db_session.query(User).all()
    assert len(users) == 1
    assert users[0].username == "judoe"
    assert users[0].first_name == "Jules"


def test_list_users_command(runner, db_session):
    """Test the list_users CLI command."""
    # Créer un utilisateur de test
    User.create_user(
        db=db_session,
        username="jdoe",
        first_name="John",
        last_name="Doe",
        email="john@example.com",
        role="commercial"
    )

    # Appeler la commande
    result = runner.invoke(list_users, obj={"db": db_session})

    # Vérifier que la commande a réussi
    assert result.exit_code == 0
    assert "=== List of Users ===" in result.output
    assert "jdoe" in result.output
    assert "John Doe" in result.output


def test_update_user_command(runner, db_session):
    """Test the update_user CLI command."""
    # Créer un utilisateur de test
    user = User.create_user(
        db=db_session,
        username="jdoe",
        first_name="John",
        last_name="Doe",
        email="john@example.com",
        role="commercial"
    )

    # Simuler les entrées utilisateur (nouveaux first_name et email)
    inputs = "Jane\nDoe\njane@example.com\ncommercial\n"

    def test_delete_user_command(runner, db_session):
        """Test the delete_user CLI command."""
        # Créer un utilisateur de test
        user = User.create_user(
            db=db_session,
            username="jdoe",
            first_name="John",
            last_name="Doe",
            email="john@example.com",
            role="commercial"
        )

        # Simuler la confirmation de suppression
        inputs = "y\n"  # Répond "yes" à la confirmation

        # Appeler la commande avec l'ID de l'utilisateur
        result = runner.invoke(
            delete_user,
            args=[str(user.user_id)],
            input=inputs,
            obj={"db": db_session}
        )

        # Vérifier que la commande a réussi
        assert result.exit_code == 0
        assert "✅ User deleted" in result.output

        # Vérifier que l'utilisateur a été supprimé de la base
        deleted_user = db_session.query(User).filter_by(user_id=user.user_id).first()
        assert deleted_user is None

    # Appeler la commande avec l'ID de l'utilisateur
    result = runner.invoke(
        update_user,
        args=[str(user.user_id)],
        input=inputs,
        obj={"db": db_session}
    )

    # Vérifier que la commande a réussi
    assert result.exit_code == 0
    assert "✅ User updated" in result.output

    # Vérifier que l'utilisateur a été mis à jour en base
    updated_user = db_session.query(User).filter_by(user_id=user.user_id).first()
    assert updated_user.first_name == "Jane"
    assert updated_user.email == "jane@example.com"


def test_delete_user_cancelled(runner, db_session):
    """Test that delete_user cancels when user responds 'no'."""
    # Créer un utilisateur de test
    user = User.create_user(
        db=db_session,
        username="jdoe",
        first_name="John",
        last_name="Doe",
        email="john@example.com",
        role="commercial"
    )

    # Simuler l'annulation de la suppression
    inputs = "n\n"  # Répond "no" à la confirmation

    # Appeler la commande avec l'ID de l'utilisateur
    result = runner.invoke(
        delete_user,
        args=[str(user.user_id)],
        input=inputs,
        obj={"db": db_session}
    )

    # Vérifier que la commande a été annulée
    assert result.exit_code == 0
    assert "🔄 Operation cancelled" in result.output

    # Vérifier que l'utilisateur est toujours dans la base
    assert db_session.query(User).filter_by(user_id=user.user_id).first() is not None

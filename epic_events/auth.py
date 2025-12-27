import bcrypt
from epic_events.models import User


def hash_password(password: str) -> str:
    """
    Hash and salt a plain text password.

    :param password: Plain text password
    :return: Hashed password as string
    """
    password_bytes = password.encode("utf-8")
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode("utf-8")


def verify_password(password: str, hashed_password: str) -> bool:
    """
    Verify a plain text password against a hashed password.

    :param password: Plain text password
    :param hashed_password: Hashed password
    :return: True if match, False otherwise
    """
    return bcrypt.checkpw(
        password.encode("utf-8"),
        hashed_password.encode("utf-8")
    )


class SessionContext:
    """
    Represents the authentication context of the current user.

    This class is a lightweight, framework-agnostic object used to:
    - Store authentication state
    - Carry user identity and role information
    - Serve as a basis for permission checks

    It deliberately avoids any dependency on the database layer.
    """

    def __init__(
            self,
            username: str,
            user_id: int,
            role: str,
            is_authenticated: bool = False
    ):
        self.username = username
        self.user_id = user_id
        self.role = role
        self.is_authenticated = is_authenticated

    def __repr__(self) -> str:
        return (
            f"<SessionContext username={self.username!r} "
            f"role={self.role!r} "
            f"authenticated={self.is_authenticated}>"
        )

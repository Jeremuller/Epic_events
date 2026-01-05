import bcrypt
from datetime import datetime, timedelta


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

    SESSION_TIMEOUT = timedelta(minutes=15)

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
        self.created_at = datetime.now()

    def is_expired(self) -> bool:
        """
        Checks whether the session has expired based on its creation time.
        """
        return datetime.now() > self.created_at + self.SESSION_TIMEOUT

    def is_valid(self) -> bool:
        """
        Returns True if the session is authenticated and not expired.
        """
        if not self.is_authenticated:
            return False

        if self.is_expired():
            self.end_session()
            return False

        return True

    def end_session(self):
        """
        Properly invalidates the session.
        """
        self.is_authenticated = False

    def __repr__(self) -> str:
        return (
            f"<SessionContext username={self.username!r} "
            f"role={self.role!r} "
            f"authenticated={self.is_authenticated}>"
        )

import bcrypt


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

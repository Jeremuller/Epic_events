from functools import wraps
from epic_events.auth import SessionContext
from epic_events.views import DisplayMessages


def requires_authentication(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        session = kwargs.get("session")

        if not session or not session.is_authenticated:
            raise PermissionError("AUTHENTICATION_REQUIRED")

        return func(*args, **kwargs)

    return wrapper


def commercial_only(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        session: SessionContext = kwargs.get("session")
        if not session or not session.is_authenticated or session.role != "commercial":
            DisplayMessages.display_error("ACCESS_DENIED")
            return None
        return func(*args, **kwargs)

    return wrapper


def management_only(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        session: SessionContext = kwargs.get("session")
        if not session or not session.is_authenticated or session.role != "management":
            DisplayMessages.display_error("ACCESS_DENIED")
            return None
        return func(*args, **kwargs)

    return wrapper


def support_only(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        session: SessionContext = kwargs.get("session")
        if not session or not session.is_authenticated or session.role != "support":
            DisplayMessages.display_error("ACCESS_DENIED")
            return None
        return func(*args, **kwargs)

    return wrapper

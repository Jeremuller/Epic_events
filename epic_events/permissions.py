from functools import wraps
from epic_events.auth import SessionContext
from epic_events.views import DisplayMessages


def requires_authentication(func):
    """
        Decorator that enforces user authentication before executing a controller action.

        This decorator ensures that a valid and authenticated SessionContext
        is provided to the decorated function. It expects the `session` argument
        to be passed as a keyword argument.

        If the session is missing or not authenticated:
            - Access denied error message is displayed
            - The decorated function is NOT executed
            - None is returned

        Typical usage:
            @requires_authentication
            def some_controller_action(db, session):
                ...

        Args:
            func (callable): The controller function to protect.

        Returns:
            callable: A wrapped function that performs an authentication check
            before delegating execution to the original function.
    """

    @wraps(func)
    def wrapper(*args, **kwargs):

        session = kwargs.get("session")

        if session is None and len(args) >= 2:
            session = args[1]

        if not session or not session.is_authenticated:
            DisplayMessages.display_error("ACCESS_DENIED")
            return None

        return func(*args, **kwargs)

    return wrapper


def commercial_only(func):
    """
    Decorator that restricts access to authenticated users with the 'commercial' role.

    This decorator ensures that:
        - A SessionContext is provided
        - The user is authenticated
        - The user's role is 'commercial'

    The decorated function expects the `session` argument to be passed
    as a keyword argument.

    If any of these conditions fail:
        - Access denied error message is displayed
        - The decorated function is NOT executed
        - None is returned

    Typical usage:
        @commercial_only
        def create_client(db, session):
            ...

    Args:
        func (callable): The controller function to protect.

    Returns:
        callable: A wrapped function that enforces commercial-only access.
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        session: SessionContext = kwargs.get("session")

        if session is None and len(args) >= 2:
            session = args[1]

        if (
                not session
                or not session.is_authenticated
                or session.role != "commercial"
        ):
            DisplayMessages.display_error("ACCESS_DENIED")
            return None

        return func(*args, **kwargs)

    return wrapper


def management_only(func):
    """
    Decorator that restricts access to authenticated users with the 'management' role.

    This decorator ensures that:
        - A SessionContext is provided
        - The user is authenticated
        - The user's role is 'management'

    The decorated function expects the `session` argument to be passed
    as a keyword argument.

    If the user is not authenticated or does not have the required role:
        - Access denied error message is displayed
        - The decorated function is NOT executed
        - None is returned.

    Typical usage:
        @management_only
        def create_user(db, session):
            ...

    Args:
        func (callable): The controller function to protect.

    Returns:
        callable: A wrapped function that enforces management-only access.
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        session: SessionContext = kwargs.get("session")

        if session is None and len(args) >= 2:
            session = args[1]

        if (
                not session
                or not session.is_authenticated
                or session.role != "management"
        ):
            DisplayMessages.display_error("ACCESS_DENIED")
            return None

        return func(*args, **kwargs)

    return wrapper


def support_only(func):
    """
    Decorator that restricts access to authenticated users with the 'support' role.

    This decorator ensures that:
        - A SessionContext is provided
        - The user is authenticated
        - The user's role is 'support'

    The decorated function expects the `session` argument to be passed
    as a keyword argument.

    If the user is not authenticated or does not have the required role:
        - Access denied error message is displayed
        - The decorated function is NOT executed
        - None is returned.

    Typical usage:
        @support_only
        def update_event(db, session):
            ...

    Args:
        func (callable): The controller function to protect.

    Returns:
        callable: A wrapped function that enforces support-only access.
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        session: SessionContext = kwargs.get("session")

        if session is None and len(args) >= 2:
            session = args[1]

        if (
                not session
                or not session.is_authenticated
                or session.role != "support"
        ):
            DisplayMessages.display_error("ACCESS_DENIED")
            return None

        return func(*args, **kwargs)

    return wrapper


def role_permission(allowed_roles):
    """
    Decorator to restrict access to users with specific roles.
    Works like `support_only` but supports multiple allowed roles.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            session = kwargs.get("session")
            # fallback: try to get session from the second positional argument
            if session is None and len(args) >= 2:
                session = args[1]

            if not session:
                raise RuntimeError("Session must be provided")

            if session.role not in allowed_roles:
                raise ValueError("ACCESS_DENIED")

            return func(*args, **kwargs)
        return wrapper
    return decorator

from enum import Enum
import click


class ErrorMessages(Enum):
    """
        Enum class to centralize and manage all error messages in the CRM system.
        Each enum member represents a specific error case with its associated user-friendly message.
        """
    USERNAME_TAKEN = "This username is already taken."
    EMAIL_TAKEN = "This email is already registered."
    REQUIRED_FIELDS_EMPTY = "Required fields cannot be empty or whitespace."
    INVALID_ROLE = "Invalid role. Must be one of: commercial, management, support."
    DELETE_FAILED = "Failed to delete user. Dependencies may be locked."
    DATABASE_ERROR = "A technical error occurred. Please try again later."
    CONTACT_NOT_FOUND = "The contact mentioned does not exist."
    INFERIOR_TOTAL_PRICE = "Total price can't be inferior to rest to pay."
    INVALID_TOTAL_PRICE = "Total_price can't be <= 0."
    NEGATIVE_REST_TO_PAY = "Rest to pay can't be < 0."
    CLIENT_NOT_FOUND = "The specified client does not exist."
    CONTRACT_NOT_FOUND = "The specified contract does not exist."
    EVENT_DATE_IN_PAST = "Event date must be in the future."
    END_BEFORE_START = "End date must be after start date."
    INVALID_CREDENTIALS = "The credentials you have selected are not recognized. Please try again."

    @classmethod
    def get_message(cls, error_key):
        """
                Retrieve the error message associated with the given error key.

                Args:
                    error_key (str): The key of the error message to retrieve.
                                      Must match an enum member name (case-sensitive).

                Returns:
                    str: The error message associated with the provided key.
                         If the key is not found, returns the generic database error message.
        """
        try:
            return cls[error_key].value
        except KeyError:
            return cls.DATABASE_ERROR.value


def validate_length(prompt_text, max_length):
    """
    Helper function to validate the length of user input.
    Args:
        prompt_text (str): The prompt to display.
        max_length (int): Maximum allowed length.
    Returns:
        str: Validated user input.
    """
    while True:
        value = click.prompt(prompt_text)
        if len(value) <= max_length:
            return value
        print(f"Error: Input must be {max_length} characters or less. Try again.")

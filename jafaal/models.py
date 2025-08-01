from typing import Protocol, TypeVar

# Define a generic TypeVar for user IDs, so schemas and protocols can work with any ID type
# (e.g., int, UUID, or a custom identifier)
ID = TypeVar("ID")


class UserProtocol(Protocol[ID]):
    """
    Protocol for user objects, specifying the required attributes. Protocol that
    ORM model should follow.

    Attributes:
        id (ID): Unique identifier for the user.
        email (str): User's email address.
        hashed_password (str): Hashed password for authentication.
        is_active (bool): Indicates if the user account is active.
        is_verified (bool): Indicates if the user's email or account is verified.
    """

    id: ID
    email: str
    hashed_password: str
    is_active: bool
    is_verified: bool


# Define a TypeVar for any concrete implementation of UserProtocol,
# enabling functions and classes to be generic over different user model types
UP = TypeVar("UP", bound=UserProtocol)

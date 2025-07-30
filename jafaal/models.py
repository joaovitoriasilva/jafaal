from datetime import datetime
from typing import Protocol, TypeVar

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

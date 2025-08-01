from typing import Any, Generic

from jafaal.models import ID, UP
from jafaal.types import DependencyCallable


class BaseUserDatabase(Generic[UP, ID]):
    """
    Abstract base class for user database operations.

    Type Parameters:
        UP: User model or schema type.
        ID: Type of the user identifier.

    Methods:
            Retrieve a user by their unique identifier.

            Retrieve a user by their email address.

            Retrieve a user by their OAuth provider and account ID.

            Create a new user with the provided data.

            Update an existing user with the provided data.

            Delete the specified user from the database.

    All methods must be implemented by subclasses.
    """

    async def get(self, user_id: ID) -> UP | None:
        """
        Retrieve an object by its unique identifier.

        Args:
            user_id (ID): The unique identifier of the object to retrieve.

        Returns:
            UP | None: The object corresponding to the given ID if found, otherwise None.

        Raises:
            NotImplementedError: If the method is not implemented in a subclass.
        """
        raise NotImplementedError()

    async def get_by_email(self, email: str) -> UP | None:
        """
        Retrieve a user instance by their email address.

        Args:
            email (str): The email address of the user to retrieve.

        Returns:
            UP | None: The user instance if found, otherwise None.

        Raises:
            NotImplementedError: This method must be implemented by subclasses.
        """
        raise NotImplementedError()

    async def create(self, create_dict: dict[str, Any]) -> UP:
        """
        Asynchronously creates a new record in the database using the provided dictionary of values.

        Args:
            create_dict (dict[str, Any]): A dictionary containing the fields and values for the new record.

        Returns:
            UP: The created record instance.

        Raises:
            NotImplementedError: If the method is not implemented in the subclass.
        """
        raise NotImplementedError()

    async def update(self, user: UP, update_dict: dict[str, Any]) -> UP:
        """
        Asynchronously updates the specified user with the provided update dictionary.

        Args:
            user (UP): The user object to be updated.
            update_dict (dict[str, Any]): A dictionary containing the fields to update and their new values.

        Returns:
            UP: The updated user object.

        Raises:
            NotImplementedError: If the method is not implemented by a subclass.
        """
        raise NotImplementedError()

    async def delete(self, user: UP) -> None:
        """
        Asynchronously deletes the specified user from the database.

        Args:
            user (UP): The user instance to be deleted.

        Raises:
            NotImplementedError: This method must be implemented by subclasses.
        """
        raise NotImplementedError()


# A FastAPI dependency type alias for any callable that provides a BaseUserDatabase instance.
# This can be:
#   - A sync function returning BaseUserDatabase[UP, ID]
#   - An async function (coroutine) returning BaseUserDatabase[UP, ID]
#   - A generator-based dependency (sync or async) yielding BaseUserDatabase[UP, ID]
#
# Use this alias when declaring `Depends(...)` on your database adapter provider.
UserDatabaseDependency = DependencyCallable[BaseUserDatabase[UP, ID]]

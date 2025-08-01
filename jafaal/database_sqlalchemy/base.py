import uuid
from typing import TYPE_CHECKING, Any, Generic

from jafaal.database.base import BaseUserDatabase
from jafaal.models import ID, UP
from sqlalchemy import Boolean, String, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import Select

from jafaal.database_sqlalchemy.generics import GUID

UUID_ID = uuid.UUID


class SQLAlchemyBaseUserTable(Generic[ID]):
    """
    SQLAlchemy base user table definition.

    This generic class defines the structure of the "users" table for SQLAlchemy ORM models.
    It supports type checking and runtime column definitions for user-related fields.

    Attributes:
        id (ID): The unique identifier for the user (type depends on the generic parameter).
        email (str): The user's email address, unique and indexed.
        hashed_password (str): The user's hashed password.
        is_active (bool): Indicates whether the user account is active.
        is_superuser (bool): Indicates whether the user has superuser privileges.
        is_verified (bool): Indicates whether the user's email is verified.
    """
    __tablename__ = "users"

    if TYPE_CHECKING:
        id: ID
        email: str
        hashed_password: str
        is_active: bool
        is_superuser: bool
        is_verified: bool
    else:
        email: Mapped[str] = mapped_column(
            String(length=320), unique=True, index=True, nullable=False
        )
        hashed_password: Mapped[str] = mapped_column(
            String(length=1024), nullable=False
        )
        is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
        is_superuser: Mapped[bool] = mapped_column(
            Boolean, default=False, nullable=False
        )
        is_verified: Mapped[bool] = mapped_column(
            Boolean, default=False, nullable=False
        )


class SQLAlchemyBaseUserTableUUID(SQLAlchemyBaseUserTable[UUID_ID]):
    """
    SQLAlchemy model for a user table with a UUID primary key.

    This class extends `SQLAlchemyBaseUserTable` with a UUID-based `id` column,
    using SQLAlchemy's `Mapped` and `mapped_column` for ORM mapping. The `id`
    column is set as the primary key and defaults to a new UUID value.

    Attributes:
        id (UUID_ID): The primary key for the user table, represented as a UUID.
    """
    if TYPE_CHECKING:
        id: UUID_ID
    else:
        id: Mapped[UUID_ID] = mapped_column(GUID, primary_key=True, default=uuid.uuid4)


class SQLAlchemyUserDatabase(Generic[UP, ID], BaseUserDatabase[UP, ID]):
    """
    A generic asynchronous user database implementation using SQLAlchemy.

    This class provides CRUD operations for user models in an asynchronous context,
    leveraging SQLAlchemy's AsyncSession and ORM capabilities.

    Type Parameters:
        UP: The SQLAlchemy user model type.
        ID: The type of the user model's primary key.

    Attributes:
        session (AsyncSession): The SQLAlchemy asynchronous session used for database operations.
        user_table (type[UP]): The SQLAlchemy user model/table class.

    Methods:
        __init__(session, user_table):
            Initializes the user database with a session and user table.

        async get(user_id: ID) -> UP | None:
            Retrieves a user by their primary key.

        async get_by_email(email: str) -> UP | None:
            Retrieves a user by their email address (case-insensitive).

        async create(create_dict: dict[str, Any]) -> UP:
            Creates a new user with the provided attributes.

        async update(user: UP, update_dict: dict[str, Any]) -> UP:
            Updates an existing user with the provided attributes.

        async delete(user: UP) -> None:
            Deletes the specified user from the database.

        async _get_user(statement: Select) -> UP | None:
            Executes the given SQLAlchemy select statement and returns a single user or None.
    """
    session: AsyncSession
    user_table: type[UP]

    def __init__(
        self,
        session: AsyncSession,
        user_table: type[UP],
    ):
        """
        Initializes the class with a given asynchronous database session and user table model.

        Args:
            session (AsyncSession): The asynchronous SQLAlchemy session to be used for database operations.
            user_table (type[UP]): The SQLAlchemy model class representing the user table.

        """
        self.session = session
        self.user_table = user_table

    async def get(self, user_id: ID) -> UP | None:
        """
        Retrieve a user record by its unique identifier.

        Args:
            user_id (ID): The unique identifier of the user to retrieve.

        Returns:
            UP | None: The user object if found, otherwise None.
        """
        statement = select(self.user_table).where(self.user_table.id == user_id)
        return await self._get_user(statement)

    async def get_by_email(self, email: str) -> UP | None:
        """
        Asynchronously retrieves a user by their email address.

        Args:
            email (str): The email address of the user to retrieve.

        Returns:
            UP | None: The user object if found, otherwise None.
        """
        statement = select(self.user_table).where(
            func.lower(self.user_table.email) == func.lower(email)
        )
        return await self._get_user(statement)

    async def create(self, create_dict: dict[str, Any]) -> UP:
        """
        Asynchronously creates a new user record in the database.

        Args:
            create_dict (dict[str, Any]): A dictionary containing the fields and values for the new user.

        Returns:
            UP: The newly created user instance after being committed and refreshed from the database.
        """
        user = self.user_table(**create_dict)
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def update(self, user: UP, update_dict: dict[str, Any]) -> UP:
        """
        Asynchronously updates the attributes of a user instance with the provided values.

        Args:
            user (UP): The user instance to be updated.
            update_dict (dict[str, Any]): A dictionary containing attribute names and their new values.

        Returns:
            UP: The updated user instance after committing and refreshing from the database.
        """
        for key, value in update_dict.items():
            setattr(user, key, value)
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def delete(self, user: UP) -> None:
        """
        Asynchronously deletes a user instance from the database and commits the transaction.

        Args:
            user (UP): The user instance to be deleted from the database.

        Returns:
            None
        """
        await self.session.delete(user)
        await self.session.commit()

    async def _get_user(self, statement: Select) -> UP | None:
        """
        Asynchronously executes the provided SQLAlchemy Select statement to retrieve a single unique user.

        Args:
            statement (Select): The SQLAlchemy Select statement used to query the user.

        Returns:
            UP | None: The user object if found, otherwise None.
        """
        results = await self.session.execute(statement)
        return results.unique().scalar_one_or_none()

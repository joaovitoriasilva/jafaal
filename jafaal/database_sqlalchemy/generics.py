import uuid
from datetime import datetime, timezone
from typing import Optional

from pydantic import UUID4
from sqlalchemy import CHAR, TIMESTAMP, TypeDecorator
from sqlalchemy.dialects.postgresql import UUID


class GUID(TypeDecorator):
    """
    A SQLAlchemy custom type decorator for handling UUIDs across different database backends.

    This GUID type ensures that UUID values are stored and retrieved consistently, regardless of the underlying database.
    - For PostgreSQL, it uses the native UUID type.
    - For other databases, it stores UUIDs as 36-character strings (CHAR(36)).

    Attributes:
        impl (TypeEngine): The underlying type implementation, set to a custom CHAR subclass.
        cache_ok (bool): Indicates that this type is safe to cache.

    Methods:
        load_dialect_impl(dialect):
            Returns the appropriate type descriptor based on the database dialect.
        process_bind_param(value, dialect):
            Converts Python UUID objects to a format suitable for storage in the database.
        process_result_value(value, dialect):
            Converts database values back into Python UUID objects.
    """
    class UUIDChar(CHAR):
        """
        A custom SQLAlchemy CHAR type for storing UUID4 values as character strings.

        This type ensures that Python values are handled as UUID4 objects,
        while being stored in the database as CHAR fields.

        Attributes:
            python_type (type): The Python type used for this column, set to UUID4.
        """
        python_type = UUID4

    impl = UUIDChar
    cache_ok = True

    def load_dialect_impl(self, dialect):
        """
        Provides the appropriate SQLAlchemy type descriptor for the current database dialect.

        If the dialect is PostgreSQL, returns a UUID type descriptor.
        For all other dialects, returns a CHAR(36) type descriptor.

        Args:
            dialect: The SQLAlchemy dialect in use.

        Returns:
            A type descriptor suitable for the specified dialect.
        """
        if dialect.name == "postgresql":
            return dialect.type_descriptor(UUID())
        return dialect.type_descriptor(CHAR(36))

    def process_bind_param(self, value, dialect):
        """
        Processes the value before it is sent to the database.

        Parameters:
            value (Any): The value to be processed, typically a UUID or a string representation of a UUID.
            dialect (Dialect): The SQLAlchemy dialect in use, which determines database-specific behavior.

        Returns:
            str or None: The processed value as a string suitable for database storage, or None if the input value is None.

        Behavior:
            - If the value is None, returns None.
            - If the database dialect is PostgreSQL, returns the string representation of the value.
            - If the value is not a UUID instance, attempts to convert it to a UUID and then to a string.
            - Otherwise, returns the string representation of the UUID value.
        """
        if value is None:
            return value
        if dialect.name == "postgresql":
            return str(value)
        if not isinstance(value, uuid.UUID):
            return str(uuid.UUID(value))
        return str(value)

    def process_result_value(self, value):
        """
        Processes the value returned from the database before passing it to the application.

        Args:
            value: The value fetched from the database.
            dialect: The database dialect in use.

        Returns:
            The processed value, converted to a uuid.UUID instance if necessary, or None if the value is None.
        """
        if value is None:
            return value
        if not isinstance(value, uuid.UUID):
            value = uuid.UUID(value)
        return value


def now_utc():
    """
    Returns the current date and time in UTC.

    Returns:
        datetime: The current UTC date and time as a timezone-aware datetime object.
    """
    return datetime.now(timezone.utc)


class TIMESTAMPAware(TypeDecorator):
    """
    A SQLAlchemy TypeDecorator that ensures returned TIMESTAMP values are timezone-aware.

    This decorator is intended for use with databases that do not natively return timezone-aware
    datetime objects (such as SQLite or MySQL). When fetching results, if the database dialect is
    not PostgreSQL and the value is not None, the returned datetime will be set to UTC timezone.

    Attributes:
        impl (TypeEngine): The underlying SQL type, set to TIMESTAMP.
        cache_ok (bool): Indicates this type is safe to cache.

    Methods:
        process_result_value(value, dialect):
            Ensures the returned datetime is timezone-aware (UTC) unless using PostgreSQL.
    """
    impl = TIMESTAMP
    cache_ok = True

    def process_result_value(self, value: Optional[datetime], dialect):
        """
        Processes the result value retrieved from the database, ensuring timezone awareness for non-PostgreSQL dialects.

        If the value is not None and the database dialect is not PostgreSQL, the method sets the timezone information to UTC.
        Otherwise, it returns the value as is.

        Args:
            value (Optional[datetime]): The datetime value retrieved from the database.
            dialect: The database dialect in use.

        Returns:
            Optional[datetime]: The processed datetime value with UTC timezone info if applicable, or the original value.
        """
        if value is not None and dialect.name != "postgresql":
            return value.replace(tzinfo=timezone.utc)
        return value

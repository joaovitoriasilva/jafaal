from typing import Any, Generic, TypeVar
from pydantic import BaseModel, ConfigDict, EmailStr

from jafaal.models import ID


def model_dump(model: BaseModel, *args, **kwargs) -> dict[str, Any]:
    """
    Serializes a Pydantic BaseModel instance to a dictionary.

    Args:
        model (BaseModel): The Pydantic model instance to serialize.
        *args: Additional positional arguments to pass to the model's `model_dump` method.
        **kwargs: Additional keyword arguments to pass to the model's `model_dump` method.

    Returns:
        dict[str, Any]: A dictionary representation of the model.
    """
    return model.model_dump(*args, **kwargs)


class CreateUpdateDictModel(BaseModel):
    """
    A Pydantic model mixin that provides a method to generate a dictionary of the model's data,
    excluding unset fields and specific attributes ('id', 'is_active', 'is_verified').

    Methods:
        create_update_dict():
            Returns a dictionary representation of the model instance, excluding unset fields
            and the fields 'id', 'is_active', and 'is_verified'.
    """

    def create_update_dict(self):
        """
        Generates a dictionary representation of the model instance for update operations.

        This method uses `model_dump` to serialize the instance, excluding fields that are unset
        and specific fields such as 'id', 'is_active', and 'is_verified'. The resulting dictionary
        is suitable for update operations where these fields should not be modified.

        Returns:
            dict: A dictionary containing the updatable fields of the model instance.
        """
        return model_dump(
            self,
            exclude_unset=True,
            exclude={
                "id",
                "is_active",
                "is_verified",
            },
        )


class BaseUser(CreateUpdateDictModel, Generic[ID]):
    """
    BaseUser is a generic base model for user entities.

    Attributes:
        id (ID): Unique identifier for the user.
        email (EmailStr): Email address of the user.
        is_active (bool): Indicates if the user account is active. Defaults to True.
        is_verified (bool): Indicates if the user's email is verified. Defaults to False.

    Config:
        model_config (ConfigDict): Configuration to allow model creation from attribute dictionaries.
    """

    id: ID
    email: EmailStr
    is_active: bool = True
    is_verified: bool = False

    model_config = ConfigDict(from_attributes=True)


class BaseUserCreate(CreateUpdateDictModel):
    """
    Schema for creating a new user.

    Attributes:
        email (EmailStr): The user's email address.
        password (str): The user's password.
        is_active (bool, optional): Indicates if the user account is active. Defaults to True.
        is_verified (bool, optional): Indicates if the user account is verified. Defaults to False.
    """

    email: EmailStr
    password: str
    is_active: bool | None = True
    is_verified: bool | None = False


class BaseUserUpdate(CreateUpdateDictModel):
    """
    Schema for updating user information.

    Attributes:
        password (str | None): The user's password. Optional.
        email (EmailStr | None): The user's email address. Optional.
        is_active (bool | None): Indicates if the user account is active. Optional.
        is_verified (bool | None): Indicates if the user account is verified. Optional.
    """

    password: str | None = None
    email: EmailStr | None = None
    is_active: bool | None = None
    is_verified: bool | None = None


# Define TypeVars for enhanced static typing:
# - U  is bound to BaseUser, for functions or classes that return/read user data schemas
# - UC is bound to BaseUserCreate, for create-operation schemas
# - UU is bound to BaseUserUpdate, for update-operation schemas
U = TypeVar("U", bound=BaseUser)
UC = TypeVar("UC", bound=BaseUserCreate)
UU = TypeVar("UU", bound=BaseUserUpdate)

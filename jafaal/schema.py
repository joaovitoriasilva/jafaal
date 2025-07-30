from typing import Any, Generic, Optional, TypeVar
from pydantic import BaseModel, ConfigDict, EmailStr

from jafaal import models


class BaseUser(BaseModel, Generic[models.ID]):

    id: models.ID
    email: EmailStr
    is_active: bool = True
    is_verified: bool = False

    model_config = ConfigDict(from_attributes=True)


class BaseUserCreate(BaseUser):
    email: EmailStr
    password: str
    is_active: bool | None = True
    is_verified: bool | None = False


class BaseUserUpdate(BaseUser):
    password: str | None = None
    email: EmailStr | None = None
    is_active: bool | None = None
    is_verified: bool | None = None

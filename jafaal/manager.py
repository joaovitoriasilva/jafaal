import uuid, os
from typing import Any, Generic, Optional, Union

from datetime import datetime, timedelta, timezone
from fastapi import Request, Response
from fastapi.security import OAuth2PasswordRequestForm

from jafaal import exceptions, models, schemas, jwt
from jafaal.database import BaseUserDatabase
from jafaal.password_hasher import PasswordHasher
from jafaal.types import DependencyCallable


JWT_ACCESS_TOKEN_EXPIRE_MINUTES = int(
    os.environ.get("ACCESS_TOKEN_EXPIRE_MINUTES", "15")
)
JWT_REFRESH_TOKEN_EXPIRE_DAYS = int(os.environ.get("REFRESH_TOKEN_EXPIRE_DAYS", "7"))


class BaseUserManager(Generic[models.UP, models.ID]):

    user_db: BaseUserDatabase[models.UP, models.ID]
    password_helper: PasswordHasher

    def __init__(
        self,
        user_db: BaseUserDatabase[models.UP, models.ID],
        password_helper: PasswordHasher | None = None,
    ):
        self.user_db = user_db
        if password_helper is None:
            self.password_helper = PasswordHasher()
        else:
            self.password_helper = password_helper

    def parse_id(self, value: Any) -> models.ID:
        raise NotImplementedError()

    async def get(self, user_id: models.ID) -> models.UP:
        user = await self.user_db.get(user_id)

        if user is None:
            raise exceptions.UserNotExists()

        return user

    async def get_by_email(self, user_email: str) -> models.UP:
        user = await self.user_db.get_by_email(user_email)

        if user is None:
            raise exceptions.UserNotExists()

        return user

    async def create(
        self,
        user_create: schemas.UC,
        safe: bool = False,
        request: Request | None = None,
    ) -> models.UP:
        await self.password_helper.validate_password(user_create.password)

        existing_user = await self.user_db.get_by_email(user_create.email)
        if existing_user is not None:
            raise exceptions.UserAlreadyExists()

        user_dict = (
            user_create.create_update_dict()
            if safe
            else user_create.create_update_dict_superuser()
        )
        password = user_dict.pop("password")
        user_dict["hashed_password"] = self.password_helper.hash_password(password)

        created_user = await self.user_db.create(user_dict)

        # await self.on_after_register(created_user, request)

        return created_user

    async def request_verify(
        self,
        user: models.UP,
        jwt_algorithm: str | None,
        jwt_secret: jwt.SecretType | None,
        scopes_required: bool = True,
        scopes: list[str] | None = None,
        request: Request | None = None,
    ) -> None:
        if not user.is_active:
            raise exceptions.UserInactive()
        if user.is_verified:
            raise exceptions.UserAlreadyVerified()

        access_token_lifetime = timedelta(minutes=JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
        refresh_token_lifetime = timedelta(days=JWT_REFRESH_TOKEN_EXPIRE_DAYS)

        token_data = {
            "sub": str(user.id),
        }

        if scopes_required:
            if scopes is None:
                raise jwt.JWTError('JWT payload must include a "scopes" claim.')
            token_data.update({"scopes": scopes})

        access_token = jwt.create_jwt(
            token_data,
            access_token_lifetime,
            jwt_algorithm,
            jwt_secret,
            scopes_required,
        )
        refresh_token = jwt.create_jwt(
            token_data,
            refresh_token_lifetime,
            jwt_algorithm,
            jwt_secret,
            scopes_required,
        )
        # await self.on_after_request_verify(user, access_token, refresh_token, request)

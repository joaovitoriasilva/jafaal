from typing import Any


class JafaalException(Exception):
    pass


class InvalidID(JafaalException):
    pass


class UserAlreadyExists(JafaalException):
    pass


class UserNotExists(JafaalException):
    pass


class UserInactive(JafaalException):
    pass


class UserAlreadyVerified(JafaalException):
    pass


class InvalidVerifyToken(JafaalException):
    pass


class InvalidResetPasswordToken(JafaalException):
    pass


class InvalidPasswordException(JafaalException):
    def __init__(self, reason: Any) -> None:
        self.reason = reason

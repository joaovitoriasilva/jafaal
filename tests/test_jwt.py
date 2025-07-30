import pytest
import jwt as pyjwt
from datetime import datetime, timedelta, timezone
from jafaal.jwt import create_jwt, decode_jwt, JWTError  # adjust import path

SECRET = "testsecret"


def test_create_jwt_success():
    data = {"sub": "user123", "scopes": ["users:read"]}
    token = create_jwt(data, timedelta(minutes=10), jwt_secret=SECRET)
    decoded = decode_jwt(token, jwt_secret=SECRET)
    assert decoded["sub"] == "user123"
    assert decoded["scopes"] == ["users:read"]


def test_create_jwt_negative_lifetime():
    with pytest.raises(JWTError):
        create_jwt(
            {"sub": "user123", "scopes": ["users:read"]},
            timedelta(seconds=0),
            jwt_secret=SECRET,
        )


def test_create_jwt_missing_secret():
    with pytest.raises(JWTError):
        create_jwt(
            {"sub": "user123", "scopes": ["users:read"]},
            timedelta(minutes=1),
            jwt_secret=None,
        )


def test_create_jwt_unsupported_algorithm():
    with pytest.raises(JWTError):
        create_jwt(
            {"sub": "user123", "scopes": ["users:read"]},
            timedelta(minutes=1),
            jwt_secret=SECRET,
            jwt_algorithm="none",
        )


def test_create_jwt_missing_sub():
    with pytest.raises(JWTError):
        create_jwt({"scopes": ["users:read"]}, timedelta(minutes=1), jwt_secret=SECRET)


def test_create_jwt_missing_scopes_when_required():
    with pytest.raises(JWTError):
        create_jwt({"sub": "user123"}, timedelta(minutes=1), jwt_secret=SECRET)


def test_decode_jwt_missing_secret():
    token = create_jwt(
        {"sub": "user123", "scopes": ["users:read"]},
        timedelta(minutes=1),
        jwt_secret=SECRET,
    )
    with pytest.raises(JWTError):
        decode_jwt(token, jwt_secret=None)


def test_decode_jwt_invalid_token():
    with pytest.raises(JWTError):
        decode_jwt("not.a.jwt", jwt_secret=SECRET)


def test_decode_jwt_expired_token():
    token = create_jwt(
        {"sub": "user123", "scopes": ["users:read"]},
        timedelta(seconds=-10),
        jwt_secret=SECRET,
    )
    with pytest.raises(JWTError):
        decode_jwt(token, jwt_secret=SECRET)


def test_decode_jwt_immature_token():
    now = datetime.now(timezone.utc)
    payload = {
        "sub": "user123",
        "scopes": ["users:read"],
        "iat": int(now.timestamp()),
        "nbf": int((now + timedelta(seconds=60)).timestamp()),
        "exp": int((now + timedelta(minutes=10)).timestamp()),
    }
    token = pyjwt.encode(payload, SECRET, algorithm="HS256")
    with pytest.raises(JWTError):
        decode_jwt(token, jwt_secret=SECRET)


def test_decode_jwt_without_scopes_required():
    data = {"sub": "user123"}
    token = create_jwt(
        data, timedelta(minutes=1), jwt_secret=SECRET, scopes_required=False
    )
    decoded = decode_jwt(token, jwt_secret=SECRET, scopes_required=False)
    assert decoded["sub"] == "u"


def test_decode_jwt_missing_scopes_when_required():
    now = datetime.now(timezone.utc)
    payload = {
        "sub": "user123",
        "iat": int(now.timestamp()),
        "nbf": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=5)).timestamp()),
    }
    token = pyjwt.encode(payload, SECRET, algorithm="HS256")
    with pytest.raises(JWTError):
        decode_jwt(token, jwt_secret=SECRET, scopes_required=True)

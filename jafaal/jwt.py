import os
import jwt

from typing import Any
from datetime import datetime, timedelta, timezone

JWT_ALGORITHM = os.environ.get("JWT_ALGORITHM", "HS256")
JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY")
SUPPORTED_ALGORITHMS = {"HS256"}


class JWTError(ValueError):
    """
    Exception raised for errors related to JSON Web Token (JWT) operations.

    This exception is typically used to indicate issues such as invalid tokens,
    decoding errors, or signature verification failures during JWT processing.

    Inherits from:
        ValueError: Indicates that a function received an argument of the correct type but with an inappropriate value.
    """


def create_jwt(
    data: dict,
    lifetime: timedelta,
    jwt_algorithm: str = JWT_ALGORITHM,
    jwt_secret: str | None = JWT_SECRET_KEY,
    scopes_required: bool = True,
) -> str:
    """
    Create a JSON Web Token (JWT) with the specified payload, lifetime, algorithm, and secret key.

    Args:
        data (dict): The payload data to include in the JWT. Must include a "sub" (subject) claim.
        lifetime (timedelta): The duration for which the JWT will be valid.
        jwt_algorithm (str, optional): The algorithm to use for encoding the JWT. Must be one of SUPPORTED_ALGORITHMS. Defaults to JWT_ALGORITHM.
        jwt_secret (str | None, optional): The secret key to use for encoding the JWT. Must be provided. Defaults to JWT_SECRET_KEY.
        scopes_required (bool, optional): Whether the payload must include a "scopes" claim. Defaults to True.

    Returns:
        str: The encoded JWT as a string.

    Raises:
        JWTError: If the lifetime is not greater than zero.
        JWTError: If the secret key is not provided.
        JWTError: If the specified algorithm is not supported.
        JWTError: If the payload does not include a "sub" (subject) claim.
        JWTError: If scopes are required but the payload does not include a "scopes" claim.
    """
    # Validate the lifetime to ensure it is greater than zero
    if lifetime.total_seconds() <= 0:
        raise JWTError("Lifetime must be greater than zero.")

    # Ensure that the secret key is provided
    if jwt_secret is None:
        raise JWTError("JWT secret key must be provided for encoding.")

    # Validate the JWT algorithm
    if jwt_algorithm not in SUPPORTED_ALGORITHMS:
        raise JWTError(f"Unsupported JWT algorithm: {jwt_algorithm}")

    # Calculate time now
    now = datetime.now(timezone.utc)
    # Calculate the expiration time based on the provided lifetime
    expire = now + lifetime
    # Create a JWT payload
    payload = data.copy()

    # Ensure that the payload includes a subject claim
    if "sub" not in payload:
        raise JWTError('JWT payload must include a "sub" (subject) claim.')
    # Ensure that the payload includes scopes if required
    if scopes_required and "scopes" not in payload:
        raise JWTError('JWT payload must include a "scopes" claim.')
    # add the issued at time to the payload
    payload["iat"] = int(now.timestamp())
    # add the expiration time to the payload
    payload["exp"] = int(expire.timestamp())
    # add the not before time to the payload
    payload["nbf"] = int((now - timedelta(seconds=10)).timestamp())

    # Encode the JWT with the provided secret and algorithm
    return jwt.encode(payload, jwt_secret, algorithm=jwt_algorithm)


def decode_jwt(
    encoded_jwt: str,
    jwt_secret: str | None = JWT_SECRET_KEY,
    algorithms: list[str] | None = None,
    scopes_required: bool = True,
) -> dict[str, Any]:
    """
    Decodes and validates a JSON Web Token (JWT).

    Args:
        encoded_jwt (str): The encoded JWT string to decode.
        jwt_secret (str | None, optional): The secret key used to decode the JWT. Defaults to JWT_SECRET_KEY.
        algorithms (list[str] | None, optional): List of acceptable algorithms for decoding. Defaults to [JWT_ALGORITHM].
        scopes_required (bool, optional): Whether the 'scopes' claim is required in the JWT. Defaults to True.

    Returns:
        dict[str, Any]: The decoded JWT payload as a dictionary.

    Raises:
        JWTError: If the secret key is not provided, required claims are missing, the token is expired, 
                  the issue time is invalid, the token is not yet valid, or the token is otherwise invalid.
    """
    # Ensure that the secret key is provided
    if jwt_secret is None:
        raise JWTError("JWT secret key must be provided for decoding.")

    # Use the default algorithm if none is provided
    if algorithms is None:
        algorithms = [JWT_ALGORITHM]

    # Define the required claims for the JWT
    required_claims = ["exp", "sub", "iat", "nbf"]
    if scopes_required:
        required_claims.append("scopes")

    try:
        return jwt.decode(
            encoded_jwt,
            jwt_secret,
            options={
                "require": required_claims,
                "verify_exp": True,
                "verify_iat": True,
                "verify_nbf": True,
            },
            algorithms=algorithms,
            leeway=5,
        )
    except jwt.MissingRequiredClaimError as err:
        raise JWTError(f"Missing claims: {err.missing_claims}") from err
    except jwt.ExpiredSignatureError as err:
        raise JWTError("JWT has expired.") from err
    except jwt.InvalidIssuedAtError as err:
        raise JWTError("JWT issue time (iat) is invalid or not an integer.") from err
    except jwt.exceptions.ImmatureSignatureError as err:
        raise JWTError("JWT is not yet valid (nbf claim).") from err
    except jwt.InvalidTokenError as err:
        raise JWTError("Invalid JWT, unable to decode token.") from err

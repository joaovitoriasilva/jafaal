import pytest

from pwdlib.hashers.argon2 import Argon2Hasher
from pwdlib.hashers.bcrypt import BcryptHasher

from jafaal.password_hasher import PasswordHasher, PasswordPolicyError


@pytest.fixture(params=[None, Argon2Hasher(), BcryptHasher()])
def hasher_instance(request):
    """
    Fixture that creates and returns a PasswordHasher instance using the parameter provided by the test request.

    Args:
        request: pytest's built-in fixture that provides access to the requesting test context and its parameters.

    Returns:
        PasswordHasher: An instance of PasswordHasher initialized with the parameter specified in the test.

    Usage:
        Used as a fixture in parameterized tests to supply different PasswordHasher configurations.
    """
    return PasswordHasher(request.param)


def test_hash_and_verify_roundtrip(hasher_instance):
    """
    Tests the password hasher's ability to correctly hash and verify passwords.

    This test ensures that:
    - A password hashed by `hasher_instance.hash_password` can be successfully verified by `hasher_instance.verify`.
    - An incorrect password does not verify against the same hash.

    Args:
        hasher_instance: An instance of the password hasher to be tested.
    """
    pwd = "StrongPass1!"
    h = hasher_instance.hash_password(pwd)
    assert hasher_instance.verify(pwd, h)
    assert not hasher_instance.verify(pwd + "X", h)


def test_verify_and_update_no_rehash(hasher_instance):
    """
    Test that verify_and_update returns True and no new hash when the password is valid and no rehash is needed.

    Args:
        hasher_instance: An instance of the password hasher to be tested.

    Asserts:
        - The password is verified successfully (valid is True).
        - No new hash is generated (new_hash is None) when rehashing is not required.
    """
    pwd = "AnotherPass2@"
    h = hasher_instance.hash_password(pwd)
    valid, new_hash = hasher_instance.verify_and_update(pwd, h)
    assert valid is True
    assert new_hash is None


def test_verify_and_update_wrong_password(hasher_instance):
    """
    Test that verify_and_update returns (False, None) when an incorrect password is provided.

    This test ensures that when a password differing from the original is checked using
    the hasher_instance's verify_and_update method, the method correctly identifies the
    password as invalid and does not produce a new hash.
    """
    pwd = "SecretX3#"
    h = hasher_instance.hash_password(pwd)
    valid, new_hash = hasher_instance.verify_and_update(pwd + "!", h)
    assert valid is False
    assert new_hash is None


@pytest.mark.parametrize("length", [8, 16, 32])
def test_generate_password_length_and_complexity(length):
    """
    Test that the PasswordHasher.generate_password method returns a password of the specified length
    and meets complexity requirements: contains at least one uppercase letter, one lowercase letter,
    one digit, and one punctuation character defined in PasswordHasher.PUNCTUATION.
    """
    pwd = PasswordHasher.generate_password(length)
    assert len(pwd) == length

    # complexity requirements
    assert any(c.isupper() for c in pwd)
    assert any(c.islower() for c in pwd)
    assert any(c.isdigit() for c in pwd)
    assert any(c in PasswordHasher.PUNCTUATION for c in pwd)


def test_generate_password_too_short():
    """
    Test that PasswordHasher.generate_password raises a PasswordPolicyError
    when attempting to generate a password that is too short.
    """
    with pytest.raises(PasswordPolicyError) as excinfo:
        PasswordHasher.generate_password(7)
    assert "too short" in str(excinfo.value)


def test_validate_password_success():
    """
    Test that PasswordHasher.validate_password does not raise an exception
    when given a password that meets all validation requirements.
    """
    # meets all requirements
    valid_pwd = "Aa1!" + "xyzXYZ"
    # should not raise
    PasswordHasher.validate_password(valid_pwd)


@pytest.mark.parametrize(
    "pwd, substring",
    [
        ("Aa1!", "too short"),  # length < 8
        ("aa1!abcd", "uppercase"),  # missing uppercase
        ("AA1!ABCD", "lowercase"),  # missing lowercase
        ("Aa!bcdefg", "digit"),  # missing digit
        ("Aa1bcdefg", "special"),  # missing punctuation
    ],
)
def test_validate_password_errors(pwd, substring):
    """
    Tests that the PasswordHasher.validate_password method raises a PasswordPolicyError
    when given an invalid password, and asserts that the error message contains the
    expected substring.

    Args:
        pwd (str): The password to validate.
        substring (str): The expected substring to be found in the exception message.

    Raises:
        AssertionError: If PasswordPolicyError is not raised or the expected substring
        is not found in the exception message.
    """
    with pytest.raises(PasswordPolicyError) as excinfo:
        PasswordHasher.validate_password(pwd)
    assert substring in str(excinfo.value).lower()


@pytest.mark.parametrize(
    "pwd, expected",
    [
        ("Aa1!abcd", True),
        ("short1!", False),
        ("NOLOWER1!", False),
        ("noupper1!", False),
        ("NoDigit!!", False),
        ("NoSpec123", False),
    ],
)
def test_is_valid_password(pwd, expected):
    """
    Tests whether the PasswordHasher.is_valid_password method correctly determines
    if a given password is valid.

    Args:
        pwd (str): The password string to be validated.
        expected (bool): The expected boolean result indicating if the password should be considered valid.

    Asserts:
        That PasswordHasher.is_valid_password(pwd) returns the expected result.
    """
    assert PasswordHasher.is_valid_password(pwd) is expected

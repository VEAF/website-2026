import logging

import bcrypt

logger = logging.getLogger(__name__)


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return bcrypt.checkpw(plain_password.encode(), hashed_password.encode())
    except ValueError:
        # Not a bcrypt hash (e.g. an Argon2 hash imported from the legacy site, or an empty value):
        # refuse the password instead of failing; the user can still reset it.
        logger.warning("Stored password is not a bcrypt hash (prefix %r)", hashed_password[:4])
        return False

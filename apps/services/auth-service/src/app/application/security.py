import base64
import hashlib
import hmac
import json
import os
from datetime import UTC, datetime, timedelta
from uuid import UUID

JWT_ALGORITHM = "HS256"
JWT_ISSUER = "super-trunfo-auth-service"
JWT_TTL_SECONDS = 3600
PASSWORD_ITERATIONS = 120_000


def base64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def json_base64url(payload: dict[str, object]) -> str:
    return base64url_encode(
        json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8")
    )


def current_jwt_secret() -> str:
    return os.getenv("AUTH_JWT_SECRET", "local-dev-secret-change-me")


def hash_password(password: str, *, salt: bytes | None = None) -> str:
    actual_salt = salt or os.urandom(16)
    digest = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        actual_salt,
        PASSWORD_ITERATIONS,
    )

    return (
        f"pbkdf2_sha256${PASSWORD_ITERATIONS}$"
        f"{base64url_encode(actual_salt)}${base64url_encode(digest)}"
    )


def verify_password(password: str, password_hash: str) -> bool:
    try:
        algorithm, iterations, encoded_salt, encoded_digest = password_hash.split("$", 3)
    except ValueError:
        return False

    if algorithm != "pbkdf2_sha256":
        return False

    padding = "=" * (-len(encoded_salt) % 4)
    salt = base64.urlsafe_b64decode(f"{encoded_salt}{padding}")
    expected = hash_password(password, salt=salt).split("$", 3)[3]

    return hmac.compare_digest(expected, encoded_digest) and int(iterations) == PASSWORD_ITERATIONS


def create_access_token(
    *,
    player_id: UUID,
    secret: str | None = None,
    now: datetime | None = None,
    expires_in: int = JWT_TTL_SECONDS,
) -> str:
    issued_at = now or datetime.now(UTC)
    expires_at = issued_at + timedelta(seconds=expires_in)
    header = {"alg": JWT_ALGORITHM, "typ": "JWT"}
    payload = {
        "iss": JWT_ISSUER,
        "sub": str(player_id),
        "iat": int(issued_at.timestamp()),
        "exp": int(expires_at.timestamp()),
    }
    signing_input = f"{json_base64url(header)}.{json_base64url(payload)}"
    signature = hmac.new(
        (secret or current_jwt_secret()).encode("utf-8"),
        signing_input.encode("ascii"),
        hashlib.sha256,
    ).digest()

    return f"{signing_input}.{base64url_encode(signature)}"

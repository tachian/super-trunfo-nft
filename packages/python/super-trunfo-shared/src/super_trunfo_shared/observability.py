import json
import logging
import re
from collections.abc import Mapping
from typing import Any
from uuid import uuid4

from pythonjsonlogger import json as jsonlogger

SENSITIVE_KEYS = {
    "authorization",
    "access_token",
    "celular",
    "cpf",
    "email",
    "full_name",
    "name",
    "nome",
    "password",
    "phone",
    "senha",
    "secret",
    "telefone",
    "token",
}
SENSITIVE_KEY_PARTS = ("password", "senha", "secret", "authorization")
EMAIL_PATTERN = re.compile(r"^([^@\s])([^@\s]*)@(.+)$")
DIGIT_PATTERN = re.compile(r"\d")


def configure_json_logging() -> None:
    root_logger = logging.getLogger()

    if getattr(root_logger, "_super_trunfo_json_logging", False):
        return

    handler = logging.StreamHandler()
    formatter = jsonlogger.JsonFormatter(
        "%(asctime)s %(levelname)s %(name)s %(message)s %(service)s %(context)s "
        "%(correlation_id)s %(event)s %(method)s %(path)s %(status_code)s"
    )
    handler.setFormatter(formatter)

    root_logger.handlers.clear()
    root_logger.addHandler(handler)
    root_logger.setLevel(logging.INFO)
    root_logger._super_trunfo_json_logging = True  # type: ignore[attr-defined]


def is_sensitive_key(key: str) -> bool:
    normalized = key.lower()
    return (
        normalized in SENSITIVE_KEYS
        or normalized.endswith("_token")
        or any(part in normalized for part in SENSITIVE_KEY_PARTS)
    )


def mask_email(value: str) -> str:
    match = EMAIL_PATTERN.match(value)

    if not match:
        return "[MASKED_EMAIL]"

    return f"{match.group(1)}***@{match.group(3)}"


def mask_digits(value: str, *, prefix: str = "") -> str:
    digits = DIGIT_PATTERN.findall(value)

    if len(digits) <= 2:
        return f"{prefix}**"

    return f"{prefix}{'*' * (len(digits) - 2)}{''.join(digits[-2:])}"


def mask_cpf(value: str) -> str:
    digits = DIGIT_PATTERN.findall(value)

    if len(digits) <= 2:
        return "***.***.***-**"

    return f"***.***.***-{''.join(digits[-2:])}"


def mask_name(value: str) -> str:
    parts = value.split()

    if not parts:
        return "[MASKED_NAME]"

    return " ".join(f"{part[0]}***" for part in parts if part)


def mask_sensitive_value(key: str, value: Any) -> Any:
    if value is None:
        return None

    normalized = key.lower()
    string_value = str(value)

    if (
        normalized in {"access_token", "token"}
        or normalized.endswith("_token")
        or any(part in normalized for part in SENSITIVE_KEY_PARTS)
    ):
        return "[REDACTED]"

    if "email" in normalized:
        return mask_email(string_value)

    if "cpf" in normalized:
        return mask_cpf(string_value)

    if "phone" in normalized or "telefone" in normalized or "celular" in normalized:
        return mask_digits(string_value)

    if "name" in normalized or "nome" in normalized:
        return mask_name(string_value)

    return value


def mask_sensitive_data(data: Any) -> Any:
    if isinstance(data, Mapping):
        return {
            key: mask_sensitive_value(str(key), value)
            if is_sensitive_key(str(key))
            else mask_sensitive_data(value)
            for key, value in data.items()
        }

    if isinstance(data, list):
        return [mask_sensitive_data(item) for item in data]

    return data


def parse_json_body(body: bytes) -> Any:
    if not body:
        return None

    try:
        return json.loads(body.decode("utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError):
        return "[UNPARSEABLE_BODY]"


def new_correlation_id() -> str:
    return str(uuid4())

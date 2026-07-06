"""Shared redaction key/pattern set - single source of truth (mirrored by node/src/redaction.js)."""

import re

SENSITIVE_KEYS = {
    "password", "new_password", "old_password", "passwd", "pwd", "secret",
    "client_secret", "token", "access_token", "refresh_token", "id_token",
    "api_key", "apikey", "authorization", "auth", "cookie", "set-cookie",
    "session", "credential",
}

MASK = "********"

_PATTERNS = [
    re.compile(r"[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}"),
    re.compile(r"Bearer\s+[A-Za-z0-9._\-]+"),
    re.compile(r"-----BEGIN(?: RSA| EC)? PRIVATE KEY-----"),
    re.compile(r"(://[^:/@\s]+:)[^@/\s]+(@)"),
]


def redact_text(value):
    if not isinstance(value, str):
        return value
    result = value
    for pattern in _PATTERNS:
        if pattern.groups:
            result = pattern.sub(lambda m: m.group(1) + MASK + m.group(2), result)
        else:
            result = pattern.sub(MASK, result)
    return result


def redact_value(value, key=None):
    if key is not None and str(key).lower() in SENSITIVE_KEYS:
        return MASK
    if isinstance(value, str):
        return redact_text(value)
    if isinstance(value, dict):
        return {k: redact_value(v, k) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return type(value)(redact_value(v) for v in value)
    return value

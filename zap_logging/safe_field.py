"""L-8: strip/escape control characters from untrusted values before they become log fields."""

import re

_CONTROL_CHARS = re.compile(r"[\r\n\t\x00-\x1f\x7f]")


def safe_field(value):
    if not isinstance(value, str):
        return value
    return _CONTROL_CHARS.sub(" ", value)

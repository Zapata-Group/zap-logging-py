import json
import logging
import os
import socket
import sys
from datetime import datetime, timezone

from .redaction import redact_value

_SENSITIVE_HATCH_WARNED = False
_PROD_DEBUG_WARNED = False

_AUDIT_PRESERVED_KEYS = {"user", "source_ip", "target"}


def _service_name():
    return os.getenv("SERVICE_NAME") or os.path.basename(os.getcwd()) or socket.gethostname()


def _env():
    return os.getenv("APP_ENV", "development")


def _sensitive_allowed():
    return os.getenv("LOG_ALLOW_SENSITIVE", "").lower() == "true" and _env() != "production"


def _resolved_level():
    global _PROD_DEBUG_WARNED
    level_name = os.getenv("LOG_LEVEL", "INFO").upper()
    if level_name == "DEBUG" and _env() == "production":
        if not _PROD_DEBUG_WARNED:
            _PROD_DEBUG_WARNED = True
            logging.getLogger("zap_logging").warning(
                "DEBUG requested in production; downgraded to INFO"
            )
        return logging.INFO
    return getattr(logging, level_name, logging.INFO)


class _RedactionFilter(logging.Filter):
    def filter(self, record):
        global _SENSITIVE_HATCH_WARNED
        if _sensitive_allowed():
            if not _SENSITIVE_HATCH_WARNED and os.getenv("LOG_ALLOW_SENSITIVE", "").lower() == "true":
                _SENSITIVE_HATCH_WARNED = True
            return True

        if isinstance(record.msg, str):
            record.msg = redact_value(record.msg)
        if record.args:
            if isinstance(record.args, dict):
                record.args = redact_value(record.args)
            else:
                record.args = tuple(redact_value(a) for a in record.args)

        extra = getattr(record, "extra_fields", None)
        if isinstance(extra, dict):
            record.extra_fields = {
                k: (v if k in _AUDIT_PRESERVED_KEYS and extra.get("audit") else redact_value(v, k))
                for k, v in extra.items()
            }

        return True


class _JsonFormatter(logging.Formatter):
    def format(self, record):
        envelope = {
            "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "level": record.levelname,
            "service": _service_name(),
            "env": _env(),
            "message": record.getMessage(),
        }
        extra = getattr(record, "extra_fields", None)
        if isinstance(extra, dict):
            envelope.update(extra)
        if record.exc_info:
            envelope["exception"] = self.formatException(record.exc_info)
        return json.dumps(envelope, default=str)


class _ExtraAdapter(logging.LoggerAdapter):
    def process(self, msg, kwargs):
        extra = kwargs.pop("extra", None)
        if extra is not None:
            kwargs["extra"] = {"extra_fields": extra}
        return msg, kwargs


def get_logger(name):
    base = logging.getLogger(name)
    base.setLevel(_resolved_level())

    if not any(isinstance(h, logging.StreamHandler) for h in base.handlers):
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(_JsonFormatter())
        handler.addFilter(_RedactionFilter())
        base.addHandler(handler)
        base.propagate = False

    return _ExtraAdapter(base, {})


_audit_logger = None


def _get_audit_logger():
    global _audit_logger
    if _audit_logger is None:
        _audit_logger = get_logger("zap_logging.audit")
    return _audit_logger


_audit_sinks = []


def register_audit_sink(fn):
    """L-13: register an additional sink; audit() fans out to stdout + every registered sink."""
    _audit_sinks.append(fn)


def _stdout_audit_sink(event, payload):
    level = logging.INFO if payload.get("outcome") == "success" else logging.WARNING
    _get_audit_logger().log(level, event, extra={"audit": True, **payload})


def audit(event, *, outcome, user=None, source_ip=None, target=None, **fields):
    payload = {"event": event, "outcome": outcome}
    if user is not None:
        payload["user"] = user
    if source_ip is not None:
        payload["source_ip"] = source_ip
    if target is not None:
        payload["target"] = target

    redacted_fields = {
        k: (v if k in _AUDIT_PRESERVED_KEYS else redact_value(v, k))
        for k, v in fields.items()
    }
    payload.update(redacted_fields)

    for sink in [_stdout_audit_sink, *_audit_sinks]:
        try:
            sink(event, payload)
        except Exception:
            logging.getLogger("zap_logging").exception(
                "audit sink failed", extra={"extra_fields": {"sink": getattr(sink, "__name__", repr(sink))}}
            )

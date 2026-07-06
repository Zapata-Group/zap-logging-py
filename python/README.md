# zap_logging

Shared structured-logging library for zap Python services. See
[../../compliance/policy/logging-libraries.md](../../compliance/policy/logging-libraries.md) for
the full behavior contract (L-1...L-13).

## Install

```
pip install "zap_logging @ git+https://github.com/<org>/zap-logging.git@v1.0.0#subdirectory=python"
```

## Usage

```python
from zap_logging import get_logger, audit, register_audit_sink

log = get_logger(__name__)
log.info("scan.start", extra={"folder_count": 12})

audit("auth.login", outcome="success", user=email, source_ip=ip, target=user_id)
```

## Migration shims

```python
from zap_logging.shims import marqo_indexer_get_logger as get_logger
from zap_logging.shims import opportunity_crawler_configure_logging as configure_logging
```

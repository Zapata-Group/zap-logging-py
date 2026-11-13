# zap-logging-py

Shared structured-logging library for zap Python services, implementing zap's logging
policy (L-1...L-13): JSON to stdout, level and redaction handling, an `audit()` helper,
and additional audit sinks.

The Python package lives at the repository root. Redaction keys and patterns are
defined in `zap_logging/redaction.py`.

See the full policy in the `compliance` repo: `policy/logging-libraries.md`.

## Install

Pin clients to a tag or commit containing the root package layout:

```sh
pip install "zap_logging @ git+https://github.com/Zapata-Group/zap-logging-py.git@<tag-or-commit>"
```

In `requirements.txt`, replace `<tag-or-commit>` with the chosen release or commit:

```text
zap_logging @ git+https://github.com/Zapata-Group/zap-logging-py.git@<tag-or-commit>
```

Older releases that still store the package under `python/` require their original
subdirectory install URL.

For local development, run from the repository root:

```sh
pip install -e .
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

## Versioning

Tag releases (`v1.0.0`, `v1.1.0`, ...) in this repository.

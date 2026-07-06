"""Migration shims for existing per-app logger factories (L-1/L-12: stdout is now the primary sink).

marqo-indexer/indexer/utils.py:get_logger(name, log_filename, level) and
opportunity-crawler/utils.py:configure_logging() keep their call-site signatures but delegate
here, ignoring file-based sinks.
"""

import logging

from .core import get_logger as _get_logger, _resolved_level


def marqo_indexer_get_logger(name, log_filename=None, level=None):
    """Drop-in replacement for indexer/utils.py:get_logger(name, log_filename, level).

    `log_filename` is accepted for signature compatibility but ignored: file logging is
    deprecated as a primary sink in favor of stdout JSON (L-1/L-12).
    """
    return _get_logger(name)


def opportunity_crawler_configure_logging(default_level="INFO"):
    """Drop-in replacement for utils.py:configure_logging(default_level).

    Reconfigures the root logger to emit via zap_logging instead of the old
    color-console/file setup. `CRAWLER_LOG_FILE` is no longer honored.
    """
    adapter = _get_logger(None)
    root = logging.getLogger()
    root.setLevel(_resolved_level())
    return adapter

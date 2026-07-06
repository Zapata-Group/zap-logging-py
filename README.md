# zap-logging

Canonical logging libraries implementing zap's logging policy (L-1...L-13). One hardened
implementation per platform; apps adopt the library instead of rolling their own.

- [`python/`](python/) — `zap_logging`, importable Python package.
- [`node/`](node/) — `@zap/logging`, pino-based Node package.

Both share the same behavior contract (JSON-to-stdout envelope, level/redaction handling,
`audit()` helper, dual-sink adapter) and the same redaction key/pattern set, kept in lockstep
across `python/zap_logging/redaction.py` and `node/src/redaction.js`.

See the policy spec in the `compliance` repo: `policy/logging-libraries.md`.

## Versioning

Tag releases (`v1.0.0`, `v1.1.0`, ...) covering both packages together. Consumers pin to a tag
via a git dependency:

```
# Python (requirements.txt)
zap_logging @ git+https://github.com/<org>/zap-logging.git@v1.0.0#subdirectory=python

# Node (package.json)
"@zap/logging": "github:<org>/zap-logging#v1.0.0"
```

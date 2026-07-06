# @zap/logging

Shared structured-logging library for zap Node services, built on pino. See
[../../compliance/policy/logging-libraries.md](../../compliance/policy/logging-libraries.md) for
the full behavior contract (L-1...L-13).

## Install

```
npm install github:<org>/zap-logging#v1.0.0
```

(package lives at the repo root's `node/` subdirectory; see `postinstall`/workspace notes in the
main repo README if `npm install github:` doesn't resolve subdirectories on your npm version —
pin a subpath via `github:<org>/zap-logging#v1.0.0:node` on npm >=9.)

## Usage

```js
const { logger, audit, registerAuditSink } = require('@zap/logging');

logger.info({ event: 'mail.send', outcome: 'success', request_id, to_count }, 'sent');
logger.error({ event: 'mail.send', outcome: 'failure', error_code }, 'send failed');

audit('mail.send', { outcome: 'success', user, source_ip, target });
```

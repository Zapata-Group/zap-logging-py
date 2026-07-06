'use strict';

// Shared redaction key/pattern set - single source of truth (mirrored by python/zap_logging/redaction.py).

const SENSITIVE_KEYS = [
  'password', 'new_password', 'old_password', 'passwd', 'pwd', 'secret',
  'client_secret', 'token', 'access_token', 'refresh_token', 'id_token',
  'api_key', 'apikey', 'authorization', 'auth', 'cookie', 'set-cookie',
  'session', 'credential',
];

const MASK = '********';

function pinoRedactPaths() {
  const variants = [];
  for (const key of SENSITIVE_KEYS) {
    variants.push(key, `*.${key}`, `*.*.${key}`);
  }
  return variants;
}

const PATTERNS = [
  /[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}/g,
  /Bearer\s+[A-Za-z0-9._-]+/g,
  /-----BEGIN(?: RSA| EC)? PRIVATE KEY-----/g,
  /(:\/\/[^:/@\s]+:)[^@/\s]+(@)/g,
];

function redactText(value) {
  if (typeof value !== 'string') return value;
  let result = value;
  for (const pattern of PATTERNS) {
    result = pattern.source.includes('(')
      ? result.replace(pattern, (_m, p1, p2) => `${p1}${MASK}${p2}`)
      : result.replace(pattern, MASK);
  }
  return result;
}

module.exports = { SENSITIVE_KEYS, MASK, pinoRedactPaths, redactText };

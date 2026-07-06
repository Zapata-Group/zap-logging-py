'use strict';

const pino = require('pino');
const { pinoRedactPaths, redactText, MASK } = require('./redaction');
const { safeField } = require('./safeField');

const AUDIT_PRESERVED_KEYS = new Set(['user', 'source_ip', 'target']);

let sensitiveHatchWarned = false;
let prodDebugWarned = false;

function env() {
  return process.env.APP_ENV || 'development';
}

function sensitiveAllowed() {
  return process.env.LOG_ALLOW_SENSITIVE === 'true' && env() !== 'production';
}

function resolvedLevel() {
  const requested = (process.env.LOG_LEVEL || 'info').toLowerCase();
  if (requested === 'debug' && env() === 'production') {
    if (!prodDebugWarned) {
      prodDebugWarned = true;
      // eslint-disable-next-line no-console
      console.warn(JSON.stringify({ level: 'WARNING', message: 'DEBUG requested in production; downgraded to INFO' }));
    }
    return 'info';
  }
  return requested;
}

function scrubStrings(obj, preserveTopLevelAuditKeys) {
  if (typeof obj === 'string') return redactText(obj);
  if (Array.isArray(obj)) return obj.map((v) => scrubStrings(v));
  if (obj && typeof obj === 'object') {
    const isAuditRecord = preserveTopLevelAuditKeys && obj.audit === true;
    const out = {};
    for (const [k, v] of Object.entries(obj)) {
      out[k] = isAuditRecord && AUDIT_PRESERVED_KEYS.has(k) ? v : scrubStrings(v);
    }
    return out;
  }
  return obj;
}

const redactConfig = sensitiveAllowed()
  ? undefined
  : { paths: pinoRedactPaths(), censor: MASK };

if (sensitiveAllowed() && process.env.LOG_ALLOW_SENSITIVE === 'true' && !sensitiveHatchWarned) {
  sensitiveHatchWarned = true;
}

const logger = pino({
  level: resolvedLevel(),
  timestamp: pino.stdTimeFunctions.isoTime,
  messageKey: 'message',
  base: { service: process.env.SERVICE_NAME || require('path').basename(process.cwd()), env: env() },
  redact: redactConfig,
  formatters: {
    log(object) {
      return sensitiveAllowed() ? object : scrubStrings(object, true);
    },
  },
});

const auditSinks = [];

function registerAuditSink(fn) {
  // L-13: register an additional sink; audit() fans out to stdout + every registered sink.
  auditSinks.push(fn);
}

function stdoutAuditSink(event, payload) {
  const level = payload.outcome === 'success' ? 'info' : 'warn';
  logger[level]({ audit: true, ...payload }, event);
}

function audit(event, fields = {}) {
  const { outcome, user, source_ip: sourceIp, target, ...rest } = fields;
  const payload = { event, outcome };
  if (user !== undefined) payload.user = user;
  if (sourceIp !== undefined) payload.source_ip = sourceIp;
  if (target !== undefined) payload.target = target;

  for (const [k, v] of Object.entries(rest)) {
    payload[k] = AUDIT_PRESERVED_KEYS.has(k) ? v : scrubStrings(v);
  }

  for (const sink of [stdoutAuditSink, ...auditSinks]) {
    try {
      sink(event, payload);
    } catch (err) {
      logger.error({ sink: sink.name || 'anonymous', err: err.message }, 'audit sink failed');
    }
  }
}

module.exports = { logger, audit, registerAuditSink, safeField };

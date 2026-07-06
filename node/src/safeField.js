'use strict';

// L-8: strip/escape control characters from untrusted values before they become log fields.

const CONTROL_CHARS = /[\r\n\t\x00-\x1f\x7f]/g;

function safeField(value) {
  if (typeof value !== 'string') return value;
  return value.replace(CONTROL_CHARS, ' ');
}

module.exports = { safeField };

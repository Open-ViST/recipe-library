'use strict';

const fs = require('node:fs');

function writeAll(fd, text) {
  const bytes = Buffer.from(text, 'utf8');
  let offset = 0;
  while (offset < bytes.length) {
    const written = fs.writeSync(fd, bytes, offset, bytes.length - offset);
    if (written <= 0) throw new Error('Output write failure');
    offset += written;
  }
}

function invalid() {
  throw new Error('Invalid input');
}

function readAndValidate() {
  if (process.argv.length !== 2) invalid();

  const buffer = Buffer.alloc(65537);
  let length = 0;
  while (length < buffer.length) {
    const count = fs.readSync(0, buffer, length, buffer.length - length, null);
    if (count === 0) break;
    length += count;
  }
  if (length > 65536) invalid();

  const decoder = new TextDecoder('utf-8', { fatal: true, ignoreBOM: true });
  const text = decoder.decode(buffer.subarray(0, length));
  if (text.charCodeAt(0) === 0xFEFF) invalid();
  if (/[\u0000-\u0009\u000B-\u001F\u007F]/.test(text)) invalid();

  const keyPattern = /^[A-Za-z_][A-Za-z0-9_]{0,63}$/;
  const selectors = new Set();
  const assignments = [];
  let separatorSeen = false;
  let assignmentCount = 0;
  let valueBytes = 0;

  for (const line of text.split('\n')) {
    if (line === '' || line.startsWith('#')) continue;

    if (line === '---') {
      if (separatorSeen) invalid();
      separatorSeen = true;
      continue;
    }

    if (!separatorSeen) {
      if (!keyPattern.test(line)) invalid();
      if (selectors.has(line) || selectors.size >= 100) invalid();
      selectors.add(line);
      continue;
    }

    assignmentCount += 1;
    if (assignmentCount > 100) invalid();
    const equals = line.indexOf('=');
    if (equals < 0) invalid();
    const key = line.slice(0, equals);
    const value = line.slice(equals + 1);
    if (!keyPattern.test(key)) invalid();
    valueBytes += Buffer.byteLength(value, 'utf8');
    if (valueBytes > 1024) invalid();
    assignments.push({
      key,
      value: selectors.has(key) ? '[REDACTED]' : value
    });
  }

  if (!separatorSeen) invalid();
  return { assignments };
}

let result;
try {
  result = readAndValidate();
} catch {
  writeAll(2, 'error: invalid input\n');
  process.exit(2);
}

writeAll(1, JSON.stringify(result) + '\n');

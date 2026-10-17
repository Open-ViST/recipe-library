'use strict';

const fs = require('node:fs');

function audit() {
  if (process.argv.length !== 2) throw new Error();

  const buffer = Buffer.alloc(65537);
  let used = 0;
  while (used < buffer.length) {
    const count = fs.readSync(0, buffer, used, buffer.length - used, null);
    if (count === 0) break;
    used += count;
  }
  if (used > 65536) throw new Error();

  const text = new TextDecoder('utf-8', {
    fatal: true,
    ignoreBOM: true
  }).decode(buffer.subarray(0, used));

  if (text.startsWith('\uFEFF')) throw new Error();
  if (/[\u0000-\u0009\u000B-\u001F\u007F]/.test(text)) {
    throw new Error();
  }

  const keyPattern = /^[A-Za-z_][A-Za-z0-9_]{0,63}$/;
  const required = new Set();
  const assigned = new Map();
  const emptyRequired = new Set();
  let separatorSeen = false;
  let selectorCount = 0;
  let assignmentCount = 0;
  let valueBytes = 0;

  for (const line of text.split('\n')) {
    if (line === '---') {
      if (separatorSeen) throw new Error();
      separatorSeen = true;
      continue;
    }
    if (line === '' || line.startsWith('#')) continue;

    if (!separatorSeen) {
      selectorCount += 1;
      if (selectorCount > 100 || !keyPattern.test(line) || required.has(line)) {
        throw new Error();
      }
      required.add(line);
      continue;
    }

    assignmentCount += 1;
    if (assignmentCount > 100) throw new Error();
    const equals = line.indexOf('=');
    if (equals < 0) throw new Error();
    const key = line.slice(0, equals);
    if (!keyPattern.test(key)) throw new Error();
    const value = line.slice(equals + 1);
    valueBytes += Buffer.byteLength(value, 'utf8');
    if (valueBytes > 1024) throw new Error();

    let positions = assigned.get(key);
    if (positions === undefined) {
      positions = [];
      assigned.set(key, positions);
    }
    positions.push(assignmentCount);
    if (value === '' && required.has(key)) emptyRequired.add(key);
  }

  if (!separatorSeen) throw new Error();

  const missing = [];
  for (const key of required) {
    if (!assigned.has(key)) missing.push(key);
  }
  missing.sort();

  const empty = Array.from(emptyRequired).sort();
  const duplicates = [];
  const unknown = [];
  const assignedKeys = Array.from(assigned.keys()).sort();
  for (const key of assignedKeys) {
    const positions = assigned.get(key);
    if (positions.length >= 2) duplicates.push({ key, positions });
    if (!required.has(key)) unknown.push(key);
  }

  return JSON.stringify({ missing, empty, duplicates, unknown }) + '\n';
}

let output;
try {
  output = audit();
} catch {
  process.stderr.write('error: invalid input\n');
  process.exit(2);
}
process.stdout.write(output);

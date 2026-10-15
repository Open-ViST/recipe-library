'use strict';

const fs = require('node:fs');

let output;
try {
  if (process.argv.length !== 2) {
    throw new Error();
  }

  const maxBytes = 65536;
  const buffer = Buffer.alloc(maxBytes + 1);
  let used = 0;

  while (used < buffer.length) {
    const count = fs.readSync(0, buffer, used, buffer.length - used, null);
    if (count === 0) break;
    used += count;
  }

  if (used > maxBytes) {
    throw new Error();
  }

  const decoder = new TextDecoder('utf-8', {
    fatal: true,
    ignoreBOM: true
  });
  const text = decoder.decode(buffer.subarray(0, used));
  const assignments = JSON.parse(text);

  if (!Array.isArray(assignments) || assignments.length > 100) {
    throw new Error();
  }

  const positionsByKey = new Map();
  const keyPattern = /^[A-Za-z][A-Za-z0-9_]{0,63}$/;

  for (let i = 0; i < assignments.length; i += 1) {
    const assignment = assignments[i];
    if (typeof assignment !== 'string') {
      throw new Error();
    }

    const separator = assignment.indexOf('=');
    if (separator < 0) {
      throw new Error();
    }

    const key = assignment.slice(0, separator);
    const match = keyPattern.exec(key);
    if (match === null || match[0] !== key) {
      throw new Error();
    }

    const position = i + 1;
    if (!Number.isSafeInteger(position)) {
      throw new Error();
    }

    let positions = positionsByKey.get(key);
    if (positions === undefined) {
      positions = [];
      positionsByKey.set(key, positions);
    }
    positions.push(position);
  }

  const repeated = [];
  for (const [key, positions] of positionsByKey) {
    if (positions.length >= 2) {
      repeated.push({ key, positions });
    }
  }

  repeated.sort((a, b) => a.key < b.key ? -1 : a.key > b.key ? 1 : 0);
  output = JSON.stringify({ repeated }) + '\n';
} catch {
  process.stderr.write('error: invalid request\n');
  process.exit(2);
}

// Output-write failures are deliberately outside the input-error guarantee.
process.stdout.write(output);

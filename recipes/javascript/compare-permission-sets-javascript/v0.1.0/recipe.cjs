'use strict';

const { readSync } = require('node:fs');

let output;
try {
  if (process.argv.length !== 2) {
    throw new Error();
  }

  const bytes = Buffer.alloc(65537);
  let used = 0;
  while (used < bytes.length) {
    const count = readSync(0, bytes, used, bytes.length - used, null);
    if (count === 0) break;
    used += count;
  }
  if (used > 65536) {
    throw new Error();
  }

  const text = new TextDecoder('utf-8', {
    fatal: true,
    ignoreBOM: true
  }).decode(bytes.subarray(0, used));
  const input = JSON.parse(text);

  if (input === null || typeof input !== 'object' || Array.isArray(input)) {
    throw new Error();
  }

  function permissionSet(values) {
    if (!Array.isArray(values) || values.length > 100) {
      throw new Error();
    }
    const result = new Set();
    for (const value of values) {
      if (typeof value !== 'string' || value.length === 0 || value.length > 80) {
        throw new Error();
      }
      result.add(value);
    }
    return result;
  }

  const before = permissionSet(input.before);
  const after = permissionSet(input.after);
  const added = [];
  const removed = [];
  const unchanged = [];

  for (const label of after) {
    if (!before.has(label)) added.push(label);
  }
  for (const label of before) {
    if (after.has(label)) unchanged.push(label);
    else removed.push(label);
  }

  added.sort();
  removed.sort();
  unchanged.sort();
  output = JSON.stringify({ added, removed, unchanged });
} catch {
  process.stderr.write('error: invalid input\n');
  process.exit(2);
}

// Output-write failures are deliberately outside the input-error handler.
process.stdout.write(output + '\n');

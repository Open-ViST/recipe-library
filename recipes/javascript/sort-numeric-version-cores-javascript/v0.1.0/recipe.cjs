'use strict';

const fs = require('node:fs');

function main() {
  if (process.argv.length !== 2) {
    throw new Error();
  }

  const bytes = Buffer.alloc(65537);
  let used = 0;
  while (used < bytes.length) {
    const count = fs.readSync(0, bytes, used, bytes.length - used, null);
    if (count === 0) break;
    used += count;
  }
  if (used > 65536) {
    throw new Error();
  }

  const decoder = new TextDecoder('utf-8', {
    fatal: true,
    ignoreBOM: true
  });
  const text = decoder.decode(bytes.subarray(0, used));
  const input = JSON.parse(text);
  if (!Array.isArray(input) || input.length > 100) {
    throw new Error();
  }

  const corePattern = /^(0|[1-9][0-9]{0,5})\.(0|[1-9][0-9]{0,5})\.(0|[1-9][0-9]{0,5})$/;
  const records = [];
  for (const original of input) {
    if (typeof original !== 'string') {
      throw new Error();
    }
    const match = corePattern.exec(original);
    // JavaScript's $ can match before a final newline; require a full match.
    if (match === null || match[0] !== original) {
      throw new Error();
    }
    const major = Number(match[1]);
    const minor = Number(match[2]);
    const patch = Number(match[3]);
    for (const component of [major, minor, patch]) {
      if (!Number.isSafeInteger(component) || component < 0 || component > 999999) {
        throw new Error();
      }
    }
    records.push({ original, major, minor, patch });
  }

  records.sort((a, b) =>
    a.major - b.major || a.minor - b.minor || a.patch - b.patch
  );
  return JSON.stringify({ versions: records.map(record => record.original) });
}

let output;
try {
  output = main();
} catch {
  process.stderr.write('error: invalid input\n', () => process.exit(2));
  return;
}

// Output writes are intentionally outside the input-error handling guarantee.
process.stdout.write(output + '\n');

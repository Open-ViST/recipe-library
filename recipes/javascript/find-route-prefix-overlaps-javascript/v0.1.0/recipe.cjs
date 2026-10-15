'use strict';

let result;

try {
  if (process.argv.length !== 2) {
    throw new Error();
  }

  const { readSync } = require('node:fs');
  const buffer = Buffer.alloc(65537);
  let used = 0;

  while (used < buffer.length) {
    const count = readSync(0, buffer, used, buffer.length - used, null);
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
  const text = decoder.decode(buffer.subarray(0, used));
  const paths = JSON.parse(text);

  if (!Array.isArray(paths) || paths.length > 20) {
    throw new Error();
  }

  // Require the absolute end of the string, including after newlines.
  const pathPattern = /^\/(?:[A-Za-z0-9_-]+(?:\/[A-Za-z0-9_-]+)*)?(?![\s\S])/;
  for (const path of paths) {
    if (typeof path !== 'string' || path.length === 0 ||
        path.length > 120 || !pathPattern.test(path)) {
      throw new Error();
    }
  }

  const overlaps = [];
  for (let i = 0; i < paths.length; i++) {
    for (let j = i + 1; j < paths.length; j++) {
      const first = paths[i];
      const second = paths[j];
      if (first === second || first === '/' || second === '/' ||
          first.startsWith(second + '/') ||
          second.startsWith(first + '/')) {
        overlaps.push({ first: i + 1, second: j + 1 });
      }
    }
  }

  result = { overlaps };
} catch {
  process.stderr.write('error: invalid input\n');
  process.exit(2);
}

// Output-write failures are outside input-error handling.
process.stdout.write(JSON.stringify(result) + '\n');

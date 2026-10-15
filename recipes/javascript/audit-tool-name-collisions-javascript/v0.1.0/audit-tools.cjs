'use strict';

const fs = require('node:fs');
let output;

try {
  if (process.argv.length !== 2) {
    throw new Error('Invalid input');
  }

  const limit = 65536;
  const buffer = Buffer.alloc(limit + 1);
  let used = 0;

  while (used < buffer.length) {
    const count = fs.readSync(0, buffer, used, buffer.length - used, null);
    if (count === 0) break;
    used += count;
    if (used > limit) {
      throw new Error('Invalid input');
    }
  }

  // Preserve a BOM so JSON.parse applies its native JSON syntax rules.
  const decoder = new TextDecoder('utf-8', {
    fatal: true,
    ignoreBOM: true
  });
  const input = JSON.parse(decoder.decode(buffer.subarray(0, used)));
  if (!Array.isArray(input)) {
    throw new Error('Invalid input');
  }

  const convention = /^[A-Za-z][A-Za-z0-9_-]{0,63}$/;
  const normalized = [];
  const positionsByName = new Map();

  for (let i = 0; i < input.length; i++) {
    const name = input[i];
    if (typeof name !== 'string') {
      throw new Error('Invalid input');
    }
    const match = convention.exec(name);
    // JavaScript's $ can match before a final newline; require a full match.
    if (match === null || match[0] !== name) {
      throw new Error('Invalid input');
    }

    const lower = name.toLowerCase();
    normalized.push(lower);
    if (!positionsByName.has(lower)) {
      positionsByName.set(lower, []);
    }
    positionsByName.get(lower).push(i + 1);
  }

  const collisions = [];
  for (const [name, positions] of positionsByName) {
    if (positions.length >= 2) {
      collisions.push({ name, positions });
    }
  }
  collisions.sort((a, b) => a.name < b.name ? -1 : a.name > b.name ? 1 : 0);
  output = JSON.stringify({ normalized, collisions }) + '\n';
} catch {
  process.stderr.write('error: invalid arguments, stdin, UTF-8, JSON, or tool names.\n');
  process.exit(2);
}

// Output failures are deliberately outside the input-validation handler.
process.stdout.write(output);

// SPDX-License-Identifier: MIT
// Copyright (c) 2026 OpenViST contributors
'use strict';

const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');
const url = require('node:url');
const assert = require('node:assert');

function fail(message) {
  process.stderr.write(`Error: ${message}\n`);
  process.exit(1);
}

function readInput(arg) {
  if (arg === '-') {
    return fs.readFileSync(0, 'utf8');
  }
  if (!arg) {
    fail('provide a UTF-8 text file path, or use - to read standard input');
  }
  return fs.readFileSync(path.resolve(arg), 'utf8');
}

function main() {
  const args = process.argv.slice(2);
  if (args.length !== 1) {
    fail('usage: node url-host-summary.js <file-path|->');
  }

  const text = readInput(args[0]);
  const counts = Object.create(null);
  const lines = text.split(/\r?\n/);
  const errors = [];

  for (let i = 0; i < lines.length; i += 1) {
    const line = lines[i].trim();
    if (line === '') continue;

    let parsed;
    try {
      parsed = new url.URL(line);
    } catch {
      errors.push(`line ${i + 1}: malformed URL`);
      continue;
    }

    if (parsed.protocol !== 'http:' && parsed.protocol !== 'https:') {
      errors.push(`line ${i + 1}: URL must use http or https`);
      continue;
    }
    if (!parsed.hostname) {
      errors.push(`line ${i + 1}: URL must include a hostname`);
      continue;
    }

    const hostname = parsed.hostname.toLowerCase();
    counts[hostname] = (counts[hostname] || 0) + 1;
  }

  if (errors.length > 0) {
    fail(`invalid input:\n${errors.join('\n')}`);
  }

  const sorted = Object.fromEntries(
    Object.entries(counts).sort(([a], [b]) => a.localeCompare(b))
  );
  process.stdout.write(`${JSON.stringify(sorted, null, 2)}\n`);
}

try {
  main();
} catch (error) {
  fail(error && error.message ? error.message : 'unable to process input');
}

// SPDX-License-Identifier: MIT
// Copyright (c) 2026 OpenViST contributors
'use strict';

const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');
const { fileURLToPath } = require('node:url');
const assert = require('node:assert');

// Recipe code intentionally uses only node:fs and node:path from the allowed
// built-ins. The other permitted built-ins are required but not needed here.

function fail(message) {
  process.stderr.write(`Error: ${message}\n`);
  process.stderr.write('Usage: node validate-hex-event-ids.cjs <input.json|->\n');
  process.exit(1);
}

function readInput(source) {
  if (source === '-') {
    return fs.readFileSync(0, 'utf8');
  }
  return fs.readFileSync(path.resolve(source), 'utf8');
}

function normalize(value) {
  if (typeof value !== 'string') return null;
  const withoutPrefix = value.startsWith('0x') || value.startsWith('0X')
    ? value.slice(2)
    : value;
  if (!/^[0-9a-fA-F]+$/.test(withoutPrefix)) return null;
  return withoutPrefix.toLowerCase();
}

function inspect(values) {
  const invalid = [];
  const firstPosition = new Map();
  const duplicates = [];
  const normalized = [];

  values.forEach((value, index) => {
    const position = index + 1;
    const id = normalize(value);
    if (id === null) {
      invalid.push({ position, valueType: value === null ? 'null' : typeof value });
      normalized.push(null);
      return;
    }
    normalized.push(id);
    if (firstPosition.has(id)) {
      duplicates.push({
        normalizedId: id,
        firstPosition: firstPosition.get(id),
        duplicatePosition: position
      });
    } else {
      firstPosition.set(id, position);
    }
  });

  return { valid: invalid.length === 0, normalized, invalid, duplicates };
}

function main() {
  const args = process.argv.slice(2);
  if (args.length !== 1) fail('provide exactly one input path, or - for standard input.');

  let parsed;
  try {
    parsed = JSON.parse(readInput(args[0]));
  } catch (error) {
    fail(`could not read or parse input: ${error.message}`);
  }

  if (!Array.isArray(parsed)) fail('the JSON top level must be an array.');

  const report = inspect(parsed);
  process.stdout.write(`${JSON.stringify(report, null, 2)}\n`);
  if (!report.valid) process.exit(2);
}

main();
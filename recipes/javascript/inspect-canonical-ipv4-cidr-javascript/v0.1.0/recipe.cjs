'use strict';

const fs = require('node:fs');
const { TextDecoder } = require('node:util');

function invalid() {
  throw new Error('invalid input');
}

function decimal(text, maximum, maximumDigits) {
  if (text.length === 0 || text.length > maximumDigits) invalid();
  if (text.length > 1 && text[0] === '0') invalid();
  let value = 0;
  for (let i = 0; i < text.length; i++) {
    const digit = text.charCodeAt(i) - 48;
    if (digit < 0 || digit > 9) invalid();
    value = value * 10 + digit;
  }
  if (value > maximum) invalid();
  return value;
}

function dotted(value) {
  const a = Math.floor(value / 16777216);
  value -= a * 16777216;
  const b = Math.floor(value / 65536);
  value -= b * 65536;
  const c = Math.floor(value / 256);
  const d = value - c * 256;
  return a + '.' + b + '.' + c + '.' + d;
}

function parseRecord(record) {
  const parts = record.split('/');
  if (parts.length !== 2) invalid();
  const octets = parts[0].split('.');
  if (octets.length !== 4) invalid();
  const a = decimal(octets[0], 255, 3);
  const b = decimal(octets[1], 255, 3);
  const c = decimal(octets[2], 255, 3);
  const d = decimal(octets[3], 255, 3);
  const prefix = decimal(parts[1], 32, 2);
  const address = a * 16777216 + b * 65536 + c * 256 + d;
  const size = 2 ** (32 - prefix);
  const network = Math.floor(address / size) * size;
  const last = network + size - 1;
  return {
    input: record,
    network: dotted(network),
    last: dotted(last),
    prefix: prefix,
    address_count: size,
    host_bits_set: address !== network
  };
}

function readInput() {
  const buffer = Buffer.alloc(65537);
  let length = 0;
  while (length < buffer.length) {
    const count = fs.readSync(0, buffer, length, buffer.length - length, null);
    if (count === 0) break;
    length += count;
  }
  if (length > 65536) invalid();
  const decoder = new TextDecoder('utf-8', {
    fatal: true,
    ignoreBOM: true
  });
  const text = decoder.decode(buffer.subarray(0, length));
  if (text.length > 0 && text.charCodeAt(0) === 0xFEFF) invalid();
  for (let i = 0; i < text.length; i++) {
    const c = text.charCodeAt(i);
    if (c !== 10 && c !== 46 && c !== 47 && !(c >= 48 && c <= 57)) {
      invalid();
    }
  }
  return text;
}

function writeAll(fd, text) {
  const buffer = Buffer.from(text, 'utf8');
  let offset = 0;
  while (offset < buffer.length) {
    const count = fs.writeSync(fd, buffer, offset, buffer.length - offset, null);
    if (count <= 0) throw new Error('output write failed');
    offset += count;
  }
}

let output;
try {
  if (process.argv.length !== 2) invalid();
  const text = readInput();
  const networks = [];
  for (const record of text.split('\n')) {
    if (record === '') continue;
    if (networks.length >= 100) invalid();
    networks.push(parseRecord(record));
  }
  output = JSON.stringify({ networks: networks }) + '\n';
} catch {
  writeAll(2, 'error: invalid input\n');
  process.exit(2);
}
writeAll(1, output);

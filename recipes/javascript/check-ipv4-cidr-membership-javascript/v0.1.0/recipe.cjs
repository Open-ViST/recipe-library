'use strict';

const fs = require('node:fs');
const { TextDecoder } = require('node:util');

function invalid() {
  throw new Error('invalid input');
}

function parseIPv4(text) {
  const parts = text.split('.');
  if (parts.length !== 4) invalid();
  const octets = parts.map((part) => {
    if (!/^(0|[1-9][0-9]{0,2})$/.test(part)) invalid();
    const value = Number(part);
    if (value > 255) invalid();
    return value;
  });
  return octets[0] * 16777216 + octets[1] * 65536 + octets[2] * 256 + octets[3];
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

  const decoder = new TextDecoder('utf-8', {
    fatal: true,
    ignoreBOM: true
  });
  const text = decoder.decode(buffer.subarray(0, length));
  if (text.startsWith('\uFEFF')) invalid();
  if (/[^0-9.\/ \n]/.test(text)) invalid();

  const checks = [];
  for (const line of text.split('\n')) {
    if (line === '') continue;
    if (checks.length >= 100) invalid();

    const match = /^([0-9]+(?:\.[0-9]+){3}) ([0-9]+(?:\.[0-9]+){3})\/([0-9]+)$/.exec(line);
    if (match === null || match[0] !== line) invalid();

    const addressText = match[1];
    const networkText = match[2];
    const prefixText = match[3];
    const address = parseIPv4(addressText);
    const networkAddress = parseIPv4(networkText);

    if (!/^(0|[1-9][0-9]?)$/.test(prefixText)) invalid();
    const prefix = Number(prefixText);
    if (prefix > 32) invalid();

    const size = 2 ** (32 - prefix);
    const network = Math.floor(networkAddress / size) * size;
    if (networkAddress !== network) invalid();
    const last = network + size - 1;

    checks.push({
      address: addressText,
      cidr: networkText + '/' + prefixText,
      contains: address >= network && address <= last
    });
  }

  return JSON.stringify({ checks }) + '\n';
}

function main() {
  let output;
  try {
    output = readAndValidate();
  } catch {
    process.stderr.write('error: invalid input\n', () => process.exit(2));
    return;
  }
  process.stdout.write(output);
}

main();

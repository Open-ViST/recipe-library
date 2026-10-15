'use strict';
const test = require('node:test');
const assert = require('node:assert/strict');
const core = require('../assets/tools-core.js');
const json = (input, compact = false) => core.run({tool:'json-validator', input, compact});
const compare = (input, second, key = 'id') => JSON.parse(core.run({tool:'csv-comparator', input, second, key}).text);
const duplicate = (input, kind = 'csv', key = 'id', field = 'value') => JSON.parse(core.run({tool:'duplicate-finder', input, kind, key, field}).text);

test('JSON formatting preserves integers beyond IEEE precision and exponent spellings', () => {
  const raw = '{"integer":9007199254740993123456789,"exponent":1e400,"negative":-0,"decimal":1.2300}';
  assert.equal(json(raw, true).text.trim(), raw);
  assert.match(json(raw).text, /9007199254740993123456789/);
  assert.match(json(raw).text, /1\.2300/);
});
test('JSON handles nested empty structures and punctuation inside strings', () => {
  const raw = '{"a":[{},[],"{,:}\\\""],"b":true,"c":null}';
  assert.deepEqual(JSON.parse(json(raw).text), JSON.parse(raw));
});
test('JSON rejects duplicate keys at every depth, including equivalent escape spellings', () => {
  for (const raw of ['{"x":1,"x":2}', '{"a":{"x":1,"\\u0078":2}}']) assert.throws(() => json(raw), /Duplicate object key/);
});
test('JSON rejects invalid syntax and reports a position', () => {
  for (const raw of ['', '[1,]', '{"a":}', '01', '+1', 'NaN', 'Infinity', 'true false', '"a\nb"', '"\\x41"', '\uFEFF{}']) assert.throws(() => json(raw), /line \d+, column \d+/);
});
test('JSON escaped strings, Unicode and literals agree with native parsing', () => {
  const values = [null, true, false, 42, 'é e\u0301 🐱', '\n\\"', {a:[1,2,{z:'value'}]}];
  for (const value of values) assert.deepEqual(JSON.parse(json(JSON.stringify(value)).text), value);
});
test('JSON rejects excessive nesting without unbounded recursion', () => {
  assert.throws(() => json('['.repeat(102) + '0' + ']'.repeat(102)), /Nesting/);
});
test('Prototype-like object keys do not modify prototypes', () => {
  const parsed = core.json('{"__proto__":{"polluted":true},"constructor":"safe"}').data;
  assert.equal(Object.getPrototypeOf(parsed), null); assert.equal({}.polluted, undefined);
  assert.equal(parsed.__proto__.polluted, true);
});
test('CSV handles BOM, CRLF, quoted commas, escaped quotes and multiline fields', () => {
  const parsed = core.csv('\uFEFFid,value\r\n1,"hello, world"\r\n2,"line1\r\nline2"\r\n3,"a""b"\r\n');
  assert.equal(parsed.records.length, 3); assert.equal(parsed.records[0].value, 'hello, world');
  assert.equal(parsed.records[1].value, 'line1\r\nline2'); assert.equal(parsed.records[2].value, 'a"b');
});
test('CSV rejects malformed quoting, empty/duplicate headers and inconsistent rows', () => {
  for (const raw of ['', 'id,id\n1,2', ',x\n1,2', 'id,value\n1', 'id,value\n1,"x"z', 'id,value\n1,x"y', 'id,value\n1,"unterminated']) assert.throws(() => core.csv(raw));
});
test('CSV trailing newline is not an additional row; header-only data is valid', () => {
  assert.equal(core.csv('id,value\n').records.length, 0);
  assert.equal(core.csv('id,value\n1,a\n').records.length, 1);
});
test('CSV comparison independently identifies additions, removals, changes and unchanged rows', () => {
  const r = compare('id,value\n1,a\n2,b\n3,c', 'value,id\na,1\nB,2\nd,4');
  assert.equal(r.added[0].id,'4'); assert.equal(r.removed[0].id,'3');
  assert.equal(r.modified[0].id,'2'); assert.deepEqual(r.modified[0].fields,['value']); assert.equal(r.unchanged,1);
});
test('CSV comparison distinguishes a missing column from an empty cell', () => {
  const r = compare('id,value\n1,', 'id\n1'); assert.deepEqual(r.modified[0].fields,['value']);
});
test('CSV comparison rejects ambiguous or missing identifiers', () => {
  for (const raw of ['id,value\n1,a\n1,b', 'id,value\n,a', 'other,value\n1,a']) assert.throws(() => compare(raw,'id,value\n1,a'));
});
test('Duplicate detection separates repeated equal pairs from conflicting values', () => {
  const r = duplicate('id,value\na,x\na,y\nb,z\nb,z');
  assert.equal(r.repeated.length,2); assert.equal(r.conflicts.length,1);
  assert.deepEqual(r.conflicts[0].values,[{value:'x',positions:[1]},{value:'y',positions:[2]}]);
});
test('JSON duplicates preserve case, spaces, normalization and literal field names', () => {
  const r = duplicate('[{"a.b":"A","v/x":"é"},{"a.b":"A","v/x":"e\\u0301"},{"a.b":"a","v/x":"é"},{"a.b":" A","v/x":"é"}]','json','a.b','v/x');
  assert.equal(r.conflicts.length,1); assert.equal(r.repeated.length,1); assert.equal(r.conflicts[0].values.length,2);
});
test('JSON duplicate detection rejects arrays, non-objects and selected non-string values', () => {
  for (const raw of ['{}','[null]','[[]]','[{"id":1,"value":"x"}]','[{"id":"a","value":false}]','[{"id":"a"}]']) assert.throws(() => duplicate(raw,'json'));
});
test('CSV maximum row and column bounds are enforced', () => {
  assert.equal(core.csv('id\n' + Array(20000).fill('x').join('\n')).records.length,20000);
  assert.throws(() => core.csv('id\n' + Array(20001).fill('x').join('\n')), /20,000/);
  assert.throws(() => core.csv(Array.from({length:101},(_,i) => 'c'+i).join(',')), /100 columns/);
});
test('Byte limit counts UTF-8 bytes rather than UTF-16 characters', () => {
  const fitting = '"' + 'a'.repeat(core.MAX_BYTES - 2) + '"'; assert.ok(json(fitting,true).text.length);
  assert.throws(() => json('"' + 'é'.repeat(core.MAX_BYTES / 2) + '"'), /2 MiB/);
});
test('Unknown tool fails without running supplied input as code', () => {
  assert.throws(() => core.run({tool:'eval',input:'throw new Error()'}),/Unknown tool/);
});

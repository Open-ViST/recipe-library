/* OpenViST Tools — MIT. Deterministic local processing; no network APIs. */
(function (root) {
  'use strict';
  const MAX_BYTES = 2 * 1024 * 1024, MAX_ROWS = 20000, MAX_COLUMNS = 100;
  function fail(message) { throw new Error(message); }
  function bounded(text) {
    if (typeof text !== 'string' || new TextEncoder().encode(text).length > MAX_BYTES) fail('Each input must be at most 2 MiB.');
    return text;
  }
  function json(text, numericToken) {
    bounded(text);
    let i = 0, nodes = 0;
    const tokens = [];
    function error(message) {
      const lines = text.slice(0, i).split('\n');
      fail(message + ' at line ' + lines.length + ', column ' + (lines[lines.length - 1].length + 1) + '.');
    }
    function space() { while (i < text.length && /[\x20\t\r\n]/.test(text[i])) i++; }
    function token(raw) { tokens.push(raw); }
    function string() {
      const start = i++;
      while (i < text.length) {
        const c = text[i++];
        if (c === '\\') { i++; continue; }
        if (c === '"') {
          const raw = text.slice(start, i);
          try { const value = JSON.parse(raw); token(raw); return value; }
          catch (_) { error('Invalid JSON string'); }
        }
      }
      error('Unterminated JSON string');
    }
    function value(depth) {
      if (depth > 100) error('Nesting exceeds 100 levels');
      if (++nodes > 100000) error('JSON exceeds 100,000 values');
      space();
      const c = text[i];
      if (c === '"') return string();
      if (c === '{' || c === '[') {
        const object = c === '{', end = object ? '}' : ']';
        const result = object ? Object.create(null) : [], keys = new Set();
        token(c); i++; space();
        if (text[i] === end) { token(end); i++; return result; }
        while (i < text.length) {
          let key;
          if (object) {
            if (text[i] !== '"') error('Expected an object key');
            key = string();
            if (keys.has(key)) error('Duplicate object key');
            keys.add(key); space();
            if (text[i] !== ':') error('Expected a colon');
            token(':'); i++;
          }
          const child = value(depth + 1);
          if (object) result[key] = child; else result.push(child);
          space();
          if (text[i] === end) { token(end); i++; return result; }
          if (text[i] !== ',') error('Expected a comma or closing bracket');
          token(','); i++; space();
        }
        error('Unterminated array or object');
      }
      const rest = text.slice(i);
      const found = /^(?:true|false|null|-?(?:0|[1-9][0-9]*)(?:\.[0-9]+)?(?:[eE][+-]?[0-9]+)?)/.exec(rest);
      if (!found) error('Expected a JSON value');
      const raw = found[0]; token(raw); i += raw.length;
      // Output formatting uses original tokens, preserving large numbers exactly.
      return raw === 'null' ? null : raw === 'true' ? true : raw === 'false' ? false : (numericToken ? numericToken(raw) : Number(raw));
    }
    const data = value(0); space();
    if (i !== text.length) error('Unexpected content after the JSON value');
    return {data, tokens, values: nodes};
  }
  function formatJSON(text, compact) {
    const parsed = json(text);
    if (compact) return {text: parsed.tokens.join('') + '\n', summary: 'Valid JSON. Minified without changing numeric tokens.'};
    let depth = 0, output = '';
    const tokens = parsed.tokens;
    const line = () => '\n' + '  '.repeat(depth);
    tokens.forEach((t, index) => {
      if (t === '{' || t === '[') { output += t; depth++; if (tokens[index + 1] !== '}' && tokens[index + 1] !== ']') output += line(); }
      else if (t === '}' || t === ']') { depth--; if (tokens[index - 1] !== '{' && tokens[index - 1] !== '[') output += line(); output += t; }
      else if (t === ',') output += ',' + line();
      else if (t === ':') output += ': ';
      else output += t;
    });
    return {text: output + '\n', summary: 'Valid JSON. Formatted without changing numeric tokens.'};
  }
  function csv(text) {
    text = bounded(text).replace(/^\uFEFF/, '');
    const rows = []; let row = [], cell = '', quoted = false, closed = false, started = false;
    function field() { row.push(cell); cell = ''; closed = false; started = false; if (row.length > MAX_COLUMNS) fail('CSV exceeds 100 columns.'); }
    function record() { field(); rows.push(row); row = []; if (rows.length > MAX_ROWS + 1) fail('CSV exceeds 20,000 data rows.'); }
    for (let i = 0; i < text.length; i++) {
      const c = text[i];
      if (quoted) {
        if (c === '"') { if (text[i + 1] === '"') { cell += '"'; i++; } else { quoted = false; closed = true; } }
        else cell += c;
        continue;
      }
      if (c === ',') { field(); continue; }
      if (c === '\n' || c === '\r') { if (c === '\r' && text[i + 1] === '\n') i++; record(); continue; }
      if (closed) fail('Unexpected text after a closing CSV quote.');
      if (c === '"') { if (started) fail('Quote inside an unquoted CSV cell.'); quoted = true; started = true; }
      else { cell += c; started = true; }
    }
    if (quoted) fail('Unterminated quoted CSV cell.');
    if (row.length || started || closed || cell) record();
    if (!rows.length) fail('CSV is empty. Include a header row.');
    const headers = rows.shift();
    if (headers.some(h => !h) || new Set(headers).size !== headers.length) fail('CSV headers must be nonempty and unique.');
    const records = rows.map((r, index) => {
      if (r.length !== headers.length) fail('CSV row ' + (index + 2) + ' has a different number of columns.');
      const result = Object.create(null); headers.forEach((h, n) => { result[h] = r[n]; }); return result;
    });
    return {headers, records};
  }
  function identifier(records, key) {
    if (!key) fail('Provide an identifier column.');
    const map = new Map();
    records.forEach((record, index) => {
      if (!Object.hasOwn(record, key) || typeof record[key] !== 'string' || !record[key]) fail('Every identifier must be a nonempty string.');
      if (map.has(record[key])) fail('Duplicate identifiers found. Use Duplicate & Conflict Finder first.');
      map.set(record[key], {record, position: index + 1});
    });
    return map;
  }
  function compare(before, after, key) {
    const a = csv(before), b = csv(after);
    if (!a.headers.includes(key) || !b.headers.includes(key)) fail('The identifier column must exist in both files.');
    const left = identifier(a.records, key), right = identifier(b.records, key);
    const added = [], removed = [], modified = [], headers = Array.from(new Set([...a.headers, ...b.headers])); let unchanged = 0;
    for (const [id, entry] of left) {
      if (!right.has(id)) { removed.push(entry.record); continue; }
      const next = right.get(id).record;
      const changed = headers.filter(h => Object.hasOwn(entry.record, h) !== Object.hasOwn(next, h) || entry.record[h] !== next[h]);
      if (changed.length) modified.push({id, fields: changed, before: entry.record, after: next}); else unchanged++;
    }
    for (const [id, entry] of right) if (!left.has(id)) added.push(entry.record);
    const result = {identifier: key, added, removed, modified, unchanged};
    return {text: JSON.stringify(result, null, 2) + '\n', summary: added.length + ' added · ' + removed.length + ' removed · ' + modified.length + ' modified · ' + unchanged + ' unchanged.'};
  }
  function duplicates(text, kind, key, field) {
    let records;
    if (kind === 'csv') {
      const input = csv(text);
      if (!input.headers.includes(key) || !input.headers.includes(field)) fail('Both selected columns must exist.');
      records = input.records;
    } else {
      records = json(text).data;
      if (!Array.isArray(records) || records.length > MAX_ROWS) fail('JSON must be an array of at most 20,000 objects.');
    }
    if (!key || !field || key === field) fail('Choose two different, nonempty field names.');
    const groups = new Map();
    records.forEach((r, index) => {
      if (!r || typeof r !== 'object' || Array.isArray(r)) fail('Every record must be an object.');
      if (!Object.hasOwn(r, key) || !Object.hasOwn(r, field) || typeof r[key] !== 'string' || typeof r[field] !== 'string' || !r[key] || !r[field]) fail('Selected fields must contain nonempty strings in every record.');
      if (!groups.has(r[key])) groups.set(r[key], {positions: [], values: new Map()});
      const group = groups.get(r[key]); group.positions.push(index + 1);
      if (!group.values.has(r[field])) group.values.set(r[field], []);
      group.values.get(r[field]).push(index + 1);
    });
    const repeated = [], conflicts = [];
    for (const [id, group] of groups) {
      if (group.positions.length > 1) repeated.push({id, positions: group.positions});
      if (group.values.size > 1) conflicts.push({id, values: Array.from(group.values, ([value, positions]) => ({value, positions}))});
    }
    return {text: JSON.stringify({records: records.length, repeated, conflicts}, null, 2) + '\n', summary: repeated.length + ' repeated identifiers · ' + conflicts.length + ' conflicting identifiers.'};
  }
  function run(task) {
    let result;
    if (task.tool === 'json-validator') result = formatJSON(task.input, task.compact === true);
    else if (task.tool === 'csv-comparator') result = compare(task.input, task.second, task.key);
    else if (task.tool === 'duplicate-finder') result = duplicates(task.input, task.kind, task.key, task.field);
    else fail('Unknown tool.');
    if (new TextEncoder().encode(result.text).length > 5 * 1024 * 1024) fail('Result exceeds 5 MiB. Use a smaller input.');
    return result;
  }
  const api = {run, json, csv, MAX_BYTES};
  if (typeof module === 'object' && module.exports) module.exports = api;
  else root.OpenViSTTools = api;
})(typeof self === 'object' ? self : globalThis);

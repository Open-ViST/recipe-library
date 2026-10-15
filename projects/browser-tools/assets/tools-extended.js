/* OpenViST Tools — MIT. Local text, conversion and sitemap checks. */
(function (root) {
  'use strict';
  const core = typeof module === 'object' && module.exports ? require('./tools-core.js') : root.OpenViSTTools;
  const previousRun = core.run;
  const fail = message => { throw new Error(message); };
  function bounded(text) {
    if (typeof text !== 'string' || new TextEncoder().encode(text).length > core.MAX_BYTES) fail('Each input must be at most 2 MiB.');
    return text;
  }
  function diff(before, after) {
    bounded(before); bounded(after);
    function lines(text) { const normalized = text.replace(/\r\n?/g, '\n'); const rows = normalized ? normalized.split('\n') : []; if (normalized.endsWith('\n')) rows.pop(); return rows; }
    const a = lines(before), b = lines(after), n = a.length, m = b.length;
    if (n > 2000 || m > 2000) fail('Text Diff accepts at most 2,000 lines per input.');
    const table = new Uint16Array((n + 1) * (m + 1)), width = m + 1;
    for (let i = n - 1; i >= 0; i--) for (let j = m - 1; j >= 0; j--) table[i * width + j] = a[i] === b[j] ? table[(i + 1) * width + j + 1] + 1 : Math.max(table[(i + 1) * width + j], table[i * width + j + 1]);
    let i = 0, j = 0, added = 0, removed = 0, same = 0;
    const output = ['OpenViST line comparison', 'Line endings are compared as LF. This report is not a patch file.',
      'Final newline — before: ' + /[\r\n]$/.test(before) + '; after: ' + /[\r\n]$/.test(after),
      'Legend: - removed, + added, = unchanged; [before:after] line positions', ''];
    while (i < n || j < m) {
      if (i < n && j < m && a[i] === b[j]) { output.push('= [' + (i + 1) + ':' + (j + 1) + '] ' + a[i]); i++; j++; same++; }
      else if (i < n && (j === m || table[(i + 1) * width + j] >= table[i * width + j + 1])) { output.push('- [' + (i + 1) + ':-] ' + a[i++]); removed++; }
      else { output.push('+ [-:' + (j + 1) + '] ' + b[j++]); added++; }
    }
    return {text: output.join('\n') + '\n', extension:'txt', mime:'text/plain;charset=utf-8',
      summary: added + ' added · ' + removed + ' removed · ' + same + ' unchanged lines.'};
  }
  class NumberToken { constructor(raw) { this.raw = raw; } }
  function columns(option, defaults) {
    if (!option || !option.trim()) return defaults;
    const value = core.json(option).data;
    if (!Array.isArray(value) || !value.length || value.length > 100 || value.some(x => typeof x !== 'string' || !x) || new Set(value).size !== value.length) fail('Columns must be a JSON array of 1–100 unique nonempty names.');
    return value;
  }
  function convert(input, direction, selected, spreadsheetSafe) {
    if (direction === 'csv-json') {
      const source = core.csv(input), headers = columns(selected, source.headers);
      if (headers.some(h => !source.headers.includes(h))) fail('A selected column is missing from the CSV header.');
      const rows = source.records.map(r => { const row = Object.create(null); headers.forEach(h => { row[h] = r[h]; }); return row; });
      return {text: JSON.stringify(rows, null, 2) + '\n', summary: rows.length + ' CSV records converted to JSON. All values remain strings.'};
    }
    if (direction !== 'json-csv') fail('Choose a supported conversion direction.');
    const rows = core.json(input, raw => new NumberToken(raw)).data;
    if (!Array.isArray(rows) || rows.length > 20000 || rows.some(r => !r || typeof r !== 'object' || Array.isArray(r) || r instanceof NumberToken)) fail('JSON must be an array of at most 20,000 objects.');
    const defaults = Array.from(new Set(rows.flatMap(r => Object.keys(r))));
    const headers = columns(selected, defaults);
    if (!headers.length || headers.length > 100 || headers.some(h => !h)) fail('Choose 1–100 nonempty column names. Empty arrays require an explicit column selection.');
    function cell(value) {
      let text;
      if (value instanceof NumberToken) text = value.raw;
      else if (value === undefined || value === null) text = '';
      else if (typeof value === 'string') text = spreadsheetSafe && /^[\s]*[=+\-@]/u.test(value) ? "'" + value : value;
      else if (typeof value === 'boolean') text = String(value);
      else fail('Selected JSON fields must be strings, numbers, booleans or null; nested data is not supported.');
      return /[",\r\n]/.test(text) ? '"' + text.replace(/"/g, '""') + '"' : text;
    }
    const output = [headers.map(cell).join(',')];
    for (const row of rows) output.push(headers.map(h => cell(Object.hasOwn(row,h) ? row[h] : undefined)).join(','));
    return {text: output.join('\r\n') + '\r\n', extension:'csv', mime:'text/csv;charset=utf-8',
      summary: rows.length + ' JSON records converted to CSV. Missing fields and null become empty cells.' + (spreadsheetSafe ? ' Formula-like text is prefixed with an apostrophe.' : ' Spreadsheet formula protection is off.')};
  }
  function validDate(value) {
    const match = /^(\d{4})-(\d{2})-(\d{2})(?:T(\d{2}):(\d{2}):(\d{2})(?:\.\d+)?(Z|[+-]\d{2}:\d{2}))?$/.exec(value);
    if (!match) return false;
    const year = +match[1], month = +match[2], day = +match[3];
    const leap = year % 4 === 0 && (year % 100 !== 0 || year % 400 === 0);
    if (!year || month < 1 || month > 12 || day < 1 || day > [31,leap?29:28,31,30,31,30,31,31,30,31,30,31][month - 1]) return false;
    if (match[4] && (+match[4] > 23 || +match[5] > 59 || +match[6] > 59)) return false;
    const zone = match[7];
    return !zone || zone === 'Z' || (+zone.slice(1,3) <= 23 && +zone.slice(4) <= 59);
  }
  function sitemap(input, parsed) {
    bounded(input);
    if (!parsed || !['urlset','sitemapindex'].includes(parsed.kind) || !Array.isArray(parsed.entries)) fail('The local XML parser did not provide a sitemap.');
    if (parsed.entries.length > 20000) fail('Sitemap Inspector accepts at most 20,000 entries.');
    const issues = (parsed.issues || []).slice(), entries = [], groups = new Map(), hosts = new Set();
    for (const [i, entry] of parsed.entries.entries()) {
      const position = i + 1, issue = code => issues.push({position, code});
      if (entry.locations.length !== 1) issue('expected_one_loc');
      const raw = entry.locations[0] || '', url = raw.trim();
      if (url !== raw) issue('loc_surrounding_whitespace');
      let canonical;
      try {
        const value = new URL(url);
        if (!/^https?:\/\//i.test(url) || /%(?![0-9a-f]{2})/i.test(url) || !['http:','https:'].includes(value.protocol) || value.username || value.password || /[\x00-\x20]/.test(url) || url.length >= 2048) throw new Error();
        if (value.hash) issue('loc_contains_fragment');
        canonical = value.href; hosts.add(value.host);
      } catch (_) { issue('invalid_http_url'); }
      if (canonical) {
        if (!groups.has(canonical)) groups.set(canonical, []);
        groups.get(canonical).push(position);
      }
      if (entry.lastmods.length > 1) issue('multiple_lastmod');
      for (const date of entry.lastmods) if (!validDate(date)) issue('invalid_lastmod');
      if (entry.priorities.length > 1) issue('multiple_priority');
      for (const value of entry.priorities) if (!/^(?:0|0?\.\d+|1(?:\.0+)?)$/.test(value) || +value > 1) issue('invalid_priority');
      if (entry.frequencies.length > 1) issue('multiple_changefreq');
      for (const value of entry.frequencies) if (!['always','hourly','daily','weekly','monthly','yearly','never'].includes(value)) issue('invalid_changefreq');
      entries.push({position, url, lastmod: entry.lastmods[0] || null});
    }
    if (hosts.size > 1) issues.push({code:'multiple_hosts', note:'Check sitemap hosting and ownership requirements.'});
    const duplicates = Array.from(groups, ([url, positions]) => ({url, positions})).filter(g => g.positions.length > 1);
    const report = {kind:parsed.kind, total_entries:entries.length, unique_http_urls:groups.size, duplicate_urls:duplicates, issues, entries,
      scope:'Local structural checks only. No URLs were requested; this is not complete XSD validation or an indexing guarantee.'};
    return {text: JSON.stringify(report, null, 2) + '\n', summary: entries.length + ' entries · ' + duplicates.length + ' repeated URLs · ' + issues.length + ' issues. No network checks performed.'};
  }
  core.run = function (task) {
    let result;
    if (task.tool === 'text-diff') result = diff(task.input, task.second);
    else if (task.tool === 'csv-json-converter') result = convert(task.input, task.direction, task.columns, task.spreadsheetSafe !== false);
    else if (task.tool === 'sitemap-inspector') result = sitemap(task.input, task.sitemap);
    else return previousRun(task);
    if (new TextEncoder().encode(result.text).length > 5 * 1024 * 1024) fail('Result exceeds 5 MiB. Use a smaller input.');
    return result;
  };
  if (typeof module === 'object' && module.exports) module.exports = core;
})(typeof self === 'object' ? self : globalThis);

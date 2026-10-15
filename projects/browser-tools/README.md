# OpenViST Tools 0.1.0

A WordPress plugin providing three free, browser-local data tools:

- `/tools/json-validator/`: JSON validation, formatting and minification.
- `/tools/csv-comparator/`: CSV comparison by a unique string identifier.
- `/tools/duplicate-finder/`: repeated identifiers and conflicting string values.

The landing page is `/tools/`. Install and activate this plugin from its ZIP.
OpenViST Home 0.3.12 adds the Tools navigation integration; older Home versions
still permit direct access to the tool URLs. No VPS service, REST processing
endpoint, OpenAI call, paid dependency or user account is required.

## Processing and privacy

The local worker reads pasted text or UTF-8 files. Its processing code does not
send input to a server, execute it, use localStorage or persist it between page
loads. File selection alone does not run the tool. Results can be copied or
downloaded as JSON. Clipboard failure falls back to manual selection. The UI
has no native HTML form submission, including when JavaScript is unavailable.
Other site plugins and consented analytics are independent of this guarantee;
operators should not configure analytics to capture text or file inputs.

Limits: 2 MiB per input (UTF-8 bytes), 20,000 CSV data records, 100 columns,
100 JSON nesting levels, 100,000 JSON values, 5 MiB serialized output and a
20-second worker timeout. Browser textarea editing can normalize line endings;
an unedited uploaded file retains its original line endings for processing.
CSV uses commas with double-quoted cells and doubled quote escapes. CSV may
start with a UTF-8 BOM; JSON may not. Empty and duplicate headers are rejected.
Blank data records are validated rather than silently ignored. Comparisons are
case-sensitive, preserve whitespace and do not normalize Unicode.

JSON formatting uses validated original tokens rather than JSON.stringify on
parsed numeric values, so very large integers, exponent spellings and negative
zero survive formatting. Duplicate object keys are rejected at every depth.
Conflict detection considers selected string fields only; other JSON field
types are ignored. Field names are literal, not nested paths. Report positions
are one-based data record positions, excluding the CSV header.

Inputs are text data only. No spreadsheet formulas are evaluated, and downloads
are JSON rather than spreadsheet-active CSV. Results can contain sensitive
values: review them before sharing. Browser extensions and site compromises
are outside the plugin's local-processing guarantee.

## WordPress integration

WordPress 6.5+, PHP 8.0+. Activation registers four virtual routes and refreshes
rewrite rules. The plugin creates no posts, Tools-owned options, cron events or database
tables, and does not alter recipe or listing publication schedules. Tools URLs
are added to the native WordPress sitemap provider. Page titles, descriptions
and canonical metadata are provided for these routes; the OpenViST Directory
UI's generic metadata is suppressed only on Tools pages. Existing theme header
and footer templates are retained. The navigation filter adds Tools after
Recipes when OpenViST Home 0.3.12 is active.

If `/tools/` returns 404 after activation, save **Settings → Permalinks** once
without changing its values. Custom sitemap plugins may require separate
integration; native provider support does not guarantee third-party sitemap
integration. Browser worker/CSP/optimizer compatibility and live responsive
layout must be verified on the installed site. JavaScript-disabled browsers
show explanatory text and cannot process inputs.

## Development and validation

```bash
node --test tests/core.test.js
node --check assets/tools-core.js
node --check assets/tools-ui.js
node --check assets/tools-worker.js
```

Nineteen independent core tests cover strict JSON grammar, duplicate keys,
precision-preserving formatting, Unicode, prototype-like keys, CSV dialect,
comparison outcomes, conflicts and input bounds. The workers and UI have
separate responsibilities; these tests do not establish browser integration
or WordPress compatibility by themselves.

The plugin PHP integration is GPL-2.0-or-later (`LICENSE`). The independent
JavaScript processing engine is MIT (`LICENSE-CORE-MIT.txt`).

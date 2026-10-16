# OpenViST Tools 0.3.0

A WordPress plugin providing nine free, browser-local data tools:

- `/tools/base64/`: strict Base64 and unpadded Base64url encoding/decoding; UTF-8 or binary output.
- `/tools/url-encoder/`: URL component encoding/decoding and ordered query inspection.
- `/tools/sha256-checksum/`: SHA-256 for UTF-8 text or exact file bytes, with optional comparison.
- `/tools/json-validator/`: JSON validation, formatting and minification.
- `/tools/csv-comparator/`: CSV comparison by a unique string identifier.
- `/tools/duplicate-finder/`: repeated identifiers and conflicting string values.
- `/tools/text-diff/`: bounded line-by-line text comparison.
- `/tools/csv-json-converter/`: conversion with optional column selection.
- `/tools/sitemap-inspector/`: local sitemap XML structural checks.

The landing page is `/tools/`. Install and activate this plugin from its ZIP.
OpenViST Home 0.3.12 adds the Tools navigation integration; older Home versions
still permit direct access to the tool URLs. No VPS service, REST processing
endpoint, OpenAI call, paid dependency or user account is required.

## Processing and privacy

Browser workers process pasted text or UTF-8 files. Sitemap XML is parsed first in the main browser context with an inert native DOMParser document that is never inserted into the page. DTD and entity declarations are rejected before parsing. Its processing code does not
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

Inputs are text data only. No spreadsheet formulas are evaluated, and CSV downloads protect formula-like strings by default. Results can contain sensitive
values: review them before sharing. Browser extensions and site compromises
are outside the plugin's local-processing guarantee.

## WordPress integration

WordPress 6.5+, PHP 8.0+. Activation registers ten virtual routes and refreshes
rewrite rules. The plugin creates no posts, user-data options, cron events or database
tables. A tiny route-version option refreshes rewrite rules once when the plugin is updated. The plugin does not alter recipe or listing publication schedules. Tools URLs
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
node --test tests/core.test.js tests/extended.test.js
node --check assets/tools-core.js
node --check assets/tools-ui.js
node --check assets/tools-worker.js
```

Thirty-five independent processing tests cover strict JSON grammar, duplicate keys,
precision-preserving formatting, Unicode, prototype-like keys, CSV dialect,
comparison outcomes, conflicts and input bounds. The workers and UI have
separate responsibilities; these tests do not establish browser integration
or WordPress compatibility by themselves.

The plugin PHP integration is GPL-2.0-or-later (`LICENSE`). The independent
JavaScript processing engine is MIT (`LICENSE-CORE-MIT.txt`).

## Additional tool contracts

Text Diff accepts at most 2,000 lines per input. It uses an exact longest-common-
subsequence comparison, normalizes CRLF and CR separators to LF, preserves case
and spaces, and reports final newline presence separately. Its TXT report is
not a patch file. Repeated-line alignment is deterministic.

CSV → JSON keeps every cell as a string, including leading zeros and strings
that resemble numbers or booleans. Optional columns are entered as a JSON
array of literal names. JSON → CSV accepts flat selected scalar fields, retains
numeric token spellings, and maps absent/null fields to empty cells. It cannot
round-trip distinctions between null, missing and empty string. Nested selected
fields are rejected. CSV uses CRLF records and double-quote escaping. Formula-
like string cells and headers are prefixed with an apostrophe by default; this
is a mitigation, not a guarantee for every spreadsheet import configuration.
The protection can be disabled explicitly, and changes text values when used.

Sitemap Inspector accepts XML urlset/sitemapindex roots and supports namespaced
elements. It reports unknown namespace/root fields, missing or repeated loc,
malformed absolute HTTP(S) URLs, credentials, fragments, duplicates, selected
lastmod formats, priorities and changefreq values. Duplicate grouping uses the
browser's URL serialization; it does not sort query parameters or equate
different path spellings. Dates support YYYY-MM-DD and timezone-bearing
YYYY-MM-DDTHH:mm:ss(.fraction)Z/±HH:mm; leap seconds and abbreviated dates are
outside this initial subset. Extension namespaces are not validated. XML is
limited to 100,000 elements and 20,000 entries. This is not full XSD validation,
a sitemap-hosting-policy check, a network checker or an indexing guarantee.
No remote sitemap indexes, listed URLs, images or external entities are fetched.
Gzip files are not accepted.

The browser integration suite renders the PHP templates against a minimal
WordPress contract harness and tests all nine tools at desktop/mobile widths.
It checks native XML parsing, worker messages, examples, file input, downloads,
clipboard copy, clearing, overflow and related-button hover states. Tests use
local fixture pages and no private data; they do not replace live checks with
WordPress, the theme and SiteGround optimization enabled.

## Encoding and checksum details

All three utilities run in the same bounded browser worker. SHA-256 uses Web Crypto
and requires HTTPS (localhost also works for development). No URL entered in the
URL tool is fetched. Query inspection supports at most 20,000 parameters and
preserves repeated names and order; `+` is a space in queries, but remains a plus
in component decoding. Malformed escapes and UTF-8 are errors.

Base64 defaults to strict standard padded input; the optional Base64url alphabet
is unpadded. Whitespace and nonzero unused padding bits are rejected. Select
binary output when decoded bytes are not UTF-8; the download is an inert `.bin`
file, never an embedded preview. Base64 is not encryption.

The 2 MiB bound applies to each selected file or pasted input. An encoded output
can be larger than its original file and exceed the decoder's input bound.
Select files for byte-exact hashing: pasted text uses UTF-8 and textarea editing
can normalize line endings. Expected hashes accept 64 hex digits, case insensitive.
A matching checksum is not proof of a trustworthy source. Utility downloads use
TXT, JSON (query inspection), or BIN (binary Base64 decoding), without any upload.

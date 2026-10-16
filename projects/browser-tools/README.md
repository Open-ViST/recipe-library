# OpenViST Tools 0.5.0

A WordPress plugin providing twelve free, browser-local data tools:

- `/tools/regex-tester/`: JavaScript worker regex matching, highlighted spans and capture reports.
- `/tools/code-to-image/`: local Canvas PNG export of short plain-text code examples.
- `/tools/json-compare/`: structural JSON comparison with exact numeric tokens and JSON Pointer paths.
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
OpenViST Home 0.5.02 adds the Tools navigation integration; older Home versions
still permit direct access to the tool URLs. No VPS service, REST processing
endpoint, OpenAI call, paid dependency or user account is required.

## Processing and privacy

Browser workers process pasted data or UTF-8 files. Code to Image draws pasted text locally using Canvas. Sitemap XML is parsed first in the main browser context with an inert native DOMParser document that is never inserted into the page. DTD and entity declarations are rejected before parsing. Its processing code does not
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

WordPress 6.5+, PHP 8.0+. Activation registers thirteen virtual routes and refreshes
rewrite rules. The plugin creates no posts, user-data options, cron events or database
tables. A tiny route-version option refreshes rewrite rules once when the plugin is updated. The plugin does not alter recipe or listing publication schedules. Tools URLs
are added to the native WordPress sitemap provider. Page titles, descriptions
and canonical metadata are provided for these routes; the OpenViST Directory
UI's generic metadata is suppressed only on Tools pages. Existing theme header
and footer templates are retained. The navigation filter adds Tools after
Recipes when OpenViST Home 0.5.02 is active.

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
WordPress contract harness and tests all ten data tools and Code to Image at desktop/mobile widths.
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

## JSON Compare

Object property order is ignored, while arrays are compared by zero-based index.
Numbers are compared by exact JSON token spelling: `1`, `1.0` and `1e0` differ.
This avoids IEEE floating-point rounding, including for arbitrarily large integers
and exponents. Strings are compared after JSON decoding (escape spelling does not
matter); Unicode normalization is not performed. Missing keys differ from null.
Duplicate keys are rejected rather than silently overwritten. Limits are 2 MiB,
100 nesting levels and 100,000 values per input; at most 10,000 reported changes
and 5 MiB output. Added/removed containers are reported once as whole subtrees.
A type change is one modification. Paths follow JSON Pointer (`~0`, `~1`), and
an empty path identifies the root. `before_json` and `after_json` are JSON source
strings, preserving original numeric tokens. The report is not executable and
is not a JSON Patch. No URLs, input data or comparison results are uploaded.

## Code to Image

Canvas-only PNG export with OpenViST blue, Midnight and Paper styles; editable
window title; optional line numbers and signature; font sizes 14/16/18/20 px;
1×/2× resolution. Inputs are plain text, not executed or highlighted. No external
fonts, assets, URLs, libraries or servers are needed. Glyphs depend on installed
fonts. Tabs display as four spaces; CRLF/CR become LF. Limits: 20 KiB UTF-8,
60 lines (including trailing blanks), 140 Unicode code points per expanded line,
80 title characters, at most 1800×1800 layout px and 13 million export pixels.
Measured long lines or oversized layouts are rejected, not silently clipped.
Control characters and directional overrides/isolates are rejected. PNG blobs
above 10 MiB are rejected. Preview invalidates on edits, old object URLs are
revoked, and clearing/reloading removes results. Clipboard image support is
optional; denied clipboard access directs users to Download PNG. Review secrets
before sharing. Input stays local; analytics should never collect input fields.

## Regex Tester and grouped catalogue

The index groups tools into JSON & structured data, Text & code, Encoding &
checksums, and Website checks. Link Auditor Bridge 0.2.5 places its server-audit
entry in Website checks and removes obsolete tool counts (older bridge versions
remain functional but insert their entry after the first group).

Regex Tester uses JavaScript RegExp in a separate worker, terminated by the UI
after 3 seconds or when Stop search is clicked. Editing input also terminates
processing and invalidates old results. No partial report is shown on timeout.
There is no automatic per-keystroke regex execution. Limits: 256 KiB UTF-8 text,
4 KiB pattern, flags g/i/m/s/u/y without duplicates, 1,000 matches, 200 capture
groups and 5 MiB output. Patterns are entered without slash delimiters. Empty
matches explicitly advance by one code point with u, or one UTF-16 unit without
u. Reports use zero-based UTF-16 indices and exclusive ends; unmatched groups
are null. Without g only the first match is returned; y uses sticky semantics.
Highlights are built from text nodes, never HTML. Zero-length matches display a
vertical marker. Results depend on browser support and do not establish
compatibility with Python, PHP, Rust or a different JavaScript engine/version.
Browser tests exercise a pathological regex, timeout, manual cancellation,
subsequent recovery, literal HTML handling and desktop/mobile examples.

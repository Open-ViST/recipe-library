# OpenViST Link Auditor

Find missing HTTP links, inspect redirect chains and distinguish access restrictions
from broken pages. Python 3.11+, standard library only. **Version 0.4.1, public beta.**

[Open the website tool](https://openvist.com/tools/link-auditor/) ·
[OpenViST Tools](https://openvist.com/tools/) ·
[Browser-only utilities](../browser-tools/)

## Download and configure your own VPS

The website offers a standalone ZIP and a downloadable [installation and limits guide](SELF_HOSTING.md). No account or API key is needed for this local CLI. Use `run_audit.py --deadline 600 -- https://example.com/ --max-pages 200 --max-urls 1000 --delay 0.5 --output my-audit` to choose your workload. The hosted service quotas do not apply to your own execution. Build the exact standalone ZIP with `python3 build_self_hosted.py --output self-hosted.zip`. The ZIP contains only the MIT CLI, report viewer, deadline launcher, guide and licence.

## Two ways to use it

**Website:** sign in, add your HTTPS website origin, verify control using a small
file and request an audit. The website shows private results with filters and a
JSON download. Availability is controlled by the operator; the beta may be paused.

**CLI:** download this folder and run a bounded audit on a site you are authorized
to check. No account, package installation, paid API or AI service is required:

```bash
python3 link_auditor.py https://example.com/ --max-pages 20 --output first-audit
python3 link_auditor.py https://example.com/ --sitemap /sitemap.xml --max-pages 50 --output sitemap-audit
```

Open `first-audit.html` or process `first-audit.json`. Existing output prefixes
are refused before making requests. The offline HTML viewer has summary cards,
local search, outcome filters, expandable discovery sources and redirect chains.
It uses no external assets or network calls and works without JavaScript except
for filtering. Untrusted report values are escaped; the static script uses a CSP hash.

## What it checks

- Server-rendered HTML anchors, relative URLs and redirects.
- Missing responses (404/410), restricted access (401/403), rate limits (429),
  server errors, transport failures and unchecked URLs as distinct outcomes.
- XML sitemap URL sets and indexes, up to ten documents, via CLI `--sitemap`.
- `robots.txt` permissions using an identifiable user agent. Missing robots
  (404/410) permits requests; other robots retrieval failures stop that origin.

It does not execute JavaScript, authenticate to audited sites, submit forms,
validate fragment targets, inspect images/CSS, implement full sitemap XSD
validation or guarantee Google indexing. HTTP 200 is not proof of correct page
content and can include soft 404s. It is not a complete SEO or security audit.

## Website verification and quotas

1. Sign in with an OpenViST account.
2. Add an exact HTTPS origin, e.g. `https://example.com/`. ASCII/punycode hostnames
   are accepted; IP addresses, paths, ports, credentials and queries are refused.
3. Download the provided text file and publish it at
   `https://example.com/.well-known/openvist-audit.txt` without a redirect.
4. Request verification, then request an audit after it passes. Keep the file
   available: the proof is rechecked before every audit. Subdomains require
   separate verification. OpenViST administrators can prove their own OpenViST
   origin using their existing administrative control.

Website limits: **50 URL checks, 200 discovered URLs and 120 seconds per audit**,
plus a separate 15-second ownership-proof process deadline. Three audits and
three verification attempts per account per rolling 24 hours, three active
websites, and 15 minutes between audits of a website. Global capacity is 30 audits
and 50 verification jobs per rolling 24 hours, ten pending jobs and one running
job. These are service limits, not guarantees that every URL will be checked.
External links are not requested in the website tool. Redirects away from the
verified origin are recorded but not followed. Robots and redirect requests
are additional to the URL-check count.

Jobs/results expire after 24 hours. Unverified domain challenges expire after
one day; verified domain records expire seven days after verification. Cleanup
runs on submissions and worker polling. Results are account-private and excluded
from page URLs, sitemaps and public exports. Downloaded copies remain on the
user's device. Reports may contain URL query parameters: review before sharing.
Removing a website erases its stored WordPress reports and cancels queued work;
an already running request may finish, but its delivered report is discarded.
Private VPS records expire after 24 hours when the worker next runs. Ordinary
hosting logs/backups are governed separately by the site's privacy policy.

## Network and process boundaries

Every destination is resolved and non-public DNS answers are rejected, including
mixed public/private answers. Connections are pinned to a validated IP while
retaining the original Host and TLS hostname verification. Ambient proxies are
not used. The proof fetch has a fixed path, exact expected content, 4 KiB bound,
no redirects, no cookies and no credentials.

The worker uses a 15-second subprocess for proof verification and a 120-second
subprocess for an audit. Child limits: 256 MiB address space, 90 CPU seconds,
8 MiB per output file, 64 descriptors and no core dumps. The user service limits
CPU to 50% and memory to 384 MiB where cgroup controllers are available. This is
resource bounding, not a container sandbox. A single file lock prevents parallel
local CLI-queue/bridge workers. The WordPress queue also enforces one active lease.

Worker traffic goes **outbound from the VPS to WordPress over HTTPS**. No inbound
VPS port or public worker endpoint is needed. Worker routes require the existing
WordPress administrator application credential; user routes require a signed-in
account and WordPress cookie/REST nonce authentication. The credential is read
from a private local config file, never logged or published, and never forwarded
across redirects. Reports are structured JSON, not server-executed HTML.

Delivery has an idempotent lease and durable private outbox. Lost delivery
responses retry the same saved result, never the audit. Interrupted audits are
not rerun automatically. Expired/cancelled results are safely discarded. Website
admission defaults to paused until a compatible worker has polled and the
administrator enables it.

## CLI bounds and exit codes

CLI defaults: 50 same-origin URL checks, 500 discovered URLs, 1 MB body per
response, at most six redirect responses, a ten-second socket timeout and at
least 250 ms between request starts. `--max-pages` and `--max-urls` accept 1..5000.
`--external` opts into checking discovered external links without crawling their
anchors. Socket timeouts in the raw CLI are not an overall wall-clock deadline;
use the worker for process deadlines. Crawl-delay directives are not implemented.
Compressed sitemap files are not supported. Query strings are preserved.

Exit 0 means recorded URLs were HTTP-successful and no limit was reached; 1 means
findings, skips or limits; 2 means invalid startup input, sitemap startup failure
or output collision. Unexpected output filesystem errors may raise exceptions.
A redirect is recorded even if its final response succeeds. 403 and 429 are not
proof of a broken link. Reports are snapshots, not future-availability guarantees.

## Tests and deployment

```bash
python3 -m unittest discover -s tests -v
node wordpress/tests/ui.test.js
php wordpress/tests/contract.php
```

Tests use deterministic network fixtures and a loopback transport fixture; they
do not audit third-party websites. CI additionally runs PHP syntax checks and
WordPress 6.8/MySQL integration tests for permissions, domain ownership, private
results, leases and retention. Test fixtures do not establish exhaustive
correctness or compatibility with every WordPress/security/cache plugin.

See [DEPLOYMENT.md](DEPLOYMENT.md) for the gated rollout and rollback. The separate
WordPress plugin is in [wordpress/](wordpress/). Existing browser Tools and Recipes
services do not need replacement. No credentials, user reports or real config
files belong in this repository.

Python CLI/worker/report code: [MIT](LICENSE). WordPress integration:
[GPL-2.0-or-later](wordpress/LICENSE). Built as part of [OpenViST](https://openvist.com/).

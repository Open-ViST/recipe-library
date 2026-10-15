# OpenViST Link Auditor Bridge 0.2.2

WordPress integration for the free, account-based Link Auditor beta. GPL-2.0-or-later.
Requires WordPress 6.5+, PHP 8.0+ and MySQL/MariaDB advisory-lock support.

The public page is `/tools/link-auditor/`. Signed-in accounts can add up to three
HTTPS domains, prove control using a fixed `.well-known/openvist-audit.txt` file,
and request bounded audits. The VPS independently verifies that file before
every audit. IPs, ports, arbitrary proof paths and redirects are not accepted.
Only OpenViST administrators can use administrative control to verify the exact
OpenViST origin. Other domains always require the file proof.

Public submissions default to paused. A recent protocol-2 worker poll is required
before an administrator can enable them under WordPress Tools → Link Auditor.
Worker routes require administrator authentication. User routes require a signed-in
account with `read`, with normal WordPress REST cookie/nonce handling. Reports and
domain records are scoped to the current account; worker routes cannot be called
by subscribers. No anonymous audit/verification requests are accepted.

Activation/update creates or migrates `<prefix>ovla_jobs` and `<prefix>ovla_domains`.
No public posts, Recipes settings or credentials are modified. Reports expire
after 24 hours; challenges after a day; verified domains seven days after
verification. Queue operations perform cleanup. Removing a domain cancels its
jobs and clears its stored reports; late results are acknowledged and discarded.

Limits: three audits and three verification jobs per account per rolling day;
15 minutes between audits of a domain; 30 global audits and 50 verification jobs
per rolling day; ten pending jobs; one running lease; 1000 stored domain records.
The worker enforces 50 checks, 200 discoveries, public-network transport, fixed
proofs, process deadlines and resource limits. Delivery is idempotent and does
not cause an audit to run again. Only structured JSON is stored; UI values are
rendered as text. The latest completed audit report and recent status entries
are returned with private no-store responses. Report HTML is not uploaded.

The public landing page has a canonical URL and its own sitemap provider, while
private results are accessible only through authenticated account-scoped APIs.
The source is at `projects/link-auditor/wordpress` in Open-ViST/recipe-library.
No user reports or credentials are included in source exports.

See the parent [README](../README.md) and [deployment guide](../DEPLOYMENT.md) for
exact processing boundaries, staged installation, account checks and rollback.

Tests: `php tests/contract.php`, `node tests/ui.test.js`; run `tests/wp-integration.php`
with WP-CLI only in the disposable `https://openvist.test` CI installation.

## Standalone download

The release ZIP bundles `downloads/openvist-link-auditor-self-hosted-0.4.1.zip` and `downloads/SELF_HOSTING.md`. These are public MIT CLI files, with no worker credentials or WordPress integration. Reproduce the download from the parent project with `python3 build_self_hosted.py --output wordpress/downloads/openvist-link-auditor-self-hosted-0.4.1.zip`, then copy `SELF_HOSTING.md` into `wordpress/downloads/`. This update preserves the existing public availability setting and does not require replacing the hosted VPS worker.

Version 0.2.2 adds accessible installation-code copying for guests and signed-in users, with honest copy-failure feedback, plus explicit OpenViST blue styling for the submit buttons to override the theme submit-button colour. Hosted limits and worker protocol are unchanged.

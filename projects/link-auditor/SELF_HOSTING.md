# Run Link Auditor on your own VPS

Version 0.4.1 · Python 3.11 or newer · standard library only · MIT licence.

The self-hosted package is an independent command-line application. It does not
need WordPress, an OpenViST account, an API key, Docker or pip packages. Audits run
on your computer/VPS and write reports there. No audit results or usage telemetry
are sent to OpenViST. Audited servers receive normal HTTP requests identifying
the auditor. Use it on websites you manage or are authorized to audit.

## Install

Download `openvist-link-auditor-self-hosted-0.4.1.zip` from the OpenViST Link
Auditor page and upload it to your VPS home directory. Confirm Python:

```bash
python3 --version
```

If Python is older than 3.11, install a supported Python release using your VPS
distribution's package manager first. Extract the ZIP and enter its directory:

```bash
mkdir -p ~/openvist-tools
python3 -m zipfile -e ~/openvist-link-auditor-self-hosted-0.4.1.zip ~/openvist-tools
cd ~/openvist-tools/openvist-link-auditor-self-hosted-0.4.1
python3 link_auditor.py --help
```

## First audit

Replace `example.com` with your authorized website. Choose a new output name for
each execution: existing files are not overwritten.

```bash
python3 run_audit.py --deadline 300 -- https://example.com/ \
  --max-pages 50 --max-urls 500 --delay 0.5 --output first-audit
```

This writes `first-audit.html` and `first-audit.json`. Download the HTML from your
VPS and open it in your browser. An exit status of 1 can mean that a configured
limit was reached, not a software failure. Unchecked URLs are listed separately.

## Change your limits

The OpenViST website's account quotas and 50-URL/120-second limits do not apply to
this local CLI. Set your own per-run bounds using arguments:

| Argument | Default | Accepted values | Meaning |
| --- | --- | --- | --- |
| `--deadline` on `run_audit.py` | 300 | 1..86400 seconds | Overall process deadline, including DNS and reads |
| `--max-pages` | 50 | 1..5000 | Same-origin URL checks |
| `--max-urls` | 500 | 1..5000 | Discovered URLs retained; set at least as high as max-pages |
| `--delay` | 0.25 | 0..60 seconds | Minimum interval between request starts |
| `--request-timeout` | 10 | 1..60 seconds | Socket timeout, not the overall deadline |
| `--byte-limit` | 1000000 | 1024..10485760 bytes | Body bytes retained per response |
| `--sitemap` | none | Same-origin path/URL | Seed URLs from a sitemap or sitemap index |
| `--external` | off | flag | Check discovered external links, without crawling their anchors |

For a larger, slower audit:

```bash
python3 run_audit.py --deadline 1800 -- https://example.com/ \
  --max-pages 1000 --max-urls 3000 --delay 1 \
  --request-timeout 15 --byte-limit 2000000 \
  --sitemap /sitemap.xml --output larger-audit
```

Increase pages, time and retained URLs to suit your VPS memory, disk capacity and
the destination's request policy. A larger URL count does not guarantee a full
crawl: robots rules, redirects, discovery and other bounds still apply. CLI
validation caps are explicitly defined by `bounded_int` and `finite_number` in
`link_auditor.py`; the MIT source can be adapted for larger authorized workloads,
but test memory and report size before increasing them. Changing the shared
OpenViST website service is separate from changing this private CLI.

## Results and limitations

- Exit **0**: recorded checks succeeded and no limit was reached.
- Exit **1**: findings, skipped checks or limits; inspect the report.
- Exit **2**: invalid startup settings, sitemap startup failure or output collision.
- Exit **124** from the launcher: deadline reached; a complete report may not exist.

The launcher limits elapsed time, not memory, CPU or disk. For unattended use,
add your own OS/service resource limits and report retention policy. The hosted
WordPress worker has its own separate process limits and verification flow.
Do not expose the CLI as an unrestricted URL-fetching web API.

The auditor checks public HTTP(S) destinations, pins validated public IPs, rejects
private-network destinations and respects robots.txt. It does not execute
JavaScript or submit forms. No external command from a crawled page is executed.
Raw CLI socket timeouts are not overall deadlines; use `run_audit.py` when you
need a deadline. Compressed sitemaps and crawl-delay directives are unsupported.

Reports may contain URL query parameters. Keep them private and review them
before sharing. HTTP 200 does not establish correct content or indexing. This is
a bounded link-checking tool, not a complete SEO or security audit.

Source, tests and deployment documentation:
https://github.com/Open-ViST/recipe-library/tree/main/projects/link-auditor

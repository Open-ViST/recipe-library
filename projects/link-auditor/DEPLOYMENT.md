# Deploy the public beta

This is an operator guide for the existing OpenViST installation. Keep public
submissions paused until all checks below pass. Use a backup before updating.
The 0.3.0 worker remains installed for rollback; do not overwrite its directory.

## 1. WordPress plugin

Install the separate `openvist-link-auditor-bridge-0.2.0.zip` as an update to the
existing Bridge plugin. It migrates the two private tables on administrator init.
The public information page is `/tools/link-auditor/`; requests and reports require
an account. Existing browser Tools and Recipes plugins are unchanged.

Under WordPress **Tools → Link Auditor**, public submissions initially remain
paused. Do not enable them yet. Updating from the private pilot rejects claims
from the old worker protocol so it cannot process an unintended domain.

## 2. VPS worker

Extract the worker release to `~/openvist/tools/openvist-link-auditor-0.4.0`:

```bash
cd ~/openvist/tools/openvist-link-auditor-0.4.0
python3 -m unittest discover -s tests -q
python3 bridge_worker.py check
```

The check must say `WORDPRESS BRIDGE PROTOCOL 2 AUTHENTICATION OK`. It neither
submits nor claims a job. The existing private config defaults to
`~/openvist/recipes/config/wordpress.json`, with `base_url`, `username` and
`application_password`; it must be mode 600 and point to `https://openvist.com`.
It is read only, never copied into a release or logged. The WordPress account
must already have administrator permission for worker routes. Do not broaden
account capabilities merely to make this check pass.

Only after the authentication check passes:

```bash
systemctl --user stop openvist-link-auditor.timer
systemctl --user stop openvist-link-auditor.service
cp deploy/openvist-link-auditor.service ~/.config/systemd/user/
systemctl --user daemon-reload
systemctl --user enable --now openvist-link-auditor.timer
systemctl --user start openvist-link-auditor.service
journalctl --user -u openvist-link-auditor.service -n 15 --no-pager
```

The 0.2.0 timer is still compatible. The new service points to 0.4.0 and has a
200-second outer timeout for claim/proof/audit/delivery. No inbound port is opened.

## 3. Administrator acceptance check

Visit `/tools/link-auditor/` with your administrator account. Add
`https://openvist.com/`; administrative control of this exact OpenViST origin
proves ownership without uploading a file. Submit one audit, wait for the worker
and refresh. Confirm `completed`, sensible results and a downloadable JSON file.
Verify that a logged-out browser sees the information/sign-in page, not reports.

Within ten minutes of a protocol-2 worker poll, enable submissions under
**WordPress Tools → Link Auditor**. Test a normal account against a second website
you control: upload its exact proof file, request verification and then audit.
The feature is a free beta; monitor the global quotas and resource use.

## Pause, rollback and records

Uncheck the WordPress availability switch to stop new non-administrator requests.
To stop all processing, also stop the user timer and service. Do not fall back to
an unverified-domain worker. For a complete rollback, restore the previous Bridge
0.1.0 plugin and the 0.3.0 service together; those versions only support the
private OpenViST administrator pilot. The migration retains previous job rows.

`~/openvist/tools/link-auditor-state/bridge-jobs` is private. The worker deletes
its own UUID-named job directories older than 24 hours on each invocation. It
never repeats interrupted audits. A 100-directory local cap stops new claims if
unexpected growth occurs. WordPress deletes expired jobs and challenges during
queue operations. Backups and hosting logs may have separate retention.

Investigate unexpected lease/authentication errors rather than resetting jobs
or weakening ownership/network checks. Queue metadata and reports must not be
added to GitHub, public uploads, Recipes exports or sitemaps.

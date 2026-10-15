"""Offline report presentation; no external assets or requests."""
from base64 import b64encode
from hashlib import sha256
from html import escape

SCRIPT = """const search=document.querySelector('#search'),filter=document.querySelector('#filter'),rows=[...document.querySelectorAll('tbody tr')],count=document.querySelector('#visible');function update(){let n=0;for(const row of rows){const match=(!filter.value||row.dataset.group===filter.value)&&row.textContent.toLowerCase().includes(search.value.toLowerCase());row.hidden=!match;if(match)n++;}count.textContent=n+' matching URLs';}search.addEventListener('input',update);filter.addEventListener('change',update);update();"""


def html_report(report):
    results = report['results']
    ok = sum(r['outcome'] == 'ok' for r in results)
    pending = sum(r['outcome'] == 'not_checked' for r in results)
    findings = len(results) - ok - pending
    redirects = sum(bool(r['redirects']) for r in results)
    rows = []
    for item in results:
        url = escape(item['url'], quote=True)
        group = 'pending' if item['outcome'] == 'not_checked' else 'ok' if item['outcome'] == 'ok' else 'findings'
        details = '<details><summary>Discovery sources (' + str(len(item['sources'])) + ')</summary><pre>' + escape('\n'.join(item['sources'])) + '</pre></details>'
        if item['redirects']:
            details += '<details><summary>Redirect chain</summary><pre>' + escape('\n'.join(str(r['status']) + ' ' + r['from'] + ' → ' + r['to'] for r in item['redirects'])) + '</pre></details>'
        if item.get('error'):
            details += '<p>' + escape(item['error']) + '</p>'
        if item.get('body_truncated'):
            details += '<p>Response body exceeded the size limit; discovery is partial.</p>'
        rows.append('<tr data-group="' + group + '"><td><a rel="noreferrer" href="' + url + '">' + url + '</a>' + details + '</td><td>' + escape(str(item['status'] or '—')) + '</td><td>' + escape(item['outcome']) + '</td><td>' + str(len(item['redirects'])) + '</td></tr>')
    digest = b64encode(sha256(SCRIPT.encode()).digest()).decode()
    cards = ''.join('<div class="card"><strong>' + str(value) + '</strong><span>' + label + '</span></div>' for value, label in [(ok, 'HTTP successful'), (findings, 'Other outcomes'), (pending, 'Not checked'), (redirects, 'URLs with redirects')])
    return '''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'; script-src 'sha256-''' + digest + ''''; base-uri 'none'; form-action 'none'">
<title>OpenViST Link Audit</title><style>
*{box-sizing:border-box}body{font:16px/1.6 system-ui;margin:0;background:#f7f9fb;color:#171d21}main{max-width:1200px;margin:auto;padding:32px 20px}h1,a{color:#2563eb}h1{margin-bottom:8px}a,pre{overflow-wrap:anywhere}pre{white-space:pre-wrap;font:inherit}.cards{display:grid;grid-template-columns:repeat(4,1fr);gap:16px;margin:24px 0}.card{background:white;border:1px solid #d9dddf;border-top:3px solid #93c5fd;border-radius:14px;padding:20px}.card strong{display:block;font-size:32px;color:#2563eb}.card span{font-size:14px}.notice{padding:16px;background:#eff6ff;border-radius:12px}.controls{display:flex;gap:16px;flex-wrap:wrap;margin:24px 0}label{display:flex;flex-direction:column;gap:4px}input,select{font:inherit;min-height:44px;border:1px solid #cbd5e1;border-radius:8px;padding:8px;background:white}input:focus,select:focus{outline:2px solid #2563eb}.scroll{overflow:auto;background:white;border-radius:12px}table{border-collapse:collapse;width:100%}th,td{padding:16px;border-bottom:1px solid #d9dddf;text-align:left;vertical-align:top}th{background:#eff6ff}td:first-child{min-width:220px;max-width:700px}summary{cursor:pointer;color:#475569;font-size:14px;margin-top:8px}tr:hover{background:#eff6ff}[hidden]{display:none!important}@media(max-width:650px){.cards{grid-template-columns:repeat(2,1fr)}main{padding:20px 12px}.controls label{width:100%}}@media print{.controls{display:none}tr[hidden]{display:table-row!important}}
</style></head><body><main><p>OPENVIST · LINK AUDITOR</p><h1>Link audit report</h1><p>''' + escape(report['started_from']) + '</p><p>Generated: ' + escape(report['generated_at']) + '</p><div class="cards">' + cards + '</div><p class="notice">' + ('Partial audit: a configured limit was reached. Unchecked URLs are not failures. ' if report['limits_reached'] else '') + '''HTTP success confirms a response, not correct content or indexability. Restricted access and rate limits are separate findings, not proof of broken links. External links are checked only when explicitly enabled.</p>
<div class="controls"><label>Find a URL or outcome<input id="search" type="search" placeholder="Search this report"></label><label>Show<select id="filter"><option value="">All URLs</option><option value="findings">Other outcomes</option><option value="ok">HTTP successful</option><option value="pending">Not checked</option></select></label></div><p id="visible" aria-live="polite">''' + str(len(results)) + ' URLs</p><noscript><p>Filtering needs JavaScript; the complete table is available below.</p></noscript><div class="scroll"><table><thead><tr><th>URL and details</th><th>HTTP</th><th>Outcome</th><th>Redirects</th></tr></thead><tbody>' + ''.join(rows) + '</tbody></table></div><p>This bounded HTTP snapshot is not a complete SEO or security audit. Reports may contain private query parameters; review them before sharing.</p></main><script>' + SCRIPT + '</script></body></html>'

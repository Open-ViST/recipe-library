(function () {
  'use strict';
  const form = document.querySelector('[data-ovt-tool]');
  if (!form) return;
  const tool = form.dataset.ovtTool, input = form.querySelector('#ovt-input');
  const second = form.querySelector('#ovt-second'), output = form.querySelector('#ovt-output');
  const status = form.querySelector('[data-ovt-status]'), panel = form.querySelector('[data-ovt-result]');
  const cancel = form.querySelector('[data-ovt-stop]'), highlights=form.querySelector('[data-ovt-highlights]');
  const run = form.querySelector('[data-ovt-run]'), download = form.querySelector('[data-ovt-download]');
  let worker = null, timer = null, objectURL = null, generation = 0;
  const fileTexts = new Map(), fileReads = new Map(), fileBytes = new Map();
  function availability() { run.disabled = !!worker || typeof Worker !== 'function' || fileReads.size > 0; }
  function message(text, error) { status.textContent = text; status.classList.toggle('is-error', !!error); }
  function stop() {
    if (worker) worker.terminate(); worker = null;
    clearTimeout(timer); timer = null; if(cancel)cancel.hidden=true;
    form.removeAttribute('aria-busy'); availability();
  }
  function reset() {
    generation++; stop(); panel.hidden = true; output.value = ''; if(highlights)highlights.replaceChildren();
    if (objectURL) URL.revokeObjectURL(objectURL); objectURL = null;
    download.removeAttribute('href');
  }
  function ready(event) { fileTexts.delete(event.target.id); fileBytes.delete(event.target.id); fileReads.delete(event.target.id); reset(); message('Ready. Run the tool to process your input.'); }
  form.querySelectorAll('textarea:not([readonly]),input[type=text],input[type=checkbox],select').forEach(el => el.addEventListener('input', ready));
  form.querySelectorAll('[data-ovt-file]').forEach(file => file.addEventListener('change', async function () {
    reset(); const selected = file.files[0], target = file.dataset.ovtFile, ticket = {};
    fileReads.delete(target); fileTexts.delete(target); fileBytes.delete(target);
    if (!selected) { availability(); return; }
    if (selected.size > 2 * 1024 * 1024) { message('Each input file must be at most 2 MiB.', true); file.value = ''; availability(); return; }
    fileReads.set(target, ticket); availability();
    try {
      const bytes = await selected.arrayBuffer();
      let text;
      if (['base64','sha256-checksum'].includes(tool)) {
        if (fileReads.get(target) !== ticket) return;
        fileBytes.set(target, new Uint8Array(bytes));
        try { text = new TextDecoder('utf-8', {fatal:true,ignoreBOM:true}).decode(bytes); }
        catch (_) { text = '[Binary file selected: ' + selected.size + ' bytes. Editing this field switches to text input.]'; }
      } else text = new TextDecoder('utf-8', {fatal: true, ignoreBOM: true}).decode(bytes);
      if (fileReads.get(target) !== ticket) return;
      fileTexts.set(target, text); form.querySelector('#' + target).value = text;
      message('File loaded locally. Run the tool when ready.');
    } catch (_) { if (fileReads.get(target) === ticket) message('Unable to read the file as UTF-8 text.', true); }
    finally { if (fileReads.get(target) === ticket) fileReads.delete(target); availability(); }
  }));
  form.querySelector('[data-ovt-sample]').addEventListener('click', function () {
    fileReads.clear(); fileTexts.clear(); fileBytes.clear(); reset();
    if (['base64','url-encoder','sha256-checksum'].includes(tool)) {
      input.value = tool === 'url-encoder' ? 'Hello world & OpenViST ✓' : 'OpenViST ✓';
      if(form.querySelector('#ovt-operation'))form.querySelector('#ovt-operation').value='encode';
      if(form.querySelector('#ovt-expected'))form.querySelector('#ovt-expected').value='';
    } else if (tool === 'regex-tester') {
      input.value = 'OpenViST v0.5.0\nPython v3.14.0\nRust v1.90.0';
      form.querySelector('#ovt-pattern').value='(?<name>[A-Za-z]+) v(?<version>[0-9]+\\.[0-9]+\\.[0-9]+)';
      form.querySelector('#ovt-flags').value='g';
    } else if (tool === 'json-compare') {
      input.value = '{"project":"OpenViST","status":"draft","retired":true,"stats":{"count":9007199254740993}}';
      second.value = '{"stats":{"count":9007199254740994},"status":"published","project":"OpenViST","active":true}';
    } else if (tool === 'json-validator') input.value = '{"project":"OpenViST","versions":[1,2,3],"large_integer":9007199254740993}';
    else if (tool === 'csv-comparator') {
      input.value = 'id,name,status\n1,Alpha,active\n2,Beta,pending\n3,Gamma,active\n';
      second.value = 'id,name,status\n1,Alpha,active\n2,Beta,active\n4,Delta,new\n';
      form.querySelector('#ovt-key').value = 'id';
    } else if (tool === 'text-diff') {
      input.value = 'project=OpenViST\nstatus=draft\nkeep=this line\n'; second.value = 'project=OpenViST\nstatus=published\nkeep=this line\nnew=feature\n';
    } else if (tool === 'csv-json-converter') {
      form.querySelector('#ovt-direction').value = 'csv-json'; form.querySelector('#ovt-columns').value = ''; form.querySelector('#ovt-safe').checked = true;
      input.value = 'id,name,active\n001,Alpha,true\n002,"Beta, Inc.",false\n';
    } else if (tool === 'sitemap-inspector') {
      input.value = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n  <url><loc>https://example.com/</loc><lastmod>2026-10-15</lastmod></url>\n  <url><loc>https://example.com/about/</loc><lastmod>2026-02-31</lastmod></url>\n  <url><loc>https://example.com/</loc></url>\n</urlset>';
    } else {
      form.querySelector('#ovt-kind').value = 'csv'; form.querySelector('#ovt-key').value = 'id'; form.querySelector('#ovt-field').value = 'value';
      input.value = 'id,value\nalpha,open\nalpha,closed\nbeta,ready\nbeta,ready\n';
    }
    form.querySelectorAll('input[type=file]').forEach(el => { el.value = ''; });
    message('Example loaded. Run the tool to see the result.'); input.focus();
  });
  form.querySelector('[data-ovt-clear]').addEventListener('click', function () {
    fileReads.clear(); fileTexts.clear(); fileBytes.clear(); reset(); input.value = ''; if (second) second.value = '';
    form.querySelectorAll('input[type=file]').forEach(el => { el.value = ''; });
    message('Inputs and results cleared.'); input.focus();
  });
  run.addEventListener('click', function () {
    reset();
    if (typeof Worker !== 'function' || !window.ovtConfig) { message('Your browser cannot start local processing. No data was sent to the server.', true); return; }
    const task = {tool, pattern:form.querySelector('#ovt-pattern')?.value, flags:form.querySelector('#ovt-flags')?.value, bytes:fileBytes.get('ovt-input'), operation:form.querySelector('#ovt-operation')?.value, alphabet:form.querySelector('#ovt-alphabet')?.value, decoded:form.querySelector('#ovt-decoded')?.value, expected:form.querySelector('#ovt-expected')?.value, input: fileTexts.get('ovt-input') ?? input.value, second: second ? (fileTexts.get('ovt-second') ?? second.value) : '',
      key: form.querySelector('#ovt-key')?.value, field: form.querySelector('#ovt-field')?.value,
      kind: form.querySelector('#ovt-kind')?.value, compact: form.querySelector('#ovt-mode')?.value === 'compact',
      direction: form.querySelector('#ovt-direction')?.value, columns: form.querySelector('#ovt-columns')?.value,
      spreadsheetSafe: form.querySelector('#ovt-safe')?.checked !== false};
    const id = generation;
    try {
      if (tool === 'sitemap-inspector') {
        if (!window.OpenViSTSitemap) throw new Error('The local XML parser could not load.');
        task.sitemap = window.OpenViSTSitemap.parse(task.input);
      }
      worker = new Worker(window.ovtConfig.worker);
      run.disabled = true; if(cancel)cancel.hidden=false; form.setAttribute('aria-busy', 'true'); message('Processing locally…');
      timer = setTimeout(function () { if (generation !== id) return; stop(); message(tool==='regex-tester'?'Search stopped after 3 seconds. Simplify the pattern or shorten the text.':'Processing stopped after 20 seconds. Try a smaller input.', true); }, tool==='regex-tester'?3000:20000);
      worker.onmessage = function (event) {
        if (generation !== id) return;
        stop(); const data = event.data;
        if (!data.ok) { message(data.error || 'Unable to process this input.', true); return; }
        output.value = data.result.text; panel.hidden = false;
        if(highlights){
          let cursor=0;const fragment=document.createDocumentFragment();
          for(const match of data.result.matches||[]){
            fragment.append(document.createTextNode(task.input.slice(cursor,match.index)));
            const mark=document.createElement('mark');mark.textContent=match.text||'│';
            mark.title='Match at UTF-16 index '+match.index+(match.text===''?' (zero length)':'');
            fragment.append(mark);cursor=match.end;
          }
          fragment.append(document.createTextNode(task.input.slice(cursor)));highlights.replaceChildren(fragment);
        }
        const extension = data.result.extension || 'json';
        objectURL = URL.createObjectURL(new Blob([data.result.bytes ?? data.result.text], {type:data.result.mime || 'application/json;charset=utf-8'}));
        download.href = objectURL; download.download = 'openvist-' + tool + '.' + extension;
        download.textContent = 'Download ' + extension.toUpperCase();
        message(data.result.summary); output.focus();
      };
      worker.onerror = function () { if (generation !== id) return; stop(); message('Local worker could not run. No data was sent to the server.', true); };
      worker.postMessage(task);
    } catch (error) { stop(); message(error.message || 'Local processing could not start. No data was sent to the server.', true); }
  });
  form.querySelector('[data-ovt-copy]').addEventListener('click', async function () {
    try { await navigator.clipboard.writeText(output.value); message('Result copied.'); }
    catch (_) { output.focus(); output.select(); message('Result selected. Use your browser’s copy command.'); }
  });
  if(cancel)cancel.addEventListener('click',()=>{reset();message('Search stopped. No partial report was kept.');});
  window.addEventListener('pagehide', reset);
  run.disabled = typeof Worker !== 'function';
  if (run.disabled) message('This browser does not support the worker required for local processing.', true);
})();

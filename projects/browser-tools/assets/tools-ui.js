(function () {
  'use strict';
  const form = document.querySelector('[data-ovt-tool]');
  if (!form) return;
  const tool = form.dataset.ovtTool, input = form.querySelector('#ovt-input');
  const second = form.querySelector('#ovt-second'), output = form.querySelector('#ovt-output');
  const status = form.querySelector('[data-ovt-status]'), panel = form.querySelector('[data-ovt-result]');
  const run = form.querySelector('[data-ovt-run]'), download = form.querySelector('[data-ovt-download]');
  let worker = null, timer = null, objectURL = null, generation = 0;
  const fileTexts = new Map(), fileReads = new Map();
  function availability() { run.disabled = !!worker || typeof Worker !== 'function' || fileReads.size > 0; }
  function message(text, error) { status.textContent = text; status.classList.toggle('is-error', !!error); }
  function stop() {
    if (worker) worker.terminate(); worker = null;
    clearTimeout(timer); timer = null;
    form.removeAttribute('aria-busy'); availability();
  }
  function reset() {
    generation++; stop(); panel.hidden = true; output.value = '';
    if (objectURL) URL.revokeObjectURL(objectURL); objectURL = null;
    download.removeAttribute('href');
  }
  function ready(event) { fileTexts.delete(event.target.id); fileReads.delete(event.target.id); reset(); message('Ready. Run the tool to process your input.'); }
  form.querySelectorAll('textarea:not([readonly]),input[type=text],select').forEach(el => el.addEventListener('input', ready));
  form.querySelectorAll('[data-ovt-file]').forEach(file => file.addEventListener('change', async function () {
    reset(); const selected = file.files[0], target = file.dataset.ovtFile, ticket = {};
    fileReads.delete(target); fileTexts.delete(target);
    if (!selected) { availability(); return; }
    if (selected.size > 2 * 1024 * 1024) { message('Each input file must be at most 2 MiB.', true); file.value = ''; availability(); return; }
    fileReads.set(target, ticket); availability();
    try {
      const bytes = await selected.arrayBuffer();
      const text = new TextDecoder('utf-8', {fatal: true, ignoreBOM: true}).decode(bytes);
      if (fileReads.get(target) !== ticket) return;
      fileTexts.set(target, text); form.querySelector('#' + target).value = text;
      message('File loaded locally. Run the tool when ready.');
    } catch (_) { if (fileReads.get(target) === ticket) message('Unable to read the file as UTF-8 text.', true); }
    finally { if (fileReads.get(target) === ticket) fileReads.delete(target); availability(); }
  }));
  form.querySelector('[data-ovt-sample]').addEventListener('click', function () {
    fileReads.clear(); fileTexts.clear(); reset();
    if (tool === 'json-validator') input.value = '{"project":"OpenViST","versions":[1,2,3],"large_integer":9007199254740993}';
    else if (tool === 'csv-comparator') {
      input.value = 'id,name,status\n1,Alpha,active\n2,Beta,pending\n3,Gamma,active\n';
      second.value = 'id,name,status\n1,Alpha,active\n2,Beta,active\n4,Delta,new\n';
      form.querySelector('#ovt-key').value = 'id';
    } else {
      form.querySelector('#ovt-kind').value = 'csv'; form.querySelector('#ovt-key').value = 'id'; form.querySelector('#ovt-field').value = 'value';
      input.value = 'id,value\nalpha,open\nalpha,closed\nbeta,ready\nbeta,ready\n';
    }
    form.querySelectorAll('input[type=file]').forEach(el => { el.value = ''; });
    message('Example loaded. Run the tool to see the result.'); input.focus();
  });
  form.querySelector('[data-ovt-clear]').addEventListener('click', function () {
    fileReads.clear(); fileTexts.clear(); reset(); input.value = ''; if (second) second.value = '';
    form.querySelectorAll('input[type=file]').forEach(el => { el.value = ''; });
    message('Inputs and results cleared.'); input.focus();
  });
  run.addEventListener('click', function () {
    reset();
    if (typeof Worker !== 'function' || !window.ovtConfig) { message('Your browser cannot start local processing. No data was sent to the server.', true); return; }
    const task = {tool, input: fileTexts.get('ovt-input') ?? input.value, second: second ? (fileTexts.get('ovt-second') ?? second.value) : '',
      key: form.querySelector('#ovt-key')?.value, field: form.querySelector('#ovt-field')?.value,
      kind: form.querySelector('#ovt-kind')?.value, compact: form.querySelector('#ovt-mode')?.value === 'compact'};
    const id = generation;
    try {
      worker = new Worker(window.ovtConfig.worker);
      run.disabled = true; form.setAttribute('aria-busy', 'true'); message('Processing locally…');
      timer = setTimeout(function () { if (generation !== id) return; stop(); message('Processing stopped after 20 seconds. Try a smaller input.', true); }, 20000);
      worker.onmessage = function (event) {
        if (generation !== id) return;
        stop(); const data = event.data;
        if (!data.ok) { message(data.error || 'Unable to process this input.', true); return; }
        output.value = data.result.text; panel.hidden = false;
        objectURL = URL.createObjectURL(new Blob([data.result.text], {type:'application/json;charset=utf-8'}));
        download.href = objectURL; download.download = 'openvist-' + tool + '.json';
        message(data.result.summary); output.focus();
      };
      worker.onerror = function () { if (generation !== id) return; stop(); message('Local worker could not run. No data was sent to the server.', true); };
      worker.postMessage(task);
    } catch (_) { stop(); message('Local processing could not start. No data was sent to the server.', true); }
  });
  form.querySelector('[data-ovt-copy]').addEventListener('click', async function () {
    try { await navigator.clipboard.writeText(output.value); message('Result copied.'); }
    catch (_) { output.focus(); output.select(); message('Result selected. Use your browser’s copy command.'); }
  });
  window.addEventListener('pagehide', reset);
  run.disabled = typeof Worker !== 'function';
  if (run.disabled) message('This browser does not support the worker required for local processing.', true);
})();

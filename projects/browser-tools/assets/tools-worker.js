'use strict';
importScripts('tools-core.js' + self.location.search, 'tools-extended.js' + self.location.search, 'tools-utilities.js' + self.location.search, 'tools-json-compare.js' + self.location.search);
self.onmessage = async function (event) {
  try { const result = await (['base64','url-encoder','sha256-checksum'].includes(event.data.tool) ? self.OpenViSTUtilities.run(event.data) : self.OpenViSTTools.run(event.data)); if(new TextEncoder().encode(result.text).length>5*1024*1024)throw new Error('Output exceeds 5 MiB.'); self.postMessage({ok:true,result}); }
  catch (error) { self.postMessage({ok: false, error: error instanceof Error ? error.message : 'Unable to process this input.'}); }
};

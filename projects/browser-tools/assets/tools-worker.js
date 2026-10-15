'use strict';
importScripts('tools-core.js' + self.location.search, 'tools-extended.js' + self.location.search);
self.onmessage = function (event) {
  try { self.postMessage({ok: true, result: self.OpenViSTTools.run(event.data)}); }
  catch (error) { self.postMessage({ok: false, error: error instanceof Error ? error.message : 'Unable to process this input.'}); }
};

<?php defined('ABSPATH') || exit; ?>
<section role="form" aria-label="Code image creator" class="ovt-workbench" data-ovt-image>
 <div class="ovt-toolbar"><button type="button" data-image-sample>Load example</button><button type="button" data-image-clear>Clear all</button></div>
 <label for="ovt-image-code">Your code</label>
 <textarea id="ovt-image-code" rows="12" maxlength="20000" spellcheck="false" autocapitalize="off" autocomplete="off" aria-describedby="ovt-image-help"></textarea>
 <p id="ovt-image-help" class="ovt-help">Up to 60 lines, 140 characters per line and 20 KiB of UTF-8 text. Tabs display as four spaces. Code is drawn as plain text without syntax highlighting. It is never executed or uploaded.</p>
 <div class="ovt-options">
  <label>Window title<input id="ovt-image-title" type="text" value="example.rs" maxlength="80" autocomplete="off"></label>
  <label>Style<select id="ovt-image-theme"><option value="ocean">OpenViST blue</option><option value="midnight">Midnight</option><option value="paper">Paper</option></select></label>
  <label>Font size<select id="ovt-image-font"><option value="14">14 px</option><option value="16" selected>16 px</option><option value="18">18 px</option><option value="20">20 px</option></select></label>
  <label>Export resolution<select id="ovt-image-scale"><option value="1">1×</option><option value="2" selected>2×</option></select></label>
  <label class="ovt-checkbox"><input id="ovt-image-lines" type="checkbox" checked> Show line numbers</label>
  <label class="ovt-checkbox"><input id="ovt-image-brand" type="checkbox" checked> Show OpenViST signature</label>
 </div>
 <button type="button" class="ovt-primary" data-image-render disabled>Create image</button>
 <p class="ovt-status" data-image-status role="status" aria-live="polite">Load an example or paste your code, then create your image.</p>
 <section class="ovt-result" data-image-result hidden><h2>Image preview</h2><canvas class="ovt-image-canvas" role="img" aria-label="Preview of your code image"></canvas><div class="ovt-toolbar"><a class="ovt-download" data-image-download download="openvist-code.png">Download PNG</a><button type="button" data-image-copy hidden>Copy image</button></div><p class="ovt-help">Review your code for secrets before sharing the PNG. Font appearance and Unicode glyphs depend on your device. The preview scales to fit your screen; the download retains its export resolution.</p></section>
 <noscript><p>JavaScript and Canvas are required. Your code is not submitted to WordPress.</p></noscript>
</section>
<section class="ovt-notes"><h2>From code to a shareable image</h2><p>Choose a short example, add its filename as the title and create an image for documentation, tutorials or social posts. Any programming language is accepted as plain text. This tool does not compile, check or highlight syntax.</p><p>Rendering uses your browser's Canvas and installed fonts. Inputs are not saved to browser storage. Long lines or images exceeding the rendering limits are rejected with an explanation rather than clipped. Nothing is loaded from your code, including URLs or HTML.</p><div class="ovt-link-actions"><a class="ovt-link-button button" href="https://github.com/Open-ViST/recipe-library/tree/main/projects/browser-tools">Source code on GitHub ↗</a><a class="ovt-link-button button" href="<?php echo esc_url(home_url('/recipes/')); ?>">Browse recipes →</a></div></section>

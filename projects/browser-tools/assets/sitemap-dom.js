/* Native inert XML parsing only. The resulting document is never inserted into the page. */
(function () {
  'use strict';
  window.OpenViSTSitemap = {parse: function (text) {
    if (new TextEncoder().encode(text).length > 2 * 1024 * 1024) throw new Error('Sitemap input must be at most 2 MiB.');
    if (/<!DOCTYPE|<!ENTITY/i.test(text)) throw new Error('DTD and entity declarations are not supported.');
    const doc = new DOMParser().parseFromString(text, 'application/xml');
    if (doc.querySelector('parsererror') || !doc.documentElement) throw new Error('Malformed XML. Check tag nesting, quoting and entity escaping.');
    if (doc.getElementsByTagName('*').length > 100000) throw new Error('XML exceeds 100,000 elements.');
    const root = doc.documentElement, kind = root.localName, ns = 'http://www.sitemaps.org/schemas/sitemap/0.9';
    if (!['urlset','sitemapindex'].includes(kind)) throw new Error('Expected a sitemap urlset or sitemapindex root element.');
    const issues = [], entries = [];
    if (root.namespaceURI !== ns) issues.push({code:'unexpected_namespace'});
    const expected = kind === 'urlset' ? 'url' : 'sitemap';
    for (const child of root.children) {
      if (child.localName !== expected || child.namespaceURI !== root.namespaceURI) { issues.push({code:'unexpected_root_child'}); continue; }
      if (entries.length >= 20000) throw new Error('Sitemap Inspector accepts at most 20,000 entries.');
      const entry = {locations:[],lastmods:[],priorities:[],frequencies:[]};
      const fields = {loc:'locations',lastmod:'lastmods',priority:'priorities',changefreq:'frequencies'};
      for (const field of child.children) {
        if (field.namespaceURI !== root.namespaceURI) continue; // Extension namespaces are not inspected.
        const key = fields[field.localName];
        if (!key) { issues.push({position:entries.length + 1,code:'unexpected_entry_field'}); continue; }
        if (field.children.length) issues.push({position:entries.length + 1,code:'nested_content_in_scalar_field'});
        if (kind === 'sitemapindex' && ['priorities','frequencies'].includes(key)) issues.push({position:entries.length + 1,code:'url_only_field_in_sitemap_index'});
        entry[key].push(field.textContent);
      }
      entries.push(entry);
    }
    return {kind, entries, issues};
  }};
})();

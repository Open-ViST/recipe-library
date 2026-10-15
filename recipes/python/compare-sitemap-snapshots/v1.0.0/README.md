# Compare two saved sitemap snapshots

Find added, removed and duplicate URLs in two sitemap urlsets without crawling the website.

Published recipe: [compare-sitemap-snapshots](https://openvist.com/recipes/compare-sitemap-snapshots/)

**Language:** python · **Version:** 1.0.0 · **License:** MIT

## Usage

Code file: `recipe.py`

See requirements below.

## Requirements

- Python 3.10 or later; standard library only.
- Two saved UTF-8 XML sitemap urlsets with the standard sitemap namespace.
- Files up to 8 MiB and 50,000 URL entries each.

## Steps

- Save the earlier and current urlset files in your working folder.
- Run: python sitemap_diff.py before.xml after.xml > sitemap-diff.json
- Inspect added and removed URL lists and the count of unchanged URLs.
- Check duplicate URL lists and investigate unexpected removals.

## Checks

- Use fixtures containing one added URL, one removed URL and one unchanged URL.
- Confirm query strings and duplicate URLs are preserved in comparison.
- Invalid XML, DTDs, wrong namespaces, credentials, fragments, mixed hosts and large files must fail with a nonzero exit status.

## Limits

- Sitemap indexes are not expanded. Download the individual urlsets separately.
- Only URL membership is compared; lastmod, priority and changefreq do not affect the result.
- Sitemap presence indicates discovery information, not actual search-engine indexing, traffic or ranking.

## Recorded validation scope

Executed locally with deterministic fixtures and CLI checks on Python 3.12.14. The three scripts pass 22 tests covering valid output, invalid input and size limits. No network or provider call was made.

This scope is copied from the published recipe. Exporting does not rerun its tests or establish additional guarantees.

## Sources

- https://www.sitemaps.org/protocol.html
- https://docs.python.org/3/library/xml.etree.elementtree.html

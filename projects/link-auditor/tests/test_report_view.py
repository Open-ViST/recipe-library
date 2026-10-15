from base64 import b64encode
from hashlib import sha256
from pathlib import Path
import sys
import unittest
sys.path.insert(0, str(Path(__file__).parents[1]))
from report_view import SCRIPT, html_report


class ReportTests(unittest.TestCase):
    def test_filters_counts_csp_and_escaping(self):
        report = {'started_from':'https://example.com/', 'generated_at':'2026-10-15', 'limits_reached':True,
            'results':[{'url':'https://example.com/<img>', 'status':None, 'outcome':'not_checked', 'redirects':[], 'sources':['</script><script>alert(1)</script>']},
                {'url':'https://example.com/ok', 'status':200, 'outcome':'ok', 'redirects':[], 'sources':[]},
                {'url':'https://example.com/missing', 'status':404, 'outcome':'missing', 'redirects':[], 'sources':[]}]}
        output = html_report(report)
        self.assertEqual(output.count('<tr data-group='), 3)
        for group in ['pending', 'ok', 'findings']:
            self.assertIn('data-group="' + group + '"', output)
        self.assertIn(b64encode(sha256(SCRIPT.encode()).digest()).decode(), output)
        self.assertNotIn('<img>', output)
        self.assertNotIn('<script>alert(1)</script>', output)
        self.assertIn('Unchecked URLs are not failures', output)
        self.assertIn('id="search"', output)
        self.assertIn('id="filter"', output)


if __name__ == '__main__':
    unittest.main()

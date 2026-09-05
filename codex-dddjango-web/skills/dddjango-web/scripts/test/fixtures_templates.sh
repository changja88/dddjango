#!/usr/bin/env bash
# 실제 백스톱 CLI: 누출되는 Django 주석과 정상·레거시 대조군.
set -eu
SCRIPTS="$(cd "$(dirname "$0")/.." && pwd)"
python3 - "$SCRIPTS" <<'PY'
import pathlib
import subprocess
import sys
import tempfile
import unittest

SCRIPT = pathlib.Path(sys.argv.pop()) / 'backstop.py'

class TemplateComments(unittest.TestCase):
    def check_template(self, content, expected, baseline=None, marker='WP6'):
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp)
            target = root / 'web/base/base.html'
            target.parent.mkdir(parents=True)
            if baseline is not None:
                target.write_text(baseline)
                for args in [('init', '-q'), ('add', '.'),
                             ('-c', 'user.name=t', '-c', 'user.email=t@t',
                              'commit', '-qm', 'baseline')]:
                    subprocess.run(['git', '-C', tmp, *args], check=True, capture_output=True)
            target.write_text(content)
            result = subprocess.run([sys.executable, str(SCRIPT), tmp, '--only', 'wp',
                                     *(['--diff-base', 'HEAD'] if baseline is not None else ['--all'])],
                                    text=True, capture_output=True)
            self.assertEqual(result.returncode, expected, result.stdout + result.stderr)
            if expected == 2:
                self.assertIn(marker, result.stdout)

    def test_multiline_short_comment_leaks(self):
        self.check_template('{# title\nprivate implementation note\n#}<h1>Catalog</h1>', 2)

    def test_valid_short_and_block_comments_are_ignored(self):
        self.check_template('{# <script>example</script> #}\n'
                            '{% comment "note" %}\n{# invalid\n#}\n'
                            '<script>ignored</script>{% endcomment %}<h1>Catalog</h1>', 0)

    def test_verbatim_documentation_is_not_a_broken_comment(self):
        self.check_template('{% verbatim demo %}{# example\n#}{% endverbatim demo %}', 0)

    def test_unclosed_short_comment_leaks(self):
        self.check_template('{# accidental unfinished note', 2)

    def test_verbatim_outputs_live_html_including_scripts(self):
        self.check_template('{% verbatim %}{# <script>live()</script> #}{% endverbatim %}',
                            2, marker='WP2')

    def test_named_verbatim_dotted_name_is_valid(self):
        self.check_template('{% verbatim docs.example %}{# example\n#}{% endverbatim docs.example %}', 0)

    def test_html_comment_in_verbatim_is_still_a_browser_comment(self):
        self.check_template('{% verbatim %}<!-- <script>ignored()</script> -->{% endverbatim %}', 0)

    def test_unchanged_legacy_comment_does_not_block(self):
        old = '{# old\nlegacy\n#}\n<h1>Old</h1>\n'
        self.check_template(old.replace('Old', 'New'), 0, old)

    def test_edit_inside_existing_broken_comment_is_checked(self):
        old = '{# old\nlegacy\n#}\n<h1>Catalog</h1>\n'
        self.check_template(old.replace('legacy', 'new note'), 2, old)

unittest.main()
PY

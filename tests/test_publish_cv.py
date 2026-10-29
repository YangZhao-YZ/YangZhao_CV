"""Exercise publication behavior against a real, isolated Git remote."""

import importlib.util
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / '.github/scripts/publish_cv.py'
spec = importlib.util.spec_from_file_location('publish_cv', SCRIPT)
publisher = importlib.util.module_from_spec(spec)
spec.loader.exec_module(publisher)


class PublicationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.repo = self.root / 'checkout'
        self.repo.mkdir()
        self.previous = Path.cwd()
        os.chdir(self.repo)
        self.addCleanup(os.chdir, self.previous)
        self.git('init', '--bare', str(self.root / 'remote.git'))
        self.git('init', '-b', 'main')
        self.git('config', 'user.name', 'CV Test')
        self.git('config', 'user.email', 'cv-test@example.invalid')
        self.git('remote', 'add', 'origin', str(self.root / 'remote.git'))

    def git(self, *args, env=None):
        return subprocess.check_output(['git', *args], text=True, stderr=subprocess.DEVNULL, env=env).strip()

    def source(self, text, when):
        Path('main.tex').write_text(text)
        self.git('add', 'main.tex')
        env = dict(os.environ, GIT_AUTHOR_DATE=when, GIT_COMMITTER_DATE=when)
        self.git('commit', '-m', text, env=env)
        return self.git('rev-parse', 'HEAD')

    def publish(self, source, content):
        pdf = self.root / 'compiled.pdf'
        pdf.write_bytes(content)
        publisher.publish(pdf, source, 'main')

    def test_daily_overwrite_idempotence_and_out_of_order_runs(self):
        older = self.source('first edit', '2026-10-28T23:00:00+00:00')
        newer = self.source('second edit', '2026-10-28T23:01:00+00:00')
        tomorrow = self.source('next day edit', '2026-10-29T23:00:00+00:00')
        self.git('push', 'origin', 'main')
        self.publish(older, b'%PDF-first')
        self.assertIn('[skip ci]', self.git('log', '-1', '--format=%s'))
        self.publish(newer, b'%PDF-second')
        daily = Path('history/YangZhao_CV_20261028.pdf')
        self.assertEqual(daily.read_bytes(), b'%PDF-second')
        self.assertEqual(len(list(Path('history').glob('*.pdf'))), 1)
        published_head = self.git('rev-parse', 'HEAD')
        self.publish(newer, b'%PDF-rerun')
        self.assertEqual(self.git('rev-parse', 'HEAD'), published_head)
        self.publish(older, b'%PDF-late-old-build')
        self.assertEqual(daily.read_bytes(), b'%PDF-second')
        self.publish(tomorrow, b'%PDF-tomorrow')
        self.assertEqual(Path('YangZhao_CV.pdf').read_bytes(), b'%PDF-tomorrow')
        self.assertEqual(daily.read_bytes(), b'%PDF-second')
        self.assertEqual(len(list(Path('history').glob('*.pdf'))), 2)
        state = json.loads(Path('history/build-index.json').read_text())
        self.assertEqual(state['latest'], tomorrow)
        self.assertEqual(state['daily']['20261028'], newer)

    def test_chicago_date_and_invalid_pdf(self):
        source = self.source('late evening Chicago', '2026-10-29T02:00:00+00:00')
        self.git('push', 'origin', 'main')
        with self.assertRaises(ValueError):
            self.publish(source, b'compiler failure')
        self.assertFalse(Path('YangZhao_CV.pdf').exists())
        self.publish(source, b'%PDF-valid')
        self.assertTrue(Path('history/YangZhao_CV_20261028.pdf').exists())
        self.assertFalse(Path('history/YangZhao_CV_20261029.pdf').exists())


if __name__ == '__main__':
    unittest.main()

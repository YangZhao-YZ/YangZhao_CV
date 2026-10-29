"""Exercise publication behavior against a real, isolated Git remote."""

import hashlib
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


def pdf(text, metadata='original', pages=1):
    """Small valid PDF fixtures with controllable visible text and metadata."""
    objects = [b'<< /Type /Catalog /Pages 2 0 R >>', b'',
               b'<< >>']
    kids = []
    for number in range(pages):
        page_id = len(objects) + 1
        kids.append(f'{page_id} 0 R')
        objects.append((f'<< /Type /Page /Parent 2 0 R /MediaBox [0 0 200 200] '
                        f'/Resources << >> '
                        f'/Contents {page_id + 1} 0 R >>').encode())
        # Vector fixtures avoid relying on machine-specific installed fonts.
        digest = hashlib.sha256(f'{text} page {number}'.encode()).digest()
        stream = b' '.join(f'{10 + i * 5} 10 3 {20 + value % 150} re f'.encode()
                           for i, value in enumerate(digest))
        objects.append(f'<< /Length {len(stream)} >>\nstream\n'.encode() + stream + b'\nendstream')
    objects[1] = f'<< /Type /Pages /Kids [{" ".join(kids)}] /Count {pages} >>'.encode()
    objects.append(f'<< /Producer ({metadata}) >>'.encode())
    data = b'%PDF-1.4\n'
    offsets = [0]
    for number, obj in enumerate(objects, 1):
        offsets.append(len(data))
        data += f'{number} 0 obj\n'.encode() + obj + b'\nendobj\n'
    start = len(data)
    data += f'xref\n0 {len(offsets)}\n0000000000 65535 f \n'.encode()
    data += b''.join(f'{offset:010d} 00000 n \n'.encode() for offset in offsets[1:])
    data += (f'trailer\n<< /Size {len(offsets)} /Root 1 0 R /Info {len(objects)} 0 R >>'
             f'\nstartxref\n{start}\n%%EOF\n').encode()
    return data


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
        self.git('push', 'origin', 'HEAD:main')
        self.publish(older, pdf('first'))
        self.assertIn('[skip ci]', self.git('log', '-1', '--format=%s'))
        newer = self.source('second edit', '2026-10-28T23:01:00+00:00')
        self.git('push', 'origin', 'HEAD:main')
        self.publish(newer, pdf('second'))
        daily = Path('history/YangZhao_CV_20261028.pdf')
        self.assertEqual(daily.read_bytes(), pdf('second'))
        self.assertEqual(len(list(Path('history').glob('*.pdf'))), 1)
        published_head = self.git('rev-parse', 'HEAD')
        self.publish(newer, pdf('rerun'))
        self.assertEqual(self.git('rev-parse', 'HEAD'), published_head)
        self.publish(older, pdf('late-old-build'))
        self.assertEqual(daily.read_bytes(), pdf('second'))
        tomorrow = self.source('next day edit', '2026-10-29T23:00:00+00:00')
        self.git('push', 'origin', 'HEAD:main')
        self.publish(tomorrow, pdf('tomorrow'))
        self.assertEqual(Path('YangZhao_CV.pdf').read_bytes(), pdf('tomorrow'))
        self.assertEqual(daily.read_bytes(), pdf('second'))
        self.assertEqual(len(list(Path('history').glob('*.pdf'))), 2)
        state = json.loads(Path('history/build-index.json').read_text())
        self.assertEqual(state['latest'], tomorrow)
        self.assertEqual(state['daily']['20261028'], newer)

    def test_unchanged_cv_does_not_create_commit_or_next_day_backup(self):
        first = self.source('CV update', '2026-10-28T23:00:00+00:00')
        self.git('push', 'origin', 'HEAD:main')
        original = pdf('same CV')
        self.publish(first, original)
        older_pending = self.source('intermediate edit', '2026-10-29T22:00:00+00:00')
        unrelated = self.source('documentation only', '2026-10-29T23:00:00+00:00')
        self.git('push', 'origin', 'HEAD:main')
        published_head = self.git('rev-parse', 'HEAD')
        original_index = Path('history/build-index.json').read_bytes()
        self.publish(unrelated, original)
        self.publish(unrelated, pdf('same CV', metadata='different build timestamp and ID'))
        self.publish(older_pending, pdf('late obsolete CV'))
        self.assertEqual(self.git('rev-parse', 'HEAD'), published_head)
        self.assertEqual(Path('history/build-index.json').read_bytes(), original_index)
        self.assertEqual(Path('YangZhao_CV.pdf').read_bytes(), original)
        self.assertFalse(Path('history/YangZhao_CV_20261029.pdf').exists())
        changed = self.source('CV visibly changed', '2026-10-30T23:00:00+00:00')
        self.git('push', 'origin', 'HEAD:main')
        self.publish(changed, pdf('new CV'))
        self.assertTrue(Path('history/YangZhao_CV_20261030.pdf').exists())
        self.assertEqual(len(list(Path('history').glob('*.pdf'))), 2)

    def test_comparison_checks_later_pages_and_page_count(self):
        first = self.root / 'first.pdf'
        second = self.root / 'second.pdf'
        first.write_bytes(pdf('same', pages=2))
        second.write_bytes(pdf('same', metadata='new metadata', pages=2))
        self.assertTrue(publisher.same_cv(first, second))
        original = pdf('same', pages=2)
        # Only the second page changes; keep stream lengths and xref offsets valid.
        second_stream = original.index(b'stream', original.index(b'7 0 obj'))
        second.write_bytes(original[:second_stream] +
                           original[second_stream:].replace(b'10 10 3', b'11 10 3', 1))
        self.assertFalse(publisher.same_cv(first, second))
        second.write_bytes(pdf('same', pages=1))
        self.assertFalse(publisher.same_cv(first, second))

    def test_chicago_date_and_invalid_pdf(self):
        source = self.source('late evening Chicago', '2026-10-29T02:00:00+00:00')
        self.git('push', 'origin', 'HEAD:main')
        with self.assertRaises(ValueError):
            self.publish(source, b'compiler failure')
        self.assertFalse(Path('YangZhao_CV.pdf').exists())
        self.publish(source, pdf('valid'))
        self.assertTrue(Path('history/YangZhao_CV_20261028.pdf').exists())
        self.assertFalse(Path('history/YangZhao_CV_20261029.pdf').exists())


if __name__ == '__main__':
    unittest.main()

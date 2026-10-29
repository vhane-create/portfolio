from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from install_mac import install, git_hash, MANIFEST


class InstallerTests(unittest.TestCase):
    def test_release_contains_approved_identity_voice_and_local_runtime(self):
        for path in ['assets/aria-full-body-approved.png', 'assets/ARIA_Heart_Introduction.mp4',
                     'voice-loop.js', 'heart-worker.js', 'mac-demo/server.py', 'aria-final.html',
                     'mac-demo/face-replies.js', 'heart-backend/heart_server.py', 'assets/aria-approved--d0.mp4']:
            self.assertIn(path, MANIFEST)
        self.assertEqual(MANIFEST['assets/aria-full-body-approved.png']['sha'], '31197d446c9fb52b741b8d91f7ceebed7ec35a89')

    def test_install_reuses_verified_files_and_preserves_other_files(self):
        data = b'package content'
        manifest = {'assets/file.txt': {'sha':git_hash(data), 'size':len(data)}}
        with tempfile.TemporaryDirectory() as folder:
            other = Path(folder) / 'unrelated.txt'; other.write_text('keep')
            self.assertEqual(install(folder, manifest, lambda *args:data), 1)
            self.assertEqual(install(folder, manifest, lambda *args:self.fail('Should reuse verified files')), 0)
            self.assertEqual(other.read_text(), 'keep')
            (Path(folder) / 'assets/file.txt').write_text('user changes')
            with self.assertRaisesRegex(ValueError, 'not overwritten'):
                install(folder, manifest, lambda *args:data)
            self.assertEqual((Path(folder) / 'assets/file.txt').read_text(), 'user changes')

    def test_corrupt_download_and_unsafe_paths_do_not_install(self):
        data = b'good'
        manifest = {'file.txt': {'sha':git_hash(data), 'size':len(data)}}
        with tempfile.TemporaryDirectory() as folder:
            with self.assertRaisesRegex(ValueError, 'did not match'):
                install(folder, manifest, lambda *args:b'evil')
            self.assertFalse((Path(folder) / 'file.txt').exists())
            with self.assertRaisesRegex(ValueError, 'Invalid package path'):
                install(folder, {'../escape':manifest['file.txt']}, lambda *args:data)

    def test_failed_write_leaves_no_partial_installed_file(self):
        data = b'complete file'
        manifest = {'file.txt': {'sha':git_hash(data), 'size':len(data)}}
        with tempfile.TemporaryDirectory() as folder:
            with patch('install_mac.os.fsync', side_effect=OSError('write failed')):
                with self.assertRaises(OSError): install(folder, manifest, lambda *args:data)
            self.assertFalse((Path(folder) / 'file.txt').exists())
            self.assertEqual(list(Path(folder).iterdir()), [])
            self.assertEqual(install(folder, manifest, lambda *args:data), 1)


if __name__ == '__main__': unittest.main()

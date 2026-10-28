"""Portable regression checks; these do not claim to verify Mac neural inference."""
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
from unittest.mock import patch
import aria_runtime as aria


class RuntimeTests(unittest.TestCase):
    def test_exact_approved_portrait_and_existing_image_protection(self):
        with tempfile.TemporaryDirectory(prefix='ARIA space ') as tmp:
            root = Path(tmp)
            aria.preserve_portrait(root)
            self.assertEqual(aria.sha256(root / 'aria-approved.png'), aria.PORTRAIT_SHA)
            (root / 'aria-approved.png').write_bytes(b'other portrait')
            with self.assertRaisesRegex(RuntimeError, 'changed'):
                aria.preserve_portrait(root)
            self.assertEqual((root / 'aria-approved.png').read_bytes(), b'other portrait')

    def test_media_without_video_or_duration_fails(self):
        for info in ({}, {'streams': [{'codec_type': 'audio'}]},
                     {'streams': [{'codec_type': 'video'}], 'format': {'duration': '0'}}):
            with self.assertRaises(RuntimeError):
                aria.video_stream(info)

    def test_missing_and_lfs_models_fail(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            with self.assertRaisesRegex(RuntimeError, 'model'):
                aria.check_weights(repo)
            first = repo / 'pretrained_weights' / aria.WEIGHTS[0]
            first.parent.mkdir(parents=True)
            first.write_bytes(b'version https://git-lfs.github.com/spec/v1\n' + b'0' * 1100)
            with self.assertRaisesRegex(RuntimeError, 'LFS'):
                aria.check_weights(repo)

    def test_never_invokes_inference_for_silent_driver(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            driver = root / 'speaking clip.mp4'
            driver.touch()
            (root / 'environment-check.json').write_text('{}')
            with patch.object(aria, 'checkout', return_value=root), patch.object(aria, 'approved'), \
                 patch.object(aria, 'check_weights'), patch.object(aria, 'probe', return_value={
                     'streams': [{'codec_type': 'video'}], 'format': {'duration': '5'}}), \
                 patch.object(aria.subprocess, 'run') as run:
                with self.assertRaisesRegex(RuntimeError, 'speech audio'):
                    aria.animate(root, driver)
                run.assert_not_called()

    def test_complete_orchestration_with_spaces_and_output_validation(self):
        with tempfile.TemporaryDirectory(prefix='ARIA path with spaces ') as tmp:
            root = Path(tmp)
            driver = root / 'speaking clip.mp4'
            driver.touch()
            (root / 'environment-check.json').write_text('{}')
            media = {'streams': [{'codec_type': 'video'}, {'codec_type': 'audio'}],
                     'format': {'duration': '5'}}
            with patch.object(aria, 'checkout', return_value=root), patch.object(aria, 'approved'), \
                 patch.object(aria, 'check_weights'), patch.object(aria, 'probe', return_value=media), \
                 patch.object(aria.subprocess, 'run') as run:
                aria.animate(root, driver)
                command = run.call_args_list[0].args[0]
                self.assertEqual(command[command.index('-d') + 1], str(driver))
                self.assertIn('--animation_region', command)
                self.assertIn('--no_flag_use_half_precision', command)
                self.assertEqual(run.call_args_list[0].kwargs['env']['PYTORCH_ENABLE_MPS_FALLBACK'], '1')
                self.assertIn('-xerror', run.call_args_list[1].args[0])
                reports = list(root.glob('animations/*/render-check.json'))
                self.assertEqual(len(reports), 1)
                self.assertIn('pending', json.loads(reports[0].read_text())['visual_review'])

    def test_failed_render_does_not_write_success(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            driver = root / 'clip.mp4'
            driver.touch()
            (root / 'environment-check.json').write_text('{}')
            media = {'streams': [{'codec_type': 'video'}, {'codec_type': 'audio'}], 'format': {'duration': '5'}}
            with patch.object(aria, 'checkout', return_value=root), patch.object(aria, 'approved'), \
                 patch.object(aria, 'check_weights'), patch.object(aria, 'probe', return_value=media), \
                 patch.object(aria.subprocess, 'run', side_effect=subprocess.CalledProcessError(1, 'inference')):
                with self.assertRaises(subprocess.CalledProcessError):
                    aria.animate(root, driver)
                self.assertEqual(list(root.glob('animations/*/render-check.json')), [])

    @unittest.skipUnless(shutil.which('ffmpeg') and shutil.which('ffprobe'), 'FFmpeg unavailable')
    def test_real_ffmpeg_probe(self):
        with tempfile.TemporaryDirectory(prefix='media space ') as tmp:
            video = Path(tmp) / 'test clip.mp4'
            subprocess.run(['ffmpeg', '-v', 'error', '-f', 'lavfi', '-i', 'color=c=black:s=64x64:r=25',
                            '-f', 'lavfi', '-i', 'sine=frequency=440', '-t', '0.4',
                            '-c:v', 'mpeg4', '-c:a', 'aac', str(video)], check=True)
            info = aria.probe(video)
            self.assertEqual(aria.video_stream(info)['width'], 64)
            self.assertTrue(any(s['codec_type'] == 'audio' for s in info['streams']))


if __name__ == '__main__':
    unittest.main()

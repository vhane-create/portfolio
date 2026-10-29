import tempfile
from pathlib import Path
import unittest
from unittest.mock import patch
import wave
import render_body as renderer


class InputChecks(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.image = Path(self.temp.name) / 'image.png'
        self.image.write_bytes(b'unapproved image')
        self.audio = Path(self.temp.name) / 'heart.wav'

    def wav(self, seconds):
        with wave.open(str(self.audio), 'wb') as audio:
            audio.setnchannels(1)
            audio.setsampwidth(2)
            audio.setframerate(24000)
            audio.writeframes(b'\0\0' * int(seconds * 24000))

    def test_rejects_changed_appearance(self):
        self.wav(1)
        with self.assertRaisesRegex(ValueError, 'approved full-body'):
            renderer.validate_inputs(self.image, self.audio)

    def test_does_not_silently_truncate_long_answers(self):
        self.wav(7)
        with patch.object(renderer, 'digest', return_value=renderer.PORTRAIT_SHA256):
            with self.assertRaisesRegex(ValueError, 'longer replies are not implemented'):
                renderer.validate_inputs(self.image, self.audio)

    def test_entire_short_audio_fits_temporal_grid(self):
        self.wav(3.05)
        with patch.object(renderer, 'digest', return_value=renderer.PORTRAIT_SHA256):
            duration, frames = renderer.validate_inputs(self.image, self.audio)
        self.assertGreaterEqual(frames / 25, duration)
        self.assertEqual((frames - 1) % 4, 0)
        command = renderer.command(Path('/repo'), Path('/weights'), self.image, self.audio, Path('/output'), frames)
        self.assertEqual(command[command.index('--image_path') + 1], str(self.image))
        self.assertEqual(command[command.index('--audio_path') + 1], str(self.audio))


if __name__ == '__main__':
    unittest.main()

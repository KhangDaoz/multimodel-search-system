import io
from pathlib import Path
import unittest
import wave
from main import build_ui
from application.speech_service import SpeechService, SpeechUnavailable


class SpeechTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ui = build_ui()
        if not cls.ui.speech_service.status()['ready']:
            raise unittest.SkipTest('Install Vosk/model and FFmpeg for real audio tests')

    def test_actual_wav_recognition_and_search(self):
        audio = Path('tests/fixtures/blue_shoes.wav').read_bytes()
        r = self.ui.submit_audio(audio)
        self.assertEqual(r['speech']['source'],'audio')
        self.assertIn('blue shoes',r['speech']['text'])
        self.assertEqual(r['query']['type'],'voice')
        self.assertEqual(r['results'][0]['product']['id'],3)
        self.assertNotIn('simulated',' '.join(r['processing']))

    def test_bad_audio_and_silence(self):
        with self.assertRaises(ValueError): self.ui.submit_audio(b'not an audio file')
        stream = io.BytesIO()
        with wave.open(stream,'wb') as w:
            w.setnchannels(1); w.setsampwidth(2); w.setframerate(16000); w.writeframes(b'\x00'*64000)
        with self.assertRaisesRegex(ValueError,'No speech detected'): self.ui.submit_audio(stream.getvalue())

    def test_missing_model_has_actionable_error(self):
        service = SpeechService('/tmp/forme-model-not-installed')
        self.assertFalse(service.status()['ready'])
        with self.assertRaises(SpeechUnavailable): service.transcribe_audio(b'bytes')

if __name__ == '__main__': unittest.main()

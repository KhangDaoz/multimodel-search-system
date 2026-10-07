"""Real offline English recognition; transcript adapter is for CLI regression tests."""
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import threading


class SpeechUnavailable(RuntimeError):
    pass


class SpeechService:
    MAX_SECONDS = 15

    def __init__(self, model_path=None):
        self.model_path = Path(model_path or os.environ.get('VOSK_MODEL_PATH',
            Path(__file__).resolve().parents[1] / 'models/vosk-model-small-en-us-0.15'))
        self._model = None
        self._lock = threading.Lock()

    def status(self):
        ready = (self.model_path / 'am/final.mdl').is_file() and shutil.which('ffmpeg') is not None and importlib.util.find_spec('vosk') is not None
        return {'ready': ready, 'engine': 'Vosk offline', 'language': 'en-US',
                'max_seconds': self.MAX_SECONDS,
                'message': 'Ready for English speech' if ready else 'Run python tools/setup_voice.py and install FFmpeg to enable voice search'}

    def _load_model(self):
        with self._lock:
            if self._model is None:
                if not self.status()['ready']:
                    raise SpeechUnavailable(self.status()['message'])
                from vosk import Model, SetLogLevel
                SetLogLevel(-1)
                self._model = Model(str(self.model_path))
        return self._model

    def transcribe_audio(self, audio):
        if not isinstance(audio, bytes) or not audio or len(audio) > 5 * 1024 * 1024:
            raise ValueError('Provide an audio recording smaller than 5 MB')
        model = self._load_model()
        with tempfile.TemporaryDirectory(prefix='forme-audio-') as folder:
            source = Path(folder) / 'recording'
            source.write_bytes(audio)
            try:
                decoded = subprocess.run([
                    shutil.which('ffmpeg'), '-nostdin', '-v', 'error',
                    '-protocol_whitelist', 'file,pipe', '-i', str(source),
                    '-t', str(self.MAX_SECONDS + 1), '-ac', '1', '-ar', '16000',
                    '-f', 's16le', '-'], capture_output=True, timeout=20, check=True)
            except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as error:
                raise ValueError('Cannot read this recording. Try WAV, WebM, Ogg or MP4.') from error
        pcm = decoded.stdout
        duration = len(pcm) / 32000
        if duration < 0.2 or duration > self.MAX_SECONDS + 0.05:
            raise ValueError(f'Record between 0.2 and {self.MAX_SECONDS} seconds')
        from vosk import KaldiRecognizer
        recognizer = KaldiRecognizer(model, 16000)
        parts = []
        for offset in range(0, len(pcm), 8000):
            if recognizer.AcceptWaveform(pcm[offset:offset + 8000]):
                parts.append(json.loads(recognizer.Result()).get('text', ''))
        parts.append(json.loads(recognizer.FinalResult()).get('text', ''))
        text = ' '.join(part for part in parts if part).strip()
        if not text:
            raise ValueError('No speech detected. Speak clearly in English and try again.')
        return {'text': text, 'engine': 'Vosk offline', 'language': 'en-US',
                'duration_seconds': round(duration, 2), 'source': 'audio'}

    def transcribe(self, transcript):
        """Explicit transcript adapter for CLI/tests; never used by the web voice route."""
        if not isinstance(transcript, str):
            raise ValueError('Transcript must be a string')
        return transcript.strip()

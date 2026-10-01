class SpeechService:
    def transcribe(self, audio_input):
        # Simulation: input is an existing transcript, not an audio recording.
        if not isinstance(audio_input, str):
            raise ValueError('Simulated speech service expects a transcript string')
        return audio_input.strip()

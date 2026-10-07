# Actual audio fixtures

Generated with eSpeak NG, not recorded human speech:

```
espeak-ng -v en-us -s 140 -w blue_shoes.wav 'find blue shoes'
espeak-ng -v en-us -s 140 -w black_bag.wav 'find a black bag'
```

The files contain actual PCM audio. Vosk recognizes their audio at runtime;
there is no transcript lookup or STT mock. The second fixture intentionally
retains a recognition failure. The browser test supplies the first fixture to
Chromium's virtual microphone and exercises MediaRecorder → audio bytes → FFmpeg
→ Vosk → search. This does not certify human voices/accents or physical hardware.

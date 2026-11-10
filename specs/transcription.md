# Speech Transcription Specifications

## STT-001: MLX Whisper Transcription & Low-Gain Normalization

When provided with an audio buffer, the transcriber shall normalize input gain, filter digital silence, and transcribe the speech using Whisper Large-V3-Turbo.

Acceptance Criteria:
- AC-STT-001.1: When given valid audio, the transcriber shall scale the peak amplitude to 0.95 and return transcribed text.
- AC-STT-001.2: If audio data is empty or shorter than 0.5 seconds, then the transcriber shall return an empty string.
- AC-STT-001.3: If audio energy root mean square is below 0.0001, then the transcriber shall return an empty string.
- AC-STT-001.4: Where low-gain Bluetooth headset audio is received, the transcriber shall normalize the signal before inference.

## STT-002: Multilingual Roman Script Steering & Hallucination Suppression

When transcribing speech, the transcriber shall steer Roman phonetic output and discard repetitive silence hallucinations.

Acceptance Criteria:
- AC-STT-002.1: Where Roman script mode is selected, the transcriber shall pass Latin phonetic prompt steering to Whisper.
- AC-STT-002.2: If the transcription output matches a known silence hallucination phrase, then the transcriber shall return an empty string.
- AC-STT-002.3: If the underlying Whisper engine raises an exception, then the transcriber shall return an empty string.


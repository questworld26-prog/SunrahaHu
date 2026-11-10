# Text Injection & Audio Feedback Specifications

## INJ-001: Direct Quartz Unicode Typing & Pasteboard Fallback

When injecting text into the active window, the text injector shall dispatch direct Quartz Unicode key events and append trailing whitespace.

Acceptance Criteria:
- AC-INJ-001.1: When given non-empty text, the text injector shall type Unicode characters directly via Quartz event APIs.
- AC-INJ-001.2: When injecting text, the text injector shall ensure the output ends with trailing whitespace for continuous dictation.
- AC-INJ-001.3: If the injection method is set to paste, then the injector shall restore the original system pasteboard content.
- AC-INJ-001.4: If the input text is empty, then the text injector shall return immediately without generating keyboard events.

## FDB-001: Zero-Bleed Audio Cues & TTS Speech Fallback

When dictation state changes or commands execute, the feedback player shall play corresponding audio cues or speak synthetic voice feedback.

Acceptance Criteria:
- AC-FDB-001.1: When recording starts, the feedback player shall play the listening audio prompt before audio capture begins.
- AC-FDB-001.2: When recording stops, the feedback player shall play the typing audio prompt before transcription completes.
- AC-FDB-001.3: When text injection completes, the feedback player shall play the completion sound.
- AC-FDB-001.4: When a command confirmation message is provided, the feedback player shall speak the message using system voice synthesis.
- AC-FDB-001.5: If an audio cue asset is missing on disk, then the feedback player shall invoke system speech synthesis as a fallback.


# Audio Capture & Voice Activity Detection Specifications

## VAD-001: Silero Neural Voice Activity Detection

When evaluating an audio buffer, the Silero VAD classifier shall calculate the speech probability of incoming 512-sample audio chunks using the neural model.

Acceptance Criteria:
- AC-VAD-001.1: When given a 512-sample float32 chunk, the classifier shall return whether speech is present and its probability.
- AC-VAD-001.2: If the input chunk length is not 512 samples, then the classifier shall return false and zero probability.
- AC-VAD-001.3: When processing silence or continuous background fan noise, the classifier shall evaluate speech probability below 0.15.

## AUD-001: CoreAudio Stream Capture & Mutex-Safe Teardown

When recording starts, the audio recorder shall capture 16kHz mono audio via a non-blocking stream and abort stream resources safely upon stopping.

Acceptance Criteria:
- AC-AUD-001.1: When started, the audio recorder shall open a 16kHz mono input stream with a non-blocking audio callback.
- AC-AUD-001.2: When stopped, the audio recorder shall abort and close the active stream without blocking the calling thread.
- AC-AUD-001.3: If audio input initialization fails, then the audio recorder shall reset recording state and raise the underlying error.
- AC-AUD-001.4: Where a specific input device index is configured, the audio recorder shall pass the selected device to the input stream.

## AUD-002: Streaming VAD Auto-Stop & Initial Silence Timeout

While audio recording is active with VAD enabled, the audio recorder shall evaluate speech frames and trigger completion callbacks on trailing silence or initial silence timeout.

Acceptance Criteria:
- AC-AUD-002.1: While recording speech, when trailing silence exceeds 1.3 seconds, the audio recorder shall trigger the silence callback.
- AC-AUD-002.2: While recording without initial speech, when silence reaches 6.0 seconds, the audio recorder shall trigger the timeout callback.
- AC-AUD-002.3: Where VAD is disabled, the audio recorder shall capture audio frames continuously without triggering silence callbacks.


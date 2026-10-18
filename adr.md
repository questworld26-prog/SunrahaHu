# Architecture Decision Records (ADRs)

## ADR-0001: Background Dictation Architecture & Technology Stack

- **Status**: Accepted
- **Date**: 2026-10-18
- **Deciders**: Engineering Team

### Context
Users on Apple Silicon macOS need a global voice dictation tool that can transcribe speech in multiple languages (English, Hindi, Bengali, etc.) and inject the transcribed text directly into any focused application without requiring an active browser or dedicated GUI window. The application must run unobtrusively in the background without interfering with developer workflows, heavy local LLM frameworks (such as Ollama), or consuming excessive RAM on 8GB machines.

### Decision
1. **Inference Framework**:
   - Use **`mlx-whisper`** with the **`whisper-large-v3-turbo`** model weights (`mlx-community/whisper-large-v3-turbo`).
   - Rationale: Runs natively on Apple Silicon Metal GPU with Unified Memory. Loads in ~545 MB of peak RAM compared to >3 GB for the standard Large-v3 model, making it safe to run alongside Ollama and modern IDEs on 8 GB systems.
2. **Audio Feedback ("सुन रहा हूँ") & Mic Timing**:
   - Play the voice prompt synchronously *before* opening the microphone capture stream.
   - Rationale: Prevents the MacBook speakers from bleeding into the microphone, which previously caused Whisper to auto-detect the Hindi audio prompt as part of the user's spoken sentence.
3. **Active Window Text Injection**:
   - Primary: Use direct Unicode keyboard event simulation via `Quartz.CGEventKeyboardSetUnicodeString`.
   - Rationale: Directly injects Unicode text (English, Bengali, Hindi, emojis) without touching `NSPasteboard` or using `Cmd+V`. This completely eliminates clipboard race conditions where an application occasionally pasted previous clipboard contents before the pasteboard update was flushed.
   - Fallback: Clipboard `Cmd+V` simulation with generous window server sync intervals.
4. **Project Layout**:
   - Standardize on `src/sunrahahu` and `tests/` with `hatchling` and `uv` package management.
   - Enforce code hygiene using **Ruff** (`ruff check`, `ruff format`) and **Pytest**.
5. **Language Selection**:
   - Provide an explicit language picker in the Menu Bar (Auto Detect, বাংলা, हिन्दी, English).
   - Rationale: Bengali and Hindi phonetic overlap can cause Whisper's auto-detect to default to Devanagari script; explicit language tags lock tokenization to the intended script.

### Consequences
- Requires macOS Accessibility and Input Monitoring permissions to capture global hotkeys and synthesize paste keystrokes.
- Translation (`task="translate"`) is not supported by `whisper-large-v3-turbo` due to OpenAI architectural pruning; the application focuses on high-speed multilingual native-script transcription.

---

## ADR-0002: Native RMS Energy Voice Activity Detection (VAD) & Silence Auto-Stop

- **Status**: Superseded by ADR-0003
- **Date**: 2026-10-18
- **Deciders**: Engineering Team

### Context
Dictation previously required two explicit user interactions: clicking "🎙️ Dictate (Toggle)" to start recording ("सुन रहा हूँ") and clicking "⏹️ Stop Recording" to finish and transcribe. For rapid dictation and voice commands (e.g., *"Computer, switch to desktop 3"*), users expect a single-trigger "click-speak-and-forget" workflow where the system automatically detects when speech has ceased and immediately triggers transcription.

### Decision
1. **Detection Method (Native RMS Energy)**:
   - Compute the Root Mean Square ($RMS = \sqrt{\text{mean}(x^2)}$) on incoming 16kHz float32 audio buffers inside PortAudio's `_callback`.
   - **Speech Threshold**: `RMS >= 0.012` (later adjusted to `0.0035`) for a minimum of `0.25s` (`min_speech_duration`).
   - **Trailing Silence Threshold**: `RMS < 0.006` sustained continuously for `1.3s` (`silence_duration`).

### Why This Approach Was Abandoned / Superseded
In real-world deployment, physical environments frequently have continuous broadband acoustic noise such as ceiling/desk fans, air conditioners (AC), or laptop blowers. 
- Static energy metrics (RMS) measure total signal amplitude without distinguishing between human speech and fan hiss.
- If thresholds were set low enough to hear normal or soft voice, continuous fan/AC noise was recognized as speech 24/7, preventing trailing silence from ever triggering.
- Switching between MacBook internal microphones and headphones/headsets dramatically altered the input gain and ambient noise floor, making any fixed threshold brittle.

---

## ADR-0003: Silero Neural Voice Activity Detection (VAD) via ONNX Runtime

- **Status**: Accepted
- **Date**: 2026-10-18
- **Deciders**: Engineering Team

### Context
Following the limitations of static RMS energy detection in ADR-0002 when exposed to fan and AC background noise and varied microphone setups (built-in mic vs. headphones), an acoustic classification system was needed that can identify human vocal tract patterns independent of ambient broadband room noise.

### Decision
1. **Neural VAD Architecture (Silero VAD v5)**:
   - Adopt the state-of-the-art **Silero VAD v5** model packaged as a lightweight ONNX binary (`src/sunrahahu/assets/silero_vad.onnx`, ~2.3 MB).
   - Execute inference using **`onnxruntime`** (`onnxruntime>=1.20.0`) on Apple Silicon CPU (`CPUExecutionProvider`).
   - Process streaming audio in 512-sample windows (32ms at 16kHz) with a 64-sample recurrent context prefix.
2. **Acoustic Discrimination (Immunity to Fans & AC)**:
   - Silero VAD evaluates spectral formants and vocal cord harmonics rather than raw sound pressure/volume.
   - Empirical benchmarks: Loud fan/AC noise (RMS 0.03) produces a speech probability of only `~0.012` (non-speech), while human speech immediately produces `0.95 – 1.00`.
   - **Speech Threshold**: Probability `p >= 0.50` sustained for `0.15s` (`min_speech_duration`).
   - **Trailing Silence Threshold**: Probability `p < 0.50` sustained for `1.3s` (`silence_duration`).
   - **Grace Period**: 6.0s timeout if no speech is detected, which invokes `stop_and_transcribe()` to ensure no words are ever discarded.
3. **Hardware & Resource Efficiency**:
   - Single-chunk inference executes in **`0.11 ms`** on Apple Silicon CPU (< 0.4% of 1 CPU core).
   - Runs exclusively on CPU threads, avoiding any resource contention with Whisper Large-V3-Turbo on the Metal GPU.
4. **Universal Microphone Compatibility**:
   - Works out-of-the-box across MacBook internal mics, AirPods, USB headsets, and studio condenser microphones without user calibration.

### Consequences
- True "click-speak-and-forget" hands-free dictation that operates reliably even in loud rooms with fans, air conditioning, or varying background noise.
- Small dependency addition (`onnxruntime`), which installs cleanly as a pre-built wheel on macOS ARM64 Python 3.13.



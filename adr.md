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

- **Status**: Accepted
- **Date**: 2026-10-18
- **Deciders**: Engineering Team

### Context
Dictation previously required two explicit user interactions: clicking "🎙️ Dictate (Toggle)" to start recording ("सुन रहा हूँ") and clicking "⏹️ Stop Recording" to finish and transcribe. For rapid dictation and voice commands (e.g., *"Computer, switch to desktop 3"*), users expect a single-trigger "click-speak-and-forget" workflow where the system automatically detects when speech has ceased and immediately triggers transcription.

### Decision
1. **Detection Method (Native RMS Energy)**:
   - Compute the Root Mean Square ($RMS = \sqrt{\text{mean}(x^2)}$) on incoming 16kHz float32 audio buffers inside PortAudio's `_callback`.
   - **Speech Threshold**: `RMS >= 0.012` for a minimum of `0.25s` (`min_speech_duration`) to distinguish intentional speech from ambient spikes, key clicks, or throat clearing.
   - **Trailing Silence Threshold**: `RMS < 0.006` sustained continuously for `1.3s` (`silence_duration`), triggering automatic stop and transcription.
   - **Initial Silence Grace Period**: `6.0s` (`max_initial_silence`) timeout if no speech is detected after trigger, safely aborting the session to conserve resources.
2. **Zero Additional Dependencies**:
   - Implemented entirely using native `numpy` vector operations already in the core pipeline, bypassing heavy dependencies (Silero VAD, WebRTC C extensions, ONNX Runtime, or PyTorch).
   - CPU overhead is $< 0.1\%$ per callback.
3. **Thread Safety & RunLoop Isolation**:
   - VAD callback transitions dispatch to a dedicated daemon thread (`threading.Thread`) before calling `stop_and_transcribe()`.
   - Never blocks PortAudio's high-priority audio callback thread or macOS Cocoa's main UI thread.
4. **User Control**:
   - Added a menu bar toggle: `✓ Auto-Stop on Silence (1.3s)` allowing users to toggle between hands-free auto-stop and manual continuous dictation.

### Consequences
- Single-click voice workflow: user clicks once, speaks, pauses, and text is automatically transcribed and injected without touching the mouse again.
- In noisy environments (e.g. loud music or heavy construction), the user can disable Auto-Stop via the menu bar item to fall back to manual toggle.


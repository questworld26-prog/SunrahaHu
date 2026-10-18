# Releases

## [1.1.0] - 2026-10-18

### Summary
Added **Silero Neural Voice Activity Detection (VAD) & Silence Auto-Stop**. Powered by the state-of-the-art Silero VAD v5 ONNX neural network, SunrahaHu reliably differentiates human voice from continuous background room noise (fans, air conditioners, laptop blowers) across both built-in laptop microphones and headphones.

### Highlights
- **Neural Speech & Silence Discrimination**:
  - Replaces fragile static energy thresholding with an acoustic deep-learning model (Silero VAD v5 via `onnxruntime`).
  - Immune to continuous fan or AC hiss: non-speech broadband noise evaluates to $< 0.03$ probability, while human voice triggers at $> 0.95$.
  - Automatically transitions to transcription upon detecting **1.3 seconds of trailing silence**.
- **Universal Microphone Compatibility**:
  - Operates reliably whether using MacBook built-in mics, AirPods, or external headphones without manual threshold calibration.
- **Micro-Latency on Apple Silicon**:
  - Executes single-frame inference in **0.11 ms** on CPU NEON threads, leaving the Metal GPU entirely dedicated to Whisper Large-V3-Turbo.
- **Architectural Documentation**:
  - Recorded migration rationale from RMS to Silero Neural VAD in [ADR-0002](file:///Users/prithis/QuestWorld/SunrahaHu/adr.md#adr-0002-native-rms-energy-voice-activity-detection-vad--silence-auto-stop) and [ADR-0003](file:///Users/prithis/QuestWorld/SunrahaHu/adr.md#adr-0003-silero-neural-voice-activity-detection-vad-via-onnx-runtime).
- **Test Coverage**:
  - Added dedicated test suite in `test_vad.py` testing pure silence, loud simulated fan noise rejection, and audio chunk boundaries (108 tests passing).

## [1.0.0] - 2026-10-18

### Summary
Milestone **1.0.0 production release** of **SunrahaHu (सुन रहा हूँ)** — high-speed background macOS dictation and hands-free voice automation utility powered by **Whisper Large-V3-Turbo** on Apple Silicon Metal GPU (`mlx-whisper`).

### Key Highlights & Features
- **Voice Commands & macOS Automation**:
  - Say **"Computer"**, **"Command"**, **"Suno"**, **"Hey Mac"**, or **"Jarvis"** followed by system actions (e.g., *"Computer switch to desktop 3"*, *"Jarvis switch to desktop 1"*).
  - Switches spaces instantly using macOS Quartz `Control + 1..9` HID event taps without elevated AppleScript permissions.
  - Automatic phonetic tolerance for Whisper mis-transcriptions (`service`, `java`, `travis`, homophones `to`/`too`/`for`, and ordinals `first`..`ninth`).
  - Spoken audio feedback cues (e.g. *"Switching to desktop 3"*) and alerts for out-of-range commands.
- **Robust macOS CoreAudio & Cocoa Stability**:
  - Eliminated CoreAudio HALC_IOThread mutex deadlocks with threaded stream teardown and timeouts.
  - Menu bar trigger actions now execute asynchronously to prevent Cocoa main UI thread blocking.
- **Multilingual & Roman Script Dictation**:
  - Auto-detect, English, Bengali (**বাংলা**), and Hindi (**हिन्दी**).
  - Trilingual Roman Script mode for natural code-switching without translation (*"Ami theek achi, aap batao what is the plan?"*).
- **Direct Quartz Unicode Typing**:
  - Injects transcribed text directly into active windows via `CGEventKeyboardSetUnicodeString`, leaving clipboard contents untouched.
- **Comprehensive Quality Assurance**:
  - 98 automated unit, edge case, and stress tests passing with 100% test fidelity.

## [0.5.1] - 2026-10-18

### Summary
Added **Roman Script (English + Hindi + Bengali)** dictation mode, allowing users who mix English, Hindi, and Bengali to have their speech transcribed phonetically in the English Latin alphabet without automatic translation.

### Highlights
- **Trilingual Roman Script Mode**: Configured prompt steering under `language="roman"` to transcribe mixed Bengali, Hindi, and English into Latin phonetic letters (e.g., *"Ami theek achi, aap batao what is the plan?"*) without translation.
- **Menu Bar Selection**: Added `Roman Script (English + Hindi + Bengali)` to the menu bar's language selector.
- **Comprehensive Testing**: Added dedicated unit tests and 10-message stress tests covering trilingual phonetic transcriptions.

## [0.5.0] - 2026-10-18

### Summary
Initial feature release of **SunrahaHu (सुन रहा हूँ)** — a lightweight background macOS voice dictation utility powered by **Whisper Large-V3-Turbo** and Apple Silicon's **MLX** framework.

### Highlights & Key Features
- **Apple Silicon Native Acceleration**: Uses `mlx-whisper` on Metal GPU with an ultra-lean memory footprint (~545 MB RAM), safely coexisting with Ollama and heavy developer environments on 8GB Macs.
- **Audio Voice Cue**: Speaks **"सुन रहा हूँ"** when triggered, with sequential mic opening to eliminate speaker audio bleed.
- **Active Window Text Injection**: Synthesizes `Cmd+V` via macOS `CGEvent` while preserving previous clipboard contents.
- **Configurable Global Hotkey**: Set to **`Cmd + Opt + .`** for quick, one-handed dictation toggle.
- **Menu Bar Status & Language Selector**: Clean macOS menu bar interface with real-time status indicators and support for Auto Detect, **বাংলা (Bengali)**, **हिन्दी (Hindi)**, and **English**.
- **Standardized Codebase**: Modern `src/` layout with full test suite (16 tests) passing under `pytest` and linted/formatted with `ruff`.

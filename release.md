# Releases

## [1.1.0] - 2026-10-18

### Summary
Added **Native RMS Voice Activity Detection (VAD) & Silence Auto-Stop**. Users no longer need to click "Stop Recording" — SunrahaHu automatically detects when you finish speaking, stops recording after **1.3 seconds of silence**, and immediately starts transcription and text injection or command execution.

### Highlights
- **Hands-Free Dictation ("Click once, speak, and forget")**:
  - Automatically transitions from recording to transcribing upon detecting 1.3s of trailing silence.
  - Zero extra dependencies: powered by native `numpy` Root Mean Square (RMS) energy thresholding (< 0.1% CPU).
  - Speech threshold (`RMS >= 0.012`, `min_duration=0.25s`) prevents premature triggers from keyboard clicks, coughing, or ambient noise.
  - Initial 6.0s grace period automatically aborts idle sessions if triggered unintentionally.
- **Menu Bar Control**:
  - Added `✓ Auto-Stop on Silence (1.3s)` menu item to toggle between hands-free auto-stop and manual continuous dictation.
- **Architectural Documentation**:
  - Documented design decisions, thresholds, and performance metrics in [ADR-0002](file:///Users/prithis/QuestWorld/SunrahaHu/adr.md).
- **Test Coverage**:
  - Added full test suite coverage for VAD speech transitions, trailing silence detection, initial timeout aborts, and menu toggles (104 tests passing).

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

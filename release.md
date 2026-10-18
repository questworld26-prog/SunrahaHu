# Releases

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

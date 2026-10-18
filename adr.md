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
   - Inject text using a clipboard-preserving `Cmd+V` simulation via macOS `Quartz.CGEvent` and `AppKit.NSPasteboard`.
   - Rationale: Ensures instantaneous pasting across third-party applications (VS Code, Cursor, Chrome, Slack, Terminal) without character drops or multi-line typing lag.
4. **Project Layout**:
   - Standardize on `src/sunrahahu` and `tests/` with `hatchling` and `uv` package management.
   - Enforce code hygiene using **Ruff** (`ruff check`, `ruff format`) and **Pytest**.
5. **Language Selection**:
   - Provide an explicit language picker in the Menu Bar (Auto Detect, বাংলা, हिन्दी, English).
   - Rationale: Bengali and Hindi phonetic overlap can cause Whisper's auto-detect to default to Devanagari script; explicit language tags lock tokenization to the intended script.

### Consequences
- Requires macOS Accessibility and Input Monitoring permissions to capture global hotkeys and synthesize paste keystrokes.
- Translation (`task="translate"`) is not supported by `whisper-large-v3-turbo` due to OpenAI architectural pruning; the application focuses on high-speed multilingual native-script transcription.

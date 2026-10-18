# AGENTS.md

Instructions, architecture guidelines, and operational constraints for AI agents working on the **SunrahaHu (सुन रहा हूँ)** codebase.

---

## 1. Project Overview

**SunrahaHu** is a lightweight, background macOS menu bar dictation utility running on Apple Silicon. It provides system-wide speech-to-text with near-zero latency, powered by **Whisper Large-V3-Turbo** via native Metal acceleration (`mlx-whisper`).

### Core Flow
1. **Trigger**: User clicks **"🎙️ Dictate (Toggle)"** in the macOS menu bar.
2. **Audio Cue**: Speaks **"सुन रहा हूँ"** synchronously *before* opening the microphone to avoid speaker audio bleed.
3. **Capture**: Records microphone audio at 16kHz float32 mono via `sounddevice`.
4. **Auto-Stop or Second Press**: Native RMS VAD automatically detects 1.3s of trailing silence and stops recording (or user clicks **"⏹️ Stop Recording"**). App announces **"Typing"** voice cue.
5. **Transcription**: Audio buffer is transcribed using `mlx-whisper` on Apple Silicon Metal GPU.
6. **Injection / Command**: Text is typed directly into the focused window via `Quartz.CGEventKeyboardSetUnicodeString`, or routed to Jarvis commands.

---

## 2. Critical Development Rules & Constraints

### ⚠️ Never Add Features Without Explicit User Confirmation
- **Do not introduce persistent logging or file persistence** unless explicitly requested and confirmed by the user.
- Consult the user before introducing new background services, telemetry, or storage formats.

### ⚠️ Always Use `uv run`
- Every command, script execution, lint check, format run, and test suite invocation **must use `uv run`**:
  ```bash
  uv run pytest
  uv run ruff check --fix .
  uv run ruff format .
  uv run sunrahahu
  ```

### ⚠️ macOS CoreAudio & Mutex Safety (`AudioRecorder`)
- **Never call `stream.stop()` on long macOS CoreAudio streams.** On macOS, `sounddevice.InputStream.stop()` deadlocks inside `HALC_IOThread::Entry` recursive mutexes.
- **Always use `stream.abort(ignore_errors=True)` followed by `stream.close(ignore_errors=True)`.**

### ⚠️ Whisper Large-V3-Turbo Capabilities & Steering
- **No `task="translate"`**: OpenAI pruned translation tokens when training Large-V3-Turbo. Turbo only supports `task="transcribe"`.
- **Multilingual Roman Script Mode (`language="roman"`)**: When the user speaks a mix of English, Hindi, and Bengali and wants English/Latin script without translation:
  - Route to `language="en"`.
  - Pass `initial_prompt=ROMAN_PHONETIC_PROMPT` containing phonetic Roman examples.

### ⚠️ Active Window Text Injection
- **Direct Unicode Typing**: Use `type_unicode_string()` in [`injector.py`](file:///Users/prithis/QuestWorld/SunrahaHu/src/sunrahahu/injector.py) via `CGEventKeyboardSetUnicodeString`. Do not rely on clipboard `Cmd+V` which can race against window server updates.
- Keep automatic trailing whitespace on typed strings for seamless continuous dictation.

### ⚠️ Thread Safety & macOS Cocoa RunLoop
- Status updates targeting `rumps` menu bar items from worker threads must be dispatched via `AppHelper.callAfter(callback)` to prevent Cocoa UI thread lockups.

---

## 3. Architecture & Directory Structure

```
SunrahaHu/
├── src/sunrahahu/
│   ├── app.py          # Central orchestrator: state machine, debounce locks, worker thread
│   ├── audio.py        # 16kHz audio capture with non-blocking abort stream cleanup
│   ├── commander.py    # Jarvis voice command router & macOS desktop space switching
│   ├── feedback.py     # Voice cues ("सुन रहा हूँ", "Typing", "Tink.aiff", command speech)
│   ├── hotkey.py       # Global keyboard listener using pynput
│   ├── injector.py     # Direct macOS Quartz CGEvent Unicode string typing
│   ├── main.py         # macOS menu bar app (rumps) & language selector
│   ├── transcriber.py  # mlx-whisper integration, RMS silence detection, Roman steering
│   └── vad.py          # Silero VAD v5 ONNX neural voice activity detection
├── tests/
│   ├── test_app.py         # State machine & toggle unit tests
│   ├── test_audio.py       # Audio recording & buffer concatenation
│   ├── test_commander.py   # Jarvis command parsing & desktop switching tests
│   ├── test_edge_cases.py  # Double start, rapid abort, disconnected mic, NaN audio
│   ├── test_feedback.py   # Voice cues & fallback speech
│   ├── test_injector.py   # Direct unicode injection & emoji support
│   ├── test_stress.py     # 10 sequential messages, variable duration (1s–12s), Roman script
│   ├── test_transcriber.py # Hallucination filtering, silent frames, Roman phonetic mode
│   └── test_vad.py         # Silero neural VAD chunk, fan noise, and speech tests
├── adr.md              # Architectural Decision Records
├── release.md          # Chronological release notes (latest on top)
├── pyproject.toml      # Project dependencies and tool configs (Ruff, Pytest)
└── AGENTS.md           # This agent guideline file
```

---

## 4. Verification Workflow

Before committing any changes:

1. **Run Linter and Formatter**:
   ```bash
   uv run ruff check --fix . && uv run ruff format .
   ```
2. **Run Pytest Suite**:
   ```bash
   uv run pytest
   ```
   *(Ensure all unit, edge case, and stress tests pass without warnings or hangs).*
3. **Check Git Status**:
   ```bash
   git status -s
   ```
4. **Preserve Release Log**:
   - Keep [`release.md`](file:///Users/prithis/QuestWorld/SunrahaHu/release.md) updated with the latest version at the top.

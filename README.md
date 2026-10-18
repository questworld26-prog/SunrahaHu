# SunrahaHu (सुन रहा हूँ) 🎙️

A lightweight, background macOS dictation application powered by **Whisper Large-V3-Turbo** and Apple Silicon's **MLX** framework.

Whenever you click **"🎙️ Dictate (Toggle)"** in the menu bar, SunrahaHu says **"सुन रहा हूँ"**, records your voice, transcribes it locally with near-zero latency, and automatically types the text directly into whichever application window currently has focus (e.g. Cursor, Chrome, Terminal, Slack, WhatsApp, Notes).

---

## ✨ Features

- **Apple Silicon Native**: Built on `mlx-whisper` using Metal GPU acceleration on Unified Memory.
- **Whisper Large-V3-Turbo**: High accuracy transcription running natively on Apple Silicon Metal GPU (~545MB RAM).
- **🌐 Language Selector**: Choose between **Auto Detect**, **Roman Script (English + Hindi + Bengali)**, **বাংলা (Bengali)**, **हिन्दी (Hindi)**, or **English** from the menu bar to ensure accurate script recognition.
- **Audio Voice Feedback**: Confirms with **"सुन रहा हूँ"** *before* opening the microphone so the voice prompt never bleeds into your dictation.
- **Direct Unicode Typing**: Uses macOS `CGEventKeyboardSetUnicodeString` to type text into active window directly without touching the clipboard.
- **Menu Bar App**: Clean macOS menu bar interface displaying current status (`🎙️ Idle`, `🔴 सुन रहा हूँ...`, `⚡ Transcribing...`).

---

## 🚀 Quick Start

Run the background menu bar app:

```bash
uv run sunrahahu
# Or:
uv run python -m sunrahahu.main
```

### Running Tests

```bash
uv run pytest -v
```

### Dictation Usage
1. Focus any text field in any app (Chrome, Terminal, Slack, Cursor, etc.).
2. Click **"🎙️ Dictate (Toggle)"** in the menu bar — you will hear **"सुन रहा हूँ"** and the menu bar turns red `🔴`.
3. Speak naturally.
4. Click **"⏹️ Stop Recording"** in the menu bar — Whisper transcribes and types the text directly into your focused window!

---

## 🔒 macOS Permissions Required
1. **Accessibility** (`System Settings -> Privacy & Security -> Accessibility`):
   - Grant permission to your terminal / Python so it can emulate the keystroke (`Cmd+V`) into other apps.
2. **Input Monitoring / Keystroke Receiving** (`System Settings -> Privacy & Security -> Input Monitoring`):
   - Needed for the global shortcut `Cmd+Shift+D` when running in the background.
3. **Microphone** (`System Settings -> Privacy & Security -> Microphone`):
   - Allow Python / Terminal to capture audio.

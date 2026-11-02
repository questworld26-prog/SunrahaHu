# SunrahaHu (सुन रहा हूँ) 🎙️

[![macOS Apple Silicon](https://img.shields.io/badge/Platform-macOS%20Apple%20Silicon%20(M1%2FM2%2FM3%2FM4)-black?logo=apple)](https://github.com/)
[![Python 3.13+](https://img.shields.io/badge/Python-3.13%2B-blue?logo=python)](https://www.python.org/)
[![MLX Whisper](https://img.shields.io/badge/Model-Whisper%20Large--V3--Turbo%20(MLX)-orange)](https://github.com/ml-explore/mlx-examples)
[![Silero VAD v5](https://img.shields.io/badge/VAD-Silero%20Neural%20VAD%20v5-green)](https://github.com/snakers4/silero-vad)
[![Code Style: Ruff](https://img.shields.io/badge/Code%20Style-Ruff-000000.svg)](https://github.com/astral-sh/ruff)
[![License: MIT](https://img.shields.io/badge/License-MIT-purple.svg)](LICENSE)

**SunrahaHu** (*"I am listening"*) is a fast, lightweight, and completely private background macOS menu bar dictation utility and voice command controller. Powered by **Whisper Large-V3-Turbo** running natively on Apple Silicon Metal GPU Unified Memory via **MLX**, and **Silero Neural VAD v5** running micro-latency inference on CPU NEON cores.

When triggered, SunrahaHu plays an audio confirmation (**"सुन रहा हूँ"**), captures your speech, auto-stops when you finish speaking, transcribes locally with near-zero latency, and automatically types the transcribed Unicode text directly into whichever application currently has focus (e.g., Cursor, VS Code, Chrome, Terminal, Slack, WhatsApp, Notes).

---

## ✨ Key Features

- **⚡ Native Apple Silicon Metal GPU Acceleration**: Built on `mlx-whisper` and Apple Silicon Unified Memory. High accuracy transcription running in **~545 MB RAM** (compared to >3 GB for legacy Whisper models), safely coexisting with local LLMs (Ollama) and IDEs on 8 GB+ machines.
- **🧠 Hands-Free Silero Neural VAD**: Integrates deep-learning Voice Activity Detection (Silero VAD v5 via ONNX Runtime). Formant-aware neural classification evaluates vocal tract frequencies rather than raw sound amplitude—completely immune to loud desk fans, air conditioners, or laptop cooling fans.
- **⏱️ "Click-Speak-and-Forget" Auto-Stop**: Automatically stops and transcribes after detecting **1.3 seconds of trailing silence**. No need to manually click "Stop".
- **🎧 Universal Bluetooth Headset & AirPods Support**: Dynamic PortAudio cache re-initialization and adaptive audio normalization. Seamlessly supports AirPods, Bluetooth headsets (HFP/SCO profiles), USB condenser microphones, and built-in MacBook array mics without audio dropouts or silence rejections.
- **🎤 Interactive Microphone Device Selector**: Switch input devices on-the-fly directly from the macOS menu bar without restarting the app.
- **🌐 Multilingual & Roman Script Mode**: Supports:
  - **Auto Detect**: Whisper detects language automatically.
  - **Roman Script (English + Hindi + Bengali)**: Trilingual phonetic Roman script transcription without translation (*"Ami theek achi, aap batao what is the plan?"*).
  - **বাংলা (Bengali)**: Native Eastern Nagari script.
  - **हिन्दी (Hindi)**: Native Devanagari script.
  - **English**: Clean Latin script.
- **⌨️ Direct Quartz Unicode Injection**: Types text directly into the focused window using macOS `Quartz.CGEventKeyboardSetUnicodeString`. Bypasses the macOS clipboard entirely, preventing clipboard overwrites and eliminating pasteboard race conditions.
- **🤖 Jarvis Voice Commands & macOS Spaces Navigation**: Voice automation for desktop space switching:
  - Say *"Computer switch to desktop 3"* or *"Jarvis move to space 2"*.
  - Dispatches native Quartz HID Control+1..9 space switching events with phonetic tolerance for Whisper speech variations.
- **🔊 Zero-Bleed Audio Feedback**: The **"सुन रहा हूँ"** audio prompt is played synchronously *before* opening the microphone stream, guaranteeing that the app's own voice prompt never bleeds into your dictation buffer. Announces a polite **"Typing"** voice cue during transcription.

---

## 🏗️ Architecture & Pipeline

```text
  [ User Clicks "🎙️ Dictate" ]
               │
               ▼
   [ Audio Cue: "सुन रहा हूँ" ]  (Plays synchronously before mic opens)
               │
               ▼
    [ CoreAudio 16kHz Stream ]   (PortAudio / sounddevice non-blocking stream)
               │
               ▼
     [ Silero Neural VAD ]       (ONNX Runtime evaluates 32ms frames; rejects fan/AC noise)
               │
    [ 1.3s Trailing Silence ]    (Hands-free auto-stop triggered)
               │
               ▼
  [ Audio Normalization & DC ]   (DC offset cancellation + low-gain scaling)
               │
               ▼
  [ Whisper Large-V3-Turbo ]     (mlx-whisper on Apple Silicon Metal GPU)
               │
         ┌─────┴────────────────┐
         ▼                      ▼
  [ Voice Command ]     [ General Dictation ]
   "Computer, go to      Direct Quartz Unicode typing
     desktop 3"          via CGEventKeyboardSetUnicodeString
         │                      │
         ▼                      ▼
  [ Quartz Ctrl+N ]     [ Injected into Focused App ]
```

---

## 📋 System Requirements

- **Operating System**: macOS 14.0 (Sonoma) or macOS 15.0+ (Sequoia)
- **Architecture**: Apple Silicon (M1, M2, M3, M4, Pro, Max, Ultra)
- **Python**: Version 3.13 or newer
- **Package Manager**: [`uv`](https://github.com/astral-sh/uv) (recommended) or `pip`

---

## 🔒 macOS Permissions Required

SunrahaHu requires standard macOS privacy permissions to capture audio and type into active windows. Configure these in **System Settings -> Privacy & Security**:

1. **Microphone**:
   - `System Settings -> Privacy & Security -> Microphone`
   - Grant permission to your terminal emulator (e.g., Terminal, iTerm2, Ghostty) or Python.
2. **Accessibility**:
   - `System Settings -> Privacy & Security -> Accessibility`
   - Grant permission to your terminal emulator or Python.
   - *Why*: Required by macOS Quartz to dispatch virtual keyboard events (`CGEventKeyboardSetUnicodeString`) into external focused windows and switch macOS Desktop Spaces via `Control + 1..9`.

---

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/SunrahaHu.git
cd SunrahaHu
```

### 2. Install Dependencies

Using `uv` (fastest and recommended):

```bash
uv sync
```

Alternatively, with standard `pip`:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

### 3. Launch SunrahaHu

```bash
uv run sunrahahu
# Or:
uv run python -m sunrahahu.main
```

A menu bar item titled **`🎙️ Idle`** will appear in your macOS status bar.

---

## 💡 How to Use

### Basic Dictation
1. Click into any text input in any app (Chrome, Terminal, Slack, Cursor, Notes, WhatsApp, etc.).
2. Click **"🎙️ Dictate (Toggle)"** in the menu bar.
3. SunrahaHu will play **"सुन रहा हूँ"**, and the menu bar status will update to **`🔴 सुन रहा हूँ...`**.
4. Speak naturally.
5. When you stop speaking for **1.3 seconds**, the Silero Neural VAD automatically stops the recording, plays a subtle **"Typing"** cue, transcribes your speech via Whisper Metal, and types the text into your focused window!
6. *Optional*: You can also manually click **"⏹️ Stop Recording"** at any time.

### Selecting Microphone
- Click **"🎤 Microphone"** in the menu bar to select an input device (e.g., Built-in MacBook Microphone, AirPods, external USB headset).
- If you plug or unplug a headset while the app is running, SunrahaHu automatically detects it, or you can click **"🔄 Refresh Devices"**.

### Selecting Language
- Click **"🌐 Language"** in the menu bar:
  - **Auto Detect**: Whisper infers spoken language on the fly.
  - **Roman Script (English + Hindi + Bengali)**: Phonetic Latin script without translation.
  - **বাংলা (Bengali)**: Direct Bengali script dictation.
  - **हिन्दी (Hindi)**: Direct Hindi script dictation.
  - **English**: English dictation.

---

## 🤖 Voice Commands (Desktop Space Navigation)

SunrahaHu includes a built-in command interpreter for hands-free macOS desktop navigation.

### Wake Prefixes
Start your sentence with any of:
- *"Computer ..."*
- *"Jarvis ..."*
- *"Hey Mac ..."*
- *"Command ..."*
- *"Suno ..."*

### Desktop Navigation Syntax
| Command | Action |
|:---|:---|
| *"Computer switch to desktop 3"* | Switches to macOS Desktop Space 3 |
| *"Jarvis go to workspace 1"* | Switches to macOS Desktop Space 1 |
| *"Hey Mac move to space 4"* | Switches to macOS Desktop Space 4 |
| *"Suno switch to desktop two"* | Switches to macOS Desktop Space 2 |
| *"Computer switch to the third desktop"* | Switches to macOS Desktop Space 3 |

> [!NOTE]
> Ensure **Mission Control** keyboard shortcuts (`Control + 1..9`) are enabled in:
> `System Settings -> Keyboard -> Keyboard Shortcuts... -> Mission Control -> Switch to Desktop 1..9`.

---

## 🛠️ Testing & Code Quality

The codebase maintains a rigorous test suite covering neural VAD inference, audio buffer concatenation, CoreAudio stream teardown, Jarvis command routing, edge cases, and multi-message stress tests.

### Running Unit & Edge-Case Tests

```bash
uv run pytest
```

### Running Stress Tests

```bash
uv run pytest -m stress -v
```

### Code Formatting & Static Analysis

SunrahaHu enforces strict Ruff compliance with zero warnings:

```bash
uv run ruff check .
uv run ruff format .
```

---

## 📁 Repository Structure

```text
SunrahaHu/
├── src/sunrahahu/
│   ├── __init__.py      # Package metadata and version definition
│   ├── app.py           # Core orchestrator: state machine, debounce locks, async worker
│   ├── audio.py         # 16kHz audio capture with non-blocking abort stream cleanup
│   ├── commander.py     # Jarvis voice command parser & macOS desktop space switching
│   ├── feedback.py      # Audio feedback ("सुन रहा हूँ", "Typing", "Tink", TTS)
│   ├── hotkey.py        # Global keyboard listener using pynput
│   ├── injector.py      # Direct macOS Quartz CGEvent Unicode string typing
│   ├── main.py          # macOS menu bar app (rumps) & language / device selector
│   ├── transcriber.py   # mlx-whisper integration, low-gain normalization, Roman steering
│   ├── vad.py           # Silero VAD v5 ONNX neural voice activity detection
│   └── assets/          # Neural ONNX model and short voice cue assets
├── tests/
│   ├── test_app.py          # State machine, auto-stop, and device selection tests
│   ├── test_audio.py        # Stream lifecycle and buffer concatenation tests
│   ├── test_commander.py    # Jarvis command parsing and key code verification
│   ├── test_edge_cases.py   # Rapid abort, double-start, mic disconnect tests
│   ├── test_feedback.py    # Audio cue execution and fallback tests
│   ├── test_injector.py    # Direct Quartz Unicode typing & astral plane tests
│   ├── test_main.py        # Menu bar UI and microphone switching tests
│   ├── test_stress.py      # Multi-duration variable length & trilingual stress tests
│   ├── test_transcriber.py  # Normalization, DC cancellation, silence filtering tests
│   └── test_vad.py          # Silero VAD fan noise rejection & speech chunk tests
├── adr.md               # Architectural Decision Records (ADR-0001 through ADR-0004)
├── release.md           # Chronological release notes and changelog
├── pyproject.toml       # Dependencies, packaging metadata, Ruff and Pytest configs
└── AGENTS.md            # Operational constraints and architecture guidelines
```

---

## 📖 Architectural Decision Records

Major engineering decisions are documented in [`adr.md`](adr.md):
- **[ADR-0001](adr.md#adr-0001-background-dictation-architecture--technology-stack)**: Background Dictation Architecture & Technology Stack (`mlx-whisper` Metal GPU, Quartz Unicode typing).
- **[ADR-0002](adr.md#adr-0002-native-rms-energy-voice-activity-detection-vad--silence-auto-stop)**: Native RMS Energy Voice Activity Detection (Superseded by ADR-0003).
- **[ADR-0003](adr.md#adr-0003-silero-neural-voice-activity-detection-vad-via-onnx-runtime)**: Silero Neural Voice Activity Detection (VAD) via ONNX Runtime.
- **[ADR-0004](adr.md#adr-0004-universal-bluetooth-headset--low-gain-microphone-compatibility)**: Universal Bluetooth Headset & Low-Gain Microphone Compatibility.

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).

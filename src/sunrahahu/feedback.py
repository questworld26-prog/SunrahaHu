"""Sound feedback utility for SunrahaHu."""

import os
import subprocess
import threading

AUDIO_DIR = os.path.join(os.path.dirname(__file__), "assets")
SUN_RAHA_HU_AUDIO = os.path.join(AUDIO_DIR, "sun_raha_hu.m4a")
TYPING_AUDIO = os.path.join(AUDIO_DIR, "typing.m4a")


# [spec: FDB-001]
def play_listening_cue(async_play: bool = True):
    """Play the 'सुन रहा हूँ' voice cue when recording starts."""

    def _play():
        if os.path.exists(SUN_RAHA_HU_AUDIO):
            subprocess.run(["afplay", SUN_RAHA_HU_AUDIO], check=False)
        else:
            # Fallback to macOS say with Lekha voice
            subprocess.run(["say", "-v", "Lekha", "सुन रहा हूँ"], check=False)

    if async_play:
        threading.Thread(target=_play, daemon=True).start()
    else:
        _play()


# [spec: FDB-001]
def play_typing_cue(async_play: bool = True):
    """Play the 'Typing' voice cue when recording stops and transcription/typing starts."""

    def _play():
        if os.path.exists(TYPING_AUDIO):
            subprocess.run(["afplay", TYPING_AUDIO], check=False)
        else:
            # Fallback to macOS say with Samantha voice
            subprocess.run(["say", "-v", "Samantha", "Typing"], check=False)

    if async_play:
        threading.Thread(target=_play, daemon=True).start()
    else:
        _play()


# [spec: FDB-001]
def play_done_cue(async_play: bool = True):
    """Play subtle system completion sound."""

    def _play():
        # Play subtle pop/tink sound
        sound_path = "/System/Library/Sounds/Tink.aiff"
        if os.path.exists(sound_path):
            subprocess.run(["afplay", sound_path], check=False)

    if async_play:
        threading.Thread(target=_play, daemon=True).start()
    else:
        _play()


# [spec: FDB-001]
def play_command_cue(message: str | None = None, async_play: bool = True):
    """Play spoken confirmation or sound for executed commands."""

    def _play():
        if message:
            subprocess.run(["say", "-v", "Samantha", message], check=False)
        else:
            play_done_cue(async_play=False)

    if async_play:
        threading.Thread(target=_play, daemon=True).start()
    else:
        _play()

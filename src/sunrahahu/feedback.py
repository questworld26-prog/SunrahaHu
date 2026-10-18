"""Sound feedback utility for SunrahaHu."""

import os
import subprocess
import threading

AUDIO_FILE = os.path.join(os.path.dirname(__file__), "assets", "sun_raha_hu.m4a")


def play_listening_cue(async_play: bool = True):
    """Play the 'सुन रहा हूँ' voice cue."""

    def _play():
        if os.path.exists(AUDIO_FILE):
            subprocess.run(["afplay", AUDIO_FILE], check=False)
        else:
            # Fallback to macOS say with Lekha voice
            subprocess.run(["say", "-v", "Lekha", "सुन रहा हूँ"], check=False)

    if async_play:
        threading.Thread(target=_play, daemon=True).start()
    else:
        _play()


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

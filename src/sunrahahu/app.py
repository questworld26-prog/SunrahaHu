"""Application core controller connecting hotkey, audio recording, Whisper transcription, and injection."""

import threading
import time

from sunrahahu.audio import AudioRecorder
from sunrahahu.commander import handle_command
from sunrahahu.feedback import play_done_cue, play_listening_cue, play_typing_cue
from sunrahahu.injector import inject_text_to_active_window
from sunrahahu.transcriber import Transcriber


class SunrahaHuApp:
    def __init__(self, on_status_change=None):
        self.auto_stop_enabled = True
        self.recorder = AudioRecorder(
            vad_enabled=self.auto_stop_enabled,
            on_silence_detected=self._on_auto_silence,
            on_initial_timeout=self._on_auto_timeout,
        )
        self.transcriber = Transcriber()
        self.on_status_change = on_status_change
        self.language = None  # None = Auto Detect, or 'bn', 'hi', 'en', 'roman'
        self.is_recording = False
        self.is_transcribing = False
        self.last_transcribed_text = ""
        self.lock = threading.Lock()

    def set_auto_stop(self, enabled: bool):
        """Enable or disable VAD auto-stop on silence."""
        self.auto_stop_enabled = enabled
        self.recorder.vad_enabled = enabled
        print(f"[SunrahaHu] Auto-stop on silence set to: {'Enabled (1.3s)' if enabled else 'Disabled'}")

    def _on_auto_silence(self):
        """Triggered automatically when trailing silence is detected after speech."""
        if not self.lock.acquire(blocking=False):
            return
        try:
            if self.is_recording and not self.is_transcribing:
                print("[SunrahaHu] Silence detected (1.3s). Auto-stopping...")
                self.stop_and_transcribe()
        finally:
            self.lock.release()

    def _on_auto_timeout(self):
        """Triggered if grace period elapsed; transcribes recorded audio so speech is never lost."""
        if not self.lock.acquire(blocking=False):
            return
        try:
            if self.is_recording and not self.is_transcribing:
                print("[SunrahaHu] Grace period elapsed. Stopping & transcribing...")
                self.stop_and_transcribe()
        finally:
            self.lock.release()

    def set_language(self, language: str = None):
        """Set language: None for Auto-detect, or 'bn', 'hi', 'en', 'roman'."""
        self.language = language
        print(f"[SunrahaHu] Spoken Language set to: {language or 'Auto Detect'}")

    def set_status(self, status: str):
        if self.on_status_change:
            try:
                self.on_status_change(status)
            except Exception as e:
                print(f"[Error updating status]: {e}")

    def toggle_recording(self):
        """
        Toggle recording on/off (press once to start, press again to finish & paste).
        Uses non-blocking lock to eliminate hotkey event queue deadlocks.
        """
        # If hotkey is bouncing or already busy, skip duplicate event
        if not self.lock.acquire(blocking=False):
            print("[SunrahaHu] Hotkey debounce: event already in progress.")
            return

        try:
            if not self.is_recording:
                if self.is_transcribing:
                    print("[SunrahaHu] Still transcribing previous audio, please wait...")
                    return
                self.start_recording()
            else:
                self.stop_and_transcribe()
        finally:
            self.lock.release()

    def start_recording(self):
        print("\n[SunrahaHu] Triggered: सुन रहा हूँ...")
        self.is_recording = True
        self.set_status("recording")
        # Play cue synchronously so mic doesn't capture the app's own prompt
        play_listening_cue(async_play=False)
        try:
            self.recorder.start()
        except Exception as e:
            print(f"[SunrahaHu Error] Microphone start failed: {e}")
            self.is_recording = False
            self.set_status("idle")

    def stop_and_transcribe(self):
        print("[SunrahaHu] Stopping recording & transcribing...")
        self.is_recording = False
        self.is_transcribing = True
        self.set_status("transcribing")
        # Announce "Typing" voice cue
        play_typing_cue(async_play=True)
        try:
            audio_data = self.recorder.stop()
        except Exception as e:
            print(f"[SunrahaHu Error] Stopping recorder failed: {e}")
            self.is_transcribing = False
            self.set_status("idle")
            return

        def _worker():
            try:
                start_time = time.time()
                text = self.transcriber.transcribe(audio_data, language=self.language)
                duration = time.time() - start_time
                print(f'[SunrahaHu] Result in {duration:.2f}s: "{text}"')

                if text:
                    self.last_transcribed_text = text
                    handled = handle_command(text)
                    if not handled:
                        inject_text_to_active_window(text)
                        play_done_cue(async_play=True)
                else:
                    print("[SunrahaHu] No speech detected or below silence threshold.")
            except Exception as e:
                print(f"[SunrahaHu] Transcription/Injection error: {e}")
            finally:
                self.is_transcribing = False
                self.set_status("idle")

        threading.Thread(target=_worker, daemon=True).start()

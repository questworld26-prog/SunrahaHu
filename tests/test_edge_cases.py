"""Comprehensive Senior Software Engineering Edge Cases Test Suite."""

from unittest.mock import MagicMock, patch

import numpy as np
import pytest

from sunrahahu.app import SunrahaHuApp
from sunrahahu.audio import AudioRecorder
from sunrahahu.injector import inject_text_to_active_window, type_unicode_string
from sunrahahu.transcriber import Transcriber


# -------------------------------------------------------------
# 1. Audio Recording Edge Cases
# -------------------------------------------------------------
# [verifies: AUD-001/AC-AUD-001.2]
def test_audio_recorder_double_start():
    """Edge Case: Double start() should safely close previous stream without leaking resources."""
    with patch("sounddevice.InputStream") as mock_stream_cls:
        first_stream = MagicMock()
        second_stream = MagicMock()
        mock_stream_cls.side_effect = [first_stream, second_stream]

        recorder = AudioRecorder()
        recorder.start()
        assert recorder.is_recording is True
        assert recorder.stream == first_stream

        # Second start without calling stop()
        recorder.start()
        first_stream.abort.assert_called_once()
        first_stream.close.assert_called_once()
        assert recorder.stream == second_stream


# [verifies: AUD-001/AC-AUD-001.3]
def test_audio_recorder_input_device_failure():
    """Edge Case: Microphone disconnected / permission denied exception handling."""
    with patch("sounddevice.InputStream", side_effect=RuntimeError("Microphone unplugged")):
        recorder = AudioRecorder()
        with pytest.raises(RuntimeError):
            recorder.start()
        assert recorder.is_recording is False
        assert recorder.stream is None


# -------------------------------------------------------------
# 2. Transcription Edge Cases & Hallucination Suppression
# -------------------------------------------------------------
# [verifies: STT-001/AC-STT-001.3]
def test_transcriber_pure_silence_rms_threshold():
    """Edge Case: Pure silence or flatline audio should be rejected early without running heavy MLX inference."""
    transcriber = Transcriber()
    # 2 seconds of pure zero amplitude
    silent_audio = np.zeros(16000 * 2, dtype=np.float32)

    with patch("mlx_whisper.transcribe") as mock_mlx:
        result = transcriber.transcribe(silent_audio)
        assert result == ""
        # Heavy MLX model should NOT even be called
        mock_mlx.assert_not_called()


# [verifies: STT-002/AC-STT-002.2]
def test_transcriber_whisper_hallucination_suppression():
    """Edge Case: Whisper frequently outputs repetitive 'Thank you.' on trailing ambient noise."""
    transcriber = Transcriber()
    # Generate low level noise that passes RMS check
    noisy_audio = np.sin(np.linspace(0, 100, 16000), dtype=np.float32) * 0.05

    for hallucination in ["Thank you.", "Thank you", "Thanks for watching!"]:
        with patch("mlx_whisper.transcribe", return_value={"text": hallucination}):
            result = transcriber.transcribe(noisy_audio)
            assert result == "", f"Failed to suppress hallucination: {hallucination}"


# [verifies: STT-002/AC-STT-002.3]
def test_transcriber_mlx_internal_crash_resilience():
    """Edge Case: MLX model throws unhandled C++ Metal out-of-memory or driver error."""
    transcriber = Transcriber()
    noisy_audio = np.sin(np.linspace(0, 100, 16000), dtype=np.float32) * 0.05

    with patch("mlx_whisper.transcribe", side_effect=RuntimeError("Metal GPU OOM")):
        result = transcriber.transcribe(noisy_audio)
        # Should gracefully return empty string and not crash the daemon
        assert result == ""


# -------------------------------------------------------------
# 3. Text Injection Edge Cases
# -------------------------------------------------------------
# [verifies: INJ-001/AC-INJ-001.2]
def test_injector_trailing_space_ergonomics():
    """Edge Case: Voice dictation should automatically append trailing space for continuous typing."""
    with patch("sunrahahu.injector.type_unicode_string") as mock_type:
        inject_text_to_active_window("Hello world")
        mock_type.assert_called_once_with("Hello world ")

    with patch("sunrahahu.injector.type_unicode_string") as mock_type:
        # If text already ends with whitespace/newline, do not append double spaces
        inject_text_to_active_window("Hello world\n")
        mock_type.assert_called_once_with("Hello world\n")


# [verifies: INJ-001/AC-INJ-001.1]
def test_injector_special_unicode_and_emojis():
    """Edge Case: Emojis, Bengali conjunct characters, and quotes must type cleanly without crashing."""
    complex_text = '🎉 নমস্কার! "How\'s it going?" 🚀'
    with patch("Quartz.CGEventPost") as mock_post, patch("Quartz.CGEventKeyboardSetUnicodeString") as mock_unicode:
        type_unicode_string(complex_text)
        assert mock_post.called
        assert mock_unicode.called


# -------------------------------------------------------------
# 4. App Lifecycle & Rapid Double Click Edge Cases
# -------------------------------------------------------------
# [verifies: APP-001/AC-APP-001.3]
def test_app_rapid_double_trigger():
    """Edge Case: User spamming hotkey while previous transcription is processing."""
    app = SunrahaHuApp()
    app.is_transcribing = True

    with patch.object(app, "start_recording") as mock_start, patch.object(app, "stop_and_transcribe") as mock_stop:
        app.toggle_recording()
        # Should ignore the trigger until current transcription finishes
        mock_start.assert_not_called()
        mock_stop.assert_not_called()
        assert app.is_transcribing is True
        assert app.is_recording is False


# [verifies: APP-001/AC-APP-001.5]
def test_app_mic_failure_cleans_status():
    """Edge Case: Microphone failure resets app state to idle rather than getting stuck."""
    status_updates = []
    app = SunrahaHuApp(on_status_change=lambda s: status_updates.append(s))

    with patch.object(app.recorder, "start", side_effect=RuntimeError("No mic found")):
        app.toggle_recording()

    assert app.is_recording is False
    assert status_updates[-1] == "idle"

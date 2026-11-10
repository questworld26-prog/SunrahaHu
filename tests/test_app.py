"""Tests for App orchestration."""

from unittest.mock import MagicMock, patch

import numpy as np

from sunrahahu.app import SunrahaHuApp


# [verifies: APP-001/AC-APP-001.1]
@patch("sunrahahu.app.play_listening_cue")
@patch("sunrahahu.app.AudioRecorder")
@patch("sunrahahu.app.Transcriber")
def test_app_start_recording(mock_transcriber_cls, mock_recorder_cls, mock_cue):
    mock_status_callback = MagicMock()
    app = SunrahaHuApp(on_status_change=mock_status_callback)

    app.toggle_recording()

    assert app.is_recording
    mock_cue.assert_called_once_with(async_play=False)
    app.recorder.start.assert_called_once()
    mock_status_callback.assert_called_with("recording")


# [verifies: APP-001/AC-APP-001.2]
@patch("sunrahahu.app.play_typing_cue")
@patch("sunrahahu.app.play_done_cue")
@patch("sunrahahu.app.inject_text_to_active_window")
@patch("sunrahahu.app.play_listening_cue")
@patch("sunrahahu.app.AudioRecorder")
@patch("sunrahahu.app.Transcriber")
def test_app_stop_and_transcribe(
    mock_transcriber_cls,
    mock_recorder_cls,
    mock_listening_cue,
    mock_inject,
    mock_done_cue,
    mock_typing_cue,
):
    mock_status_callback = MagicMock()
    app = SunrahaHuApp(on_status_change=mock_status_callback)

    # Start first
    app.toggle_recording()
    assert app.is_recording

    # Mock audio return and transcription
    fake_audio = np.ones(16000, dtype=np.float32)
    app.recorder.stop.return_value = fake_audio
    app.transcriber.transcribe.return_value = "Hello World"

    # Stop and trigger transcription worker
    with patch("threading.Thread") as mock_thread:
        # Intercept and run thread target directly for test determinism
        def run_target(target, daemon):
            target()
            return MagicMock()

        mock_thread.side_effect = run_target
        app.toggle_recording()

    app.recorder.stop.assert_called_once()
    app.transcriber.transcribe.assert_called_once_with(fake_audio, language=None)
    mock_typing_cue.assert_called_once_with(async_play=True)
    mock_inject.assert_called_once_with("Hello World")
    mock_done_cue.assert_called_once_with(async_play=True)
    mock_status_callback.assert_any_call("transcribing")
    mock_status_callback.assert_any_call("idle")


# [verifies: APP-001/AC-APP-001.2]
@patch("sunrahahu.app.play_typing_cue")
@patch("sunrahahu.app.play_done_cue")
@patch("sunrahahu.app.inject_text_to_active_window")
@patch("sunrahahu.app.play_listening_cue")
@patch("sunrahahu.app.AudioRecorder")
@patch("sunrahahu.app.Transcriber")
def test_app_language_selection(
    mock_transcriber_cls,
    mock_recorder_cls,
    mock_listening_cue,
    mock_inject,
    mock_done_cue,
    mock_typing_cue,
):
    app = SunrahaHuApp()
    app.set_language("bn")
    assert app.language == "bn"

    app.toggle_recording()
    fake_audio = np.ones(16000, dtype=np.float32)
    app.recorder.stop.return_value = fake_audio
    app.transcriber.transcribe.return_value = "হ্যালো বোব"

    with patch("threading.Thread") as mock_thread:

        def run_target(target, daemon):
            target()
            return MagicMock()

        mock_thread.side_effect = run_target
        app.toggle_recording()

    app.transcriber.transcribe.assert_called_once_with(fake_audio, language="bn")
    mock_inject.assert_called_once_with("হ্যালো বোব")


# [verifies: APP-001/AC-APP-001.2]
@patch("sunrahahu.app.handle_command", return_value=True)
@patch("sunrahahu.app.play_typing_cue")
@patch("sunrahahu.app.play_done_cue")
@patch("sunrahahu.app.inject_text_to_active_window")
@patch("sunrahahu.app.play_listening_cue")
@patch("sunrahahu.app.AudioRecorder")
@patch("sunrahahu.app.Transcriber")
def test_app_jarvis_command_flow(
    mock_transcriber_cls,
    mock_recorder_cls,
    mock_listening_cue,
    mock_inject,
    mock_done_cue,
    mock_typing_cue,
    mock_handle_cmd,
):
    app = SunrahaHuApp()
    app.toggle_recording()

    fake_audio = np.ones(16000, dtype=np.float32)
    app.recorder.stop.return_value = fake_audio
    app.transcriber.transcribe.return_value = "Jarvis switch to desktop 3"

    with patch("threading.Thread") as mock_thread:

        def run_target(target, daemon):
            target()
            return MagicMock()

        mock_thread.side_effect = run_target
        app.toggle_recording()

    mock_handle_cmd.assert_called_once_with("Jarvis switch to desktop 3")
    mock_inject.assert_not_called()
    mock_done_cue.assert_not_called()


# [verifies: APP-001/AC-APP-001.4]
@patch("sunrahahu.app.AudioRecorder")
@patch("sunrahahu.app.Transcriber")
def test_app_auto_silence(mock_transcriber_cls, mock_recorder_cls):
    app = SunrahaHuApp()
    app.is_recording = True
    app.stop_and_transcribe = MagicMock()

    app._on_auto_silence()

    app.stop_and_transcribe.assert_called_once()


# [verifies: APP-001/AC-APP-001.4]
@patch("sunrahahu.app.AudioRecorder")
@patch("sunrahahu.app.Transcriber")
def test_app_auto_timeout(mock_transcriber_cls, mock_recorder_cls):
    app = SunrahaHuApp()
    app.is_recording = True
    app.stop_and_transcribe = MagicMock()

    app._on_auto_timeout()

    app.stop_and_transcribe.assert_called_once()


# [verifies: APP-001/AC-APP-001.1]
def test_app_set_auto_stop():
    app = SunrahaHuApp()
    assert app.auto_stop_enabled is True
    assert app.recorder.vad_enabled is True

    app.set_auto_stop(False)
    assert app.auto_stop_enabled is False
    assert app.recorder.vad_enabled is False


# [verifies: APP-001/AC-APP-001.1]
def test_app_set_device():
    app = SunrahaHuApp()
    assert app.selected_device is None
    assert app.recorder.device is None

    app.set_device(3)
    assert app.selected_device == 3
    assert app.recorder.device == 3

    app.set_device(None)
    assert app.selected_device is None
    assert app.recorder.device is None

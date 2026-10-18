"""Tests for AudioRecorder."""

from unittest.mock import MagicMock, patch

import numpy as np

from sunrahahu.audio import AudioRecorder


def test_audio_recorder_init():
    recorder = AudioRecorder(sample_rate=16000, channels=1)
    assert recorder.sample_rate == 16000
    assert recorder.channels == 1
    assert not recorder.is_recording
    assert recorder.stream is None


@patch("sounddevice.InputStream")
def test_audio_recorder_start_stop(mock_input_stream):
    mock_stream_instance = MagicMock()
    mock_input_stream.return_value = mock_stream_instance

    recorder = AudioRecorder(sample_rate=16000, channels=1)
    recorder.start()

    assert recorder.is_recording
    mock_input_stream.assert_called_once()
    mock_stream_instance.start.assert_called_once()

    # Simulate callback receiving audio frames
    frame1 = np.ones((1600, 1), dtype=np.float32)
    frame2 = np.ones((1600, 1), dtype=np.float32) * 2
    recorder._callback(frame1, 1600, None, None)
    recorder._callback(frame2, 1600, None, None)

    # Stop recording
    result = recorder.stop()

    assert not recorder.is_recording
    mock_stream_instance.abort.assert_called_once()
    mock_stream_instance.close.assert_called_once()
    assert isinstance(result, np.ndarray)
    assert len(result) == 3200
    assert result[0] == 1.0
    assert result[1600] == 2.0


def test_audio_recorder_empty_stop():
    recorder = AudioRecorder()
    result = recorder.stop()
    assert isinstance(result, np.ndarray)
    assert len(result) == 0


def test_audio_recorder_vad_silence_detection():
    mock_silence_cb = MagicMock()
    # Configure with small durations for fast test execution
    recorder = AudioRecorder(
        sample_rate=16000,
        channels=1,
        vad_enabled=True,
        speech_threshold=0.012,
        silence_threshold=0.006,
        silence_duration=0.1,  # 1600 frames
        min_speech_duration=0.05,  # 800 frames
        on_silence_detected=mock_silence_cb,
    )
    recorder.is_recording = True

    # 1. Speech frame (RMS ~0.05, 1000 frames)
    speech_frame = (np.sin(np.linspace(0, 100, 1000)) * 0.05).astype(np.float32).reshape(-1, 1)
    recorder._callback(speech_frame, 1000, None, None)
    assert recorder.has_speech_started is True
    mock_silence_cb.assert_not_called()

    # 2. Silence frame under threshold (RMS ~0.001, 1600 frames >= 1600 frames threshold)
    with patch("threading.Thread") as mock_thread:

        def run_target(target, daemon):
            target()
            return MagicMock()

        mock_thread.side_effect = run_target

        silence_frame = np.full((1600, 1), 0.001, dtype=np.float32)
        recorder._callback(silence_frame, 1600, None, None)

    mock_silence_cb.assert_called_once()
    assert recorder.vad_triggered is True


def test_audio_recorder_vad_initial_timeout():
    mock_timeout_cb = MagicMock()
    recorder = AudioRecorder(
        sample_rate=16000,
        channels=1,
        vad_enabled=True,
        max_initial_silence=0.1,  # 1600 frames
        on_initial_timeout=mock_timeout_cb,
    )
    recorder.is_recording = True

    with patch("threading.Thread") as mock_thread:

        def run_target(target, daemon):
            target()
            return MagicMock()

        mock_thread.side_effect = run_target

        silence_frame = np.full((1600, 1), 0.001, dtype=np.float32)
        recorder._callback(silence_frame, 1600, None, None)

    mock_timeout_cb.assert_called_once()
    assert recorder.vad_triggered is True


def test_audio_recorder_vad_disabled():
    mock_silence_cb = MagicMock()
    recorder = AudioRecorder(
        sample_rate=16000,
        channels=1,
        vad_enabled=False,
        silence_duration=0.1,
        min_speech_duration=0.05,
        on_silence_detected=mock_silence_cb,
    )
    recorder.is_recording = True

    speech_frame = (np.sin(np.linspace(0, 100, 1000)) * 0.05).astype(np.float32).reshape(-1, 1)
    recorder._callback(speech_frame, 1000, None, None)

    silence_frame = np.full((2000, 1), 0.001, dtype=np.float32)
    recorder._callback(silence_frame, 2000, None, None)

    mock_silence_cb.assert_not_called()

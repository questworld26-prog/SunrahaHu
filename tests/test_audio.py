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
    recorder = AudioRecorder(
        sample_rate=16000,
        channels=1,
        vad_enabled=True,
        silence_duration=0.1,  # 1600 frames
        min_speech_duration=0.05,  # 800 frames
        on_silence_detected=mock_silence_cb,
    )
    recorder.is_recording = True
    recorder.vad = MagicMock()

    # 1. Speech chunks (512 samples each, returns is_speech=True)
    recorder.vad.is_speech.return_value = (True, 0.95)
    speech_frame = np.ones((1024, 1), dtype=np.float32)
    recorder._callback(speech_frame, 1024, None, None)
    assert recorder.has_speech_started is True
    mock_silence_cb.assert_not_called()

    # 2. Silence chunks (512 samples each, returns is_speech=False)
    recorder.vad.is_speech.return_value = (False, 0.01)
    with patch("threading.Thread") as mock_thread:

        def run_target(target, daemon):
            target()
            return MagicMock()

        mock_thread.side_effect = run_target

        silence_frame = np.zeros((2048, 1), dtype=np.float32)
        recorder._callback(silence_frame, 2048, None, None)

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
    recorder.vad = MagicMock()
    recorder.vad.is_speech.return_value = (False, 0.01)

    with patch("threading.Thread") as mock_thread:

        def run_target(target, daemon):
            target()
            return MagicMock()

        mock_thread.side_effect = run_target

        silence_frame = np.zeros((2048, 1), dtype=np.float32)
        recorder._callback(silence_frame, 2048, None, None)

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
    recorder.vad = MagicMock()
    recorder.vad.is_speech.return_value = (True, 0.95)

    speech_frame = np.ones((1024, 1), dtype=np.float32)
    recorder._callback(speech_frame, 1024, None, None)

    recorder.vad.is_speech.return_value = (False, 0.01)
    silence_frame = np.zeros((2048, 1), dtype=np.float32)
    recorder._callback(silence_frame, 2048, None, None)

    mock_silence_cb.assert_not_called()

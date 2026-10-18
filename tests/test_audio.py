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
    mock_stream_instance.stop.assert_called_once()
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

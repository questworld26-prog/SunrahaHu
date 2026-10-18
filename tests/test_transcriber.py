"""Tests for Transcriber."""

from unittest.mock import patch

import numpy as np

from sunrahahu.transcriber import MODEL_NAME, Transcriber


def test_transcriber_init():
    transcriber = Transcriber()
    assert transcriber.model_name == MODEL_NAME


def test_transcriber_empty_audio():
    transcriber = Transcriber()
    assert transcriber.transcribe(None) == ""
    assert transcriber.transcribe(np.array([], dtype=np.float32)) == ""


def test_transcriber_too_short_audio():
    transcriber = Transcriber()
    # 0.2s of audio is under the 0.4s threshold
    short_audio = np.zeros(16000 // 5, dtype=np.float32)
    assert transcriber.transcribe(short_audio) == ""


@patch("mlx_whisper.transcribe")
def test_transcriber_successful(mock_mlx_transcribe):
    mock_mlx_transcribe.return_value = {"text": "  नमस्ते, यह एक टेस्ट है।  "}
    transcriber = Transcriber()

    # 1 second of audio
    audio = np.zeros(16000, dtype=np.float32)
    result = transcriber.transcribe(audio, language="hi")

    assert result == "नमस्ते, यह एक टेस्ट है।"
    mock_mlx_transcribe.assert_called_once_with(audio, path_or_hf_repo=MODEL_NAME, task="transcribe", language="hi")


@patch("mlx_whisper.transcribe")
def test_transcriber_translate(mock_mlx_transcribe):
    mock_mlx_transcribe.return_value = {"text": "Hello, this is a test."}
    transcriber = Transcriber()

    # 1 second of audio
    audio = np.zeros(16000, dtype=np.float32)
    result = transcriber.transcribe(audio, task="translate")

    assert result == "Hello, this is a test."
    mock_mlx_transcribe.assert_called_once_with(audio, path_or_hf_repo=MODEL_NAME, task="translate")

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

    # 1 second of non-silent audio
    audio = np.sin(np.linspace(0, 100, 16000), dtype=np.float32) * 0.1
    result = transcriber.transcribe(audio, language="hi")

    assert result == "नमस्ते, यह एक टेस्ट है।"
    assert mock_mlx_transcribe.call_count == 1
    _, kwargs = mock_mlx_transcribe.call_args
    assert kwargs["path_or_hf_repo"] == MODEL_NAME
    assert kwargs["task"] == "transcribe"
    assert kwargs["language"] == "hi"
    assert kwargs["no_speech_threshold"] == 0.6


@patch("mlx_whisper.transcribe")
def test_transcriber_translate(mock_mlx_transcribe):
    mock_mlx_transcribe.return_value = {"text": "Hello, this is a test."}
    transcriber = Transcriber()

    # 1 second of non-silent audio
    audio = np.sin(np.linspace(0, 100, 16000), dtype=np.float32) * 0.1
    result = transcriber.transcribe(audio, task="translate")

    assert result == "Hello, this is a test."
    assert mock_mlx_transcribe.call_count == 1
    _, kwargs = mock_mlx_transcribe.call_args
    assert kwargs["path_or_hf_repo"] == MODEL_NAME
    assert kwargs["task"] == "translate"
    assert kwargs["no_speech_threshold"] == 0.6


@patch("mlx_whisper.transcribe")
def test_transcriber_roman_script(mock_mlx_transcribe):
    """Verifies that 'roman' language mode routes to language='en' with phonetic steering prompt."""
    mock_mlx_transcribe.return_value = {"text": "Ami theek achi, aap batao what is the plan? Ei project ta khub bhalo."}
    transcriber = Transcriber()

    audio = np.sin(np.linspace(0, 100, 16000), dtype=np.float32) * 0.1
    result = transcriber.transcribe(audio, language="roman")

    assert result == "Ami theek achi, aap batao what is the plan? Ei project ta khub bhalo."
    assert mock_mlx_transcribe.call_count == 1
    _, kwargs = mock_mlx_transcribe.call_args
    assert kwargs["language"] == "en"
    assert kwargs["task"] == "transcribe"
    assert "English Latin alphabet" in kwargs["initial_prompt"]
    assert "Bengali" in kwargs["initial_prompt"]
    assert "Hindi" in kwargs["initial_prompt"]

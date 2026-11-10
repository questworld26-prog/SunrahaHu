"""Tests for Audio Feedback."""

from unittest.mock import patch

from sunrahahu.feedback import (
    play_command_cue,
    play_done_cue,
    play_listening_cue,
    play_typing_cue,
)


# [verifies: FDB-001/AC-FDB-001.1]
@patch("subprocess.run")
def test_play_listening_cue_file(mock_run):
    with patch("os.path.exists", return_value=True):
        play_listening_cue(async_play=False)
        mock_run.assert_called_once()
        assert "afplay" in mock_run.call_args[0][0]


# [verifies: FDB-001/AC-FDB-001.5]
@patch("subprocess.run")
def test_play_listening_cue_fallback(mock_run):
    with patch("os.path.exists", return_value=False):
        play_listening_cue(async_play=False)
        mock_run.assert_called_once()
        args = mock_run.call_args[0][0]
        assert "say" in args
        assert "Lekha" in args


# [verifies: FDB-001/AC-FDB-001.2]
@patch("subprocess.run")
def test_play_typing_cue_file(mock_run):
    with patch("os.path.exists", return_value=True):
        play_typing_cue(async_play=False)
        mock_run.assert_called_once()
        assert "afplay" in mock_run.call_args[0][0]


# [verifies: FDB-001/AC-FDB-001.5]
@patch("subprocess.run")
def test_play_typing_cue_fallback(mock_run):
    with patch("os.path.exists", return_value=False):
        play_typing_cue(async_play=False)
        mock_run.assert_called_once()
        args = mock_run.call_args[0][0]
        assert "say" in args
        assert "Samantha" in args


# [verifies: FDB-001/AC-FDB-001.3]
@patch("subprocess.run")
def test_play_done_cue(mock_run):
    with patch("os.path.exists", return_value=True):
        play_done_cue(async_play=False)
        mock_run.assert_called_once()
        assert "afplay" in mock_run.call_args[0][0]


# [verifies: FDB-001/AC-FDB-001.4]
@patch("subprocess.run")
def test_play_command_cue_speech(mock_run):
    play_command_cue("Switching to desktop 3", async_play=False)
    mock_run.assert_called_once()
    args = mock_run.call_args[0][0]
    assert "say" in args
    assert "Switching to desktop 3" in args


# [verifies: FDB-001/AC-FDB-001.4]
@patch("subprocess.run")
def test_play_command_cue_sound(mock_run):
    with patch("os.path.exists", return_value=True):
        play_command_cue(None, async_play=False)
        mock_run.assert_called_once()
        assert "afplay" in mock_run.call_args[0][0]

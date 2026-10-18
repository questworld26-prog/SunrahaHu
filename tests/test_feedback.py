"""Tests for Audio Feedback."""

from unittest.mock import patch

from sunrahahu.feedback import play_done_cue, play_listening_cue


@patch("subprocess.run")
def test_play_listening_cue_file(mock_run):
    with patch("os.path.exists", return_value=True):
        play_listening_cue(async_play=False)
        mock_run.assert_called_once()
        assert "afplay" in mock_run.call_args[0][0]


@patch("subprocess.run")
def test_play_listening_cue_fallback(mock_run):
    with patch("os.path.exists", return_value=False):
        play_listening_cue(async_play=False)
        mock_run.assert_called_once()
        args = mock_run.call_args[0][0]
        assert "say" in args
        assert "Lekha" in args


@patch("subprocess.run")
def test_play_done_cue(mock_run):
    with patch("os.path.exists", return_value=True):
        play_done_cue(async_play=False)
        mock_run.assert_called_once()
        assert "afplay" in mock_run.call_args[0][0]

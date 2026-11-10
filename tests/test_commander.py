"""Tests for Jarvis Commander and macOS Desktop Space Switching."""

from unittest.mock import MagicMock, patch

import pytest

from sunrahahu.commander import (
    DESKTOP_KEYCODES,
    handle_command,
    is_jarvis_command,
    parse_command,
    parse_desktop_number,
    strip_jarvis_prefix,
    switch_to_desktop,
)


# [verifies: CMD-001/AC-CMD-001.1]
@pytest.mark.parametrize(
    "text,expected",
    [
        ("Jarvis switch to desktop 3", True),
        ("jarvis, switch to desktop 1", True),
        ("JARVIS go to desktop 2", True),
        ("service switch to desktop one", True),
        ("Java switch to desktop 3", True),
        ("travis switch to desktop 2", True),
        ("Computer switch to desktop 1", True),
        ("command switch to desktop 4", True),
        ("suno switch to desktop 2", True),
        ("Hey Mac switch to desktop 3", True),
        ("Jarvis: move to workspace 4", True),
        ("jarvis desktop 5", True),
        ("Jarvis", True),
        ("Jarvis!", True),
        ("Hello Jarvis", False),
        ("Switch to desktop 3", False),
        ("Just dictating text", False),
        ("", False),
    ],
)
# [verifies: CMD-001/AC-CMD-001.1]
def test_is_jarvis_command(text, expected):
    """[verifies: CMD-001/AC-CMD-001.1]"""
    assert is_jarvis_command(text) == expected


# [verifies: CMD-001/AC-CMD-001.2]
@pytest.mark.parametrize(
    "text,expected",
    [
        ("Jarvis switch to desktop 3", "switch to desktop 3"),
        ("jarvis, switch to desktop 1.", "switch to desktop 1."),
        ("service switch to desktop one", "switch to desktop one"),
        ("Java switch to desktop 3", "switch to desktop 3"),
        ("Computer switch to desktop 2", "switch to desktop 2"),
        ("Command switch to desktop 4", "switch to desktop 4"),
        ("Suno switch to desktop 1", "switch to desktop 1"),
        ("Hey Mac switch to desktop 3", "switch to desktop 3"),
        ("JARVIS: go to space 2", "go to space 2"),
        ("Jarvis", ""),
    ],
)
# [verifies: CMD-001/AC-CMD-001.2]
def test_strip_jarvis_prefix(text, expected):
    """[verifies: CMD-001/AC-CMD-001.2]"""
    assert strip_jarvis_prefix(text) == expected


# [verifies: CMD-001/AC-CMD-001.3]
@pytest.mark.parametrize(
    "phrase,expected_num",
    [
        ("switch to desktop 3", 3),
        ("switch to desktop 1", 1),
        ("switch to desktop 9", 9),
        ("switch to desktop three", 3),
        ("switch to desktop one", 1),
        ("switch to desktop nine", 9),
        ("go to desktop 2", 2),
        ("move to desktop 4", 4),
        ("jump to workspace 5", 5),
        ("switch to workspace 6", 6),
        ("switch to space 7", 7),
        ("desktop 8", 8),
        ("workspace 2", 2),
        ("space 1", 1),
        ("switch to desktop number 3", 3),
        ("switch to the third desktop", 3),
        ("switch to the 3rd desktop", 3),
        ("switch to third desktop", 3),
        ("go to second workspace", 2),
        ("switch to desktop to", 2),
        ("switch to desktop too", 2),
        ("switch to desktop for", 4),
        ("switch to desktop first", 1),
        ("switch to desktop 10", 10),
        ("turn up the volume", None),
        ("hello world", None),
    ],
)
# [verifies: CMD-001/AC-CMD-001.3]
def test_parse_desktop_number(phrase, expected_num):
    """[verifies: CMD-001/AC-CMD-001.3]"""
    assert parse_desktop_number(phrase) == expected_num


# [verifies: CMD-001/AC-CMD-001.3]
def test_parse_command_valid():
    action, arg = parse_command("Jarvis switch to desktop 3")
    assert action == "switch_desktop"
    assert arg == 3

    action, arg = parse_command("Jarvis, switch to desktop 1.")
    assert action == "switch_desktop"
    assert arg == 1


# [verifies: CMD-001/AC-CMD-001.4]
def test_parse_command_unrecognized():
    action, arg = parse_command("Jarvis do something unknown")
    assert action is None
    assert arg is None


# [verifies: CMD-002/AC-CMD-002.1]
@patch("Quartz.CGEventPost")
@patch("Quartz.CGEventSetFlags")
@patch("Quartz.CGEventCreateKeyboardEvent")
def test_switch_to_desktop_valid(mock_create_event, mock_set_flags, mock_post_event):
    mock_event = MagicMock()
    mock_create_event.return_value = mock_event

    for num in range(1, 10):
        mock_create_event.reset_mock()
        mock_set_flags.reset_mock()
        mock_post_event.reset_mock()

        success = switch_to_desktop(num)
        assert success is True
        expected_code = DESKTOP_KEYCODES[num]

        # Key down & Key up
        assert mock_create_event.call_count == 2
        assert mock_create_event.call_args_list[0].args == (None, expected_code, True)
        assert mock_create_event.call_args_list[1].args == (None, expected_code, False)

        assert mock_post_event.call_count == 2


# [verifies: CMD-002/AC-CMD-002.2]
def test_switch_to_desktop_invalid_number():
    assert switch_to_desktop(0) is False
    assert switch_to_desktop(10) is False
    assert switch_to_desktop(-1) is False


# [verifies: CMD-002/AC-CMD-002.1]
@patch("sunrahahu.commander.play_command_cue")
@patch("sunrahahu.commander.switch_to_desktop", return_value=True)
def test_handle_command_success(mock_switch, mock_cue):
    result = handle_command("Jarvis switch to desktop 3")
    assert result is True
    mock_switch.assert_called_once_with(3)
    mock_cue.assert_called_once_with("Switching to desktop 3", async_play=True)


# [verifies: CMD-002/AC-CMD-002.2]
@patch("sunrahahu.commander.play_command_cue")
@patch("sunrahahu.commander.switch_to_desktop")
def test_handle_command_out_of_bounds(mock_switch, mock_cue):
    result = handle_command("Jarvis switch to desktop 12")
    assert result is True
    mock_switch.assert_not_called()
    mock_cue.assert_called_once_with("Desktop number must be between 1 and 9", async_play=True)


# [verifies: CMD-002/AC-CMD-002.3]
@patch("sunrahahu.commander.play_command_cue")
@patch("sunrahahu.commander.switch_to_desktop")
def test_handle_command_unrecognized(mock_switch, mock_cue):
    result = handle_command("Jarvis sing a song")
    assert result is True
    mock_switch.assert_not_called()
    mock_cue.assert_called_once_with("Command not recognized", async_play=True)


# [verifies: CMD-002/AC-CMD-002.4]
def test_handle_command_non_command():
    result = handle_command("Today is a wonderful sunny day")
    assert result is False

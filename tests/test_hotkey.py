"""Tests for Global Hotkey Listener."""

from unittest.mock import MagicMock, patch

from sunrahahu.hotkey import HotkeyListener


# [verifies: HKY-001/AC-HKY-001.1]
@patch("pynput.keyboard.GlobalHotKeys")
def test_hotkey_listener_start(mock_global_hotkeys):
    """Verify that start initializes and starts GlobalHotKeys."""
    mock_instance = MagicMock()
    mock_global_hotkeys.return_value = mock_instance

    callback = MagicMock()
    listener = HotkeyListener("<cmd>+<shift>+d", callback)
    listener.start()

    mock_global_hotkeys.assert_called_once_with({"<cmd>+<shift>+d": callback})
    mock_instance.start.assert_called_once()
    assert listener.listener is mock_instance


# [verifies: HKY-001/AC-HKY-001.2]
@patch("pynput.keyboard.GlobalHotKeys")
def test_hotkey_listener_stop(mock_global_hotkeys):
    """Verify that stop stops GlobalHotKeys and resets reference to None."""
    mock_instance = MagicMock()
    mock_global_hotkeys.return_value = mock_instance

    callback = MagicMock()
    listener = HotkeyListener("<cmd>+<shift>+d", callback)
    listener.start()
    listener.stop()

    mock_instance.stop.assert_called_once()
    assert listener.listener is None

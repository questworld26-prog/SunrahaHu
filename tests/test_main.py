"""Tests for macOS menu bar application."""

from unittest.mock import patch

from sunrahahu.main import SunrahaHuMenuBar


def test_menu_bar_init():
    """Verify SunrahaHuMenuBar instantiates cleanly without rumps menu exceptions."""
    app = SunrahaHuMenuBar()
    assert app is not None
    assert app.mic_menu is not None
    assert len(app.mic_menu) > 0


@patch("sounddevice.query_devices")
@patch("sounddevice.default")
def test_menu_bar_microphone_selection(mock_default, mock_query):
    mock_query.return_value = [
        {"name": "MacBook Air Microphone", "max_input_channels": 1},
        {"name": "Bread Headset", "max_input_channels": 1},
    ]
    mock_default.device = [0, 1]

    app = SunrahaHuMenuBar()
    app.refresh_microphones()

    assert app.app_core.selected_device is None

    # Switch to device index 1
    app.select_microphone(1, None)
    assert app.app_core.selected_device == 1

    # Switch back to default
    app.select_microphone(None, None)
    assert app.app_core.selected_device is None

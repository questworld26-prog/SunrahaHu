"""Tests for Active Window Injector."""

from unittest.mock import MagicMock, patch

from sunrahahu.injector import inject_text_to_active_window, type_unicode_string


def test_inject_text_empty():
    with patch("sunrahahu.injector.type_unicode_string") as mock_type:
        inject_text_to_active_window("")
        mock_type.assert_not_called()


@patch("Quartz.CGEventPost")
@patch("Quartz.CGEventKeyboardSetUnicodeString")
@patch("Quartz.CGEventCreateKeyboardEvent")
def test_type_unicode_string(mock_create_event, mock_set_unicode, mock_post_event):
    type_unicode_string("হ্যালো World")
    mock_create_event.assert_called()
    mock_set_unicode.assert_called()
    mock_post_event.assert_called()


@patch("sunrahahu.injector.type_unicode_string")
def test_inject_text_direct_default(mock_type):
    inject_text_to_active_window("New transcribed text")
    mock_type.assert_called_once_with("New transcribed text ")


@patch("sunrahahu.injector.post_cmd_v")
@patch("sunrahahu.injector.get_pasteboard")
def test_inject_text_clipboard_flow(
    mock_get_pb,
    mock_post_cmd_v,
):
    mock_pb = MagicMock()
    mock_pb.stringForType_.return_value = "original_clipboard_text"
    mock_get_pb.return_value = mock_pb

    inject_text_to_active_window("New transcribed dictation", method="paste")

    # 1. Backed up old clipboard
    mock_pb.stringForType_.assert_called_once()

    # 2. Cleared and set new transcribed text with trailing space
    mock_pb.clearContents.assert_any_call()
    assert any(
        call.args and call.args[0] == "New transcribed dictation " for call in mock_pb.setString_forType_.call_args_list
    )

    # 3. Simulated Cmd+V keyboard events
    mock_post_cmd_v.assert_called_once()

    # 4. Restored old content
    assert any(
        call.args and call.args[0] == "original_clipboard_text" for call in mock_pb.setString_forType_.call_args_list
    )

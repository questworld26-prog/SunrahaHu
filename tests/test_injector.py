"""Tests for Active Window Injector."""

from unittest.mock import MagicMock, patch

from sunrahahu.injector import inject_text_to_active_window


def test_inject_text_empty():
    # Should safely return without touching pasteboard
    with patch("sunrahahu.injector.get_pasteboard") as mock_get_pb:
        inject_text_to_active_window("")
        mock_get_pb.assert_not_called()


@patch("sunrahahu.injector.post_cmd_v")
@patch("sunrahahu.injector.get_pasteboard")
def test_inject_text_clipboard_flow(
    mock_get_pb,
    mock_post_cmd_v,
):
    mock_pb = MagicMock()
    mock_pb.stringForType_.return_value = "original_clipboard_text"
    mock_get_pb.return_value = mock_pb

    inject_text_to_active_window("New transcribed dictation")

    # 1. Backed up old clipboard
    mock_pb.stringForType_.assert_called_once()

    # 2. Cleared and set new transcribed text
    mock_pb.clearContents.assert_any_call()
    assert any(
        call.args and call.args[0] == "New transcribed dictation" for call in mock_pb.setString_forType_.call_args_list
    )

    # 3. Simulated Cmd+V keyboard events
    mock_post_cmd_v.assert_called_once()

    # 4. Restored old content
    assert any(
        call.args and call.args[0] == "original_clipboard_text" for call in mock_pb.setString_forType_.call_args_list
    )

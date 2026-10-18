"""Active window text injection for macOS."""

import time

import AppKit
import Quartz


def get_pasteboard():
    """Helper to retrieve system pasteboard."""
    return AppKit.NSPasteboard.generalPasteboard()


def post_cmd_v():
    """Simulate Cmd+V keyboard shortcut."""
    key_code_v = 9  # kVK_ANSI_V

    # Key down with Command modifier
    event_down = Quartz.CGEventCreateKeyboardEvent(None, key_code_v, True)
    Quartz.CGEventSetFlags(event_down, Quartz.kCGEventFlagMaskCommand)
    Quartz.CGEventPost(Quartz.kCGHIDEventTap, event_down)

    time.sleep(0.02)

    # Key up
    event_up = Quartz.CGEventCreateKeyboardEvent(None, key_code_v, False)
    Quartz.CGEventSetFlags(event_up, Quartz.kCGEventFlagMaskCommand)
    Quartz.CGEventPost(Quartz.kCGHIDEventTap, event_up)


def inject_text_to_active_window(text: str):
    """
    Inserts text into the currently active macOS application window.
    Preserves original clipboard contents, pastes text using Cmd+V via CGEvent,
    and then restores original clipboard contents.
    """
    if not text:
        return

    pasteboard = get_pasteboard()
    ns_type = AppKit.NSPasteboardTypeString

    # 1. Backup existing clipboard content
    old_content = pasteboard.stringForType_(ns_type)

    try:
        # 2. Write new text to clipboard
        pasteboard.clearContents()
        pasteboard.setString_forType_(text, ns_type)

        # Brief pause to ensure pasteboard is updated
        time.sleep(0.05)

        # 3. Simulate Cmd+V keyboard shortcut
        post_cmd_v()

        # Allow destination app to process the paste command
        time.sleep(0.2)

    finally:
        # 4. Restore previous clipboard content
        if old_content is not None:
            pasteboard.clearContents()
            pasteboard.setString_forType_(old_content, ns_type)

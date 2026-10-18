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


def type_unicode_string(text: str):
    """
    Directly types a unicode string into the focused window using CGEventKeyboardSetUnicodeString.
    Handles emojis, non-BMP characters, and astral plane surrogate pairs cleanly.
    """
    if not text:
        return

    # Post unicode string in chunks (up to 20 chars per event for stability)
    chunk_size = 20
    for i in range(0, len(text), chunk_size):
        chunk = text[i : i + chunk_size]
        try:
            event_down = Quartz.CGEventCreateKeyboardEvent(None, 0, True)
            Quartz.CGEventKeyboardSetUnicodeString(event_down, len(chunk), chunk)
            Quartz.CGEventPost(Quartz.kCGHIDEventTap, event_down)

            time.sleep(0.005)

            event_up = Quartz.CGEventCreateKeyboardEvent(None, 0, False)
            Quartz.CGEventSetFlags(event_up, 0)
            Quartz.CGEventPost(Quartz.kCGHIDEventTap, event_up)
        except Exception as e:
            print(f"[Injector Error] Failed to post unicode chunk: {e}")


def inject_text_to_active_window(text: str, method: str = "direct"):
    """
    Inserts text into the currently active macOS application window.
    method:
      'direct' (default): Synthesizes direct unicode typing. Never touches clipboard!
      'paste': Uses pasteboard with Cmd+V and preserves previous clipboard content.
    """
    if not text:
        return

    # Append trailing space for natural continuous voice dictation
    if not text.endswith((" ", "\n", "\t")):
        text = text + " "

    if method == "direct":
        type_unicode_string(text)
        return

    # Fallback / paste method
    pasteboard = get_pasteboard()
    ns_type = AppKit.NSPasteboardTypeString

    # 1. Backup existing clipboard content
    old_content = pasteboard.stringForType_(ns_type)

    try:
        # 2. Write new text to clipboard
        pasteboard.clearContents()
        pasteboard.setString_forType_(text, ns_type)

        # Pause to ensure pasteboard is flushed and recognized by window server
        time.sleep(0.1)

        # 3. Simulate Cmd+V keyboard shortcut
        post_cmd_v()

        # Allow destination app ample time to process the paste event before restoring
        time.sleep(0.4)

    finally:
        # 4. Restore previous clipboard content
        if old_content is not None:
            pasteboard.clearContents()
            pasteboard.setString_forType_(old_content, ns_type)

"""Jarvis voice command processor and system automation for macOS."""

import re
import time

import Quartz

from sunrahahu.feedback import play_command_cue

# macOS Carbon virtual key codes for numbers 1-9
DESKTOP_KEYCODES = {
    1: 18,  # kVK_ANSI_1
    2: 19,  # kVK_ANSI_2
    3: 20,  # kVK_ANSI_3
    4: 21,  # kVK_ANSI_4
    5: 23,  # kVK_ANSI_5
    6: 22,  # kVK_ANSI_6
    7: 26,  # kVK_ANSI_7
    8: 28,  # kVK_ANSI_8
    9: 25,  # kVK_ANSI_9
}

# Word to number mapping including ordinals and common Whisper phonetic variations
WORD_TO_NUMBER = {
    "1": 1,
    "2": 2,
    "3": 3,
    "4": 4,
    "5": 5,
    "6": 6,
    "7": 7,
    "8": 8,
    "9": 9,
    "1st": 1,
    "2nd": 2,
    "3rd": 3,
    "4th": 4,
    "5th": 5,
    "6th": 6,
    "7th": 7,
    "8th": 8,
    "9th": 9,
    "one": 1,
    "two": 2,
    "three": 3,
    "four": 4,
    "five": 5,
    "six": 6,
    "seven": 7,
    "eight": 8,
    "nine": 9,
    "first": 1,
    "second": 2,
    "third": 3,
    "fourth": 4,
    "fifth": 5,
    "sixth": 6,
    "seventh": 7,
    "eighth": 8,
    "ninth": 9,
    "to": 2,
    "too": 2,
    "for": 4,
}

DESKTOP_PATTERNS = [
    re.compile(
        r"^(?:(?:switch|go|move)\s+(?:to\s+)?|jump\s+to\s+)?(?:the\s+)?(?:desktop|workspace|space)(?:\s+(?:number|no\.?))?\s+([a-zA-Z0-9]+)\.?$",
        re.IGNORECASE,
    ),
    re.compile(
        r"^(?:(?:switch|go|move)\s+(?:to\s+)?|jump\s+to\s+)?(?:the\s+)?([a-zA-Z0-9]+)\s+(?:desktop|workspace|space)\.?$",
        re.IGNORECASE,
    ),
]


WAKE_PREFIX_PATTERN = re.compile(
    r"^\s*(?:jarvis|service|java|travis|computer|command|suno|hey\s+mac)\b[\s,.:;!?-]*",
    re.IGNORECASE,
)


def is_jarvis_command(text: str) -> bool:
    """Determine if the input text starts with a recognized wake prefix."""
    if not text:
        return False
    return bool(WAKE_PREFIX_PATTERN.match(text))


def strip_jarvis_prefix(text: str) -> str:
    """Remove the wake prefix and leading/trailing punctuation."""
    return WAKE_PREFIX_PATTERN.sub("", text).strip()


def parse_desktop_number(text: str) -> int | None:
    """Extract desktop number 1-9 from command text."""
    for pattern in DESKTOP_PATTERNS:
        m = pattern.match(text)
        if m:
            token = m.group(1).lower().rstrip(".,;:!?")
            if token in WORD_TO_NUMBER:
                return WORD_TO_NUMBER[token]
            if token.isdigit():
                return int(token)
    return None


def parse_command(text: str) -> tuple[str | None, int | None]:
    """
    Parses command body after stripping wake prefix.
    Returns (action, argument) or (None, None) if unrecognized.
    """
    rest = strip_jarvis_prefix(text)
    if not rest:
        return None, None

    desktop_num = parse_desktop_number(rest)
    if desktop_num is not None:
        return "switch_desktop", desktop_num

    return None, None


def switch_to_desktop(desktop_num: int) -> bool:
    """Switch to macOS Desktop Space N (1-9) using Quartz Control+N key event."""
    if desktop_num not in DESKTOP_KEYCODES:
        return False

    key_code = DESKTOP_KEYCODES[desktop_num]
    try:
        event_down = Quartz.CGEventCreateKeyboardEvent(None, key_code, True)
        Quartz.CGEventSetFlags(event_down, Quartz.kCGEventFlagMaskControl)
        Quartz.CGEventPost(Quartz.kCGHIDEventTap, event_down)

        time.sleep(0.02)

        event_up = Quartz.CGEventCreateKeyboardEvent(None, key_code, False)
        Quartz.CGEventSetFlags(event_up, 0)
        Quartz.CGEventPost(Quartz.kCGHIDEventTap, event_up)
        return True
    except Exception as e:
        print(f"[Commander Error] Failed to switch desktop: {e}")
        return False


def handle_command(text: str) -> bool:
    """
    Check if transcribed text is a Jarvis command and execute it.
    Returns True if handled (or attempted) as a command, False for standard dictation.
    """
    if not is_jarvis_command(text):
        return False

    action, arg = parse_command(text)
    if action == "switch_desktop" and arg is not None:
        if 1 <= arg <= 9:
            success = switch_to_desktop(arg)
            if success:
                print(f"[Commander] Switched to Desktop {arg}")
                play_command_cue(f"Switching to desktop {arg}", async_play=True)
            else:
                print(f"[Commander] Failed to switch to Desktop {arg}")
                play_command_cue("Failed to switch desktop", async_play=True)
        else:
            play_command_cue("Desktop number must be between 1 and 9", async_play=True)
        return True

    # Jarvis prefix present, but command unrecognized
    print(f'[Commander] Unrecognized Jarvis command: "{text}"')
    play_command_cue("Command not recognized", async_play=True)
    return True

"""Global hotkey listener using pynput."""

from pynput import keyboard


class HotkeyListener:
    def __init__(self, hotkey_combo: str, on_trigger):
        """
        hotkey_combo: e.g. '<cmd>+<shift>+d' or '<ctrl>+<alt>+space'
        """
        self.hotkey_combo = hotkey_combo
        self.on_trigger = on_trigger
        self.listener = None

    def start(self):
        hotkeys = {self.hotkey_combo: self.on_trigger}
        self.listener = keyboard.GlobalHotKeys(hotkeys)
        self.listener.start()

    def stop(self):
        if self.listener:
            self.listener.stop()
            self.listener = None

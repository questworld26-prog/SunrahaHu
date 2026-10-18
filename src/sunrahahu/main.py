import rumps
from PyObjCTools import AppHelper

from sunrahahu.app import SunrahaHuApp
from sunrahahu.hotkey import HotkeyListener

# Default Hotkey: Cmd+Option+.
DEFAULT_HOTKEY = "<cmd>+<alt>+."


class SunrahaHuMenuBar(rumps.App):
    def __init__(self):
        super().__init__("SunrahaHu", title="🎙️ Idle")
        self.app_core = SunrahaHuApp(on_status_change=self.on_status_change)

        # Menu items
        self.trigger_item = rumps.MenuItem("🎙️ Dictate (Cmd+Opt+.)", callback=self.manual_trigger)
        self.status_item = rumps.MenuItem("Status: Ready (Language: Auto)", callback=None)

        # Language selection submenu
        self.lang_menu = rumps.MenuItem("🌐 Language")
        self.lang_auto = rumps.MenuItem("✓ Auto Detect", callback=lambda sender: self.select_language(None, sender))
        self.lang_hinglish = rumps.MenuItem(
            "  Hinglish (Hindi in English Script)", callback=lambda sender: self.select_language("hinglish", sender)
        )
        self.lang_bn = rumps.MenuItem("  বাংলা (Bengali)", callback=lambda sender: self.select_language("bn", sender))
        self.lang_hi = rumps.MenuItem("  हिन्दी (Hindi)", callback=lambda sender: self.select_language("hi", sender))
        self.lang_en = rumps.MenuItem("  English", callback=lambda sender: self.select_language("en", sender))
        self.lang_menu.update([self.lang_auto, self.lang_hinglish, self.lang_bn, self.lang_hi, self.lang_en])

        self.menu = [
            self.trigger_item,
            self.status_item,
            None,  # Separator
            self.lang_menu,
            None,  # Separator
            rumps.MenuItem("📋 Copy Last Transcription", callback=self.copy_last_transcription),
            rumps.MenuItem("📁 Open Dictation History Log", callback=self.open_history_log),
            None,
            rumps.MenuItem("Say 'सुन रहा हूँ' test", callback=self.test_voice),
            None,
        ]

        # Start global hotkey
        self.hotkey_listener = HotkeyListener(DEFAULT_HOTKEY, self.on_hotkey)
        self.hotkey_listener.start()

    def on_status_change(self, status: str):
        def _update():
            if status == "recording":
                self.title = "🔴 सुन रहा हूँ..."
                self.status_item.title = "Status: Recording..."
            elif status == "transcribing":
                self.title = "⚡ Transcribing..."
                self.status_item.title = "Status: Transcribing..."
            else:
                self.title = "🎙️ Idle"
                self.status_item.title = "Status: Ready"

        try:
            AppHelper.callAfter(_update)
        except Exception:
            _update()

    def on_hotkey(self):
        self.app_core.toggle_recording()

    def manual_trigger(self, _):
        self.app_core.toggle_recording()

    def select_language(self, lang_code, sender):
        self.app_core.set_language(lang_code)

        # Update checkmarks
        self.lang_auto.title = "  Auto Detect"
        self.lang_hinglish.title = "  Hinglish (Hindi in English Script)"
        self.lang_bn.title = "  বাংলা (Bengali)"
        self.lang_hi.title = "  हिन्दी (Hindi)"
        self.lang_en.title = "  English"

        name = "Auto"
        if lang_code == "hinglish":
            self.lang_hinglish.title = "✓ Hinglish (Hindi in English Script)"
            name = "Hinglish (Roman Script)"
        elif lang_code == "bn":
            self.lang_bn.title = "✓ বাংলা (Bengali)"
            name = "বাংলা (Bengali)"
        elif lang_code == "hi":
            self.lang_hi.title = "✓ हिन्दी (Hindi)"
            name = "हिन्दी (Hindi)"
        elif lang_code == "en":
            self.lang_en.title = "✓ English"
            name = "English"
        else:
            self.lang_auto.title = "✓ Auto Detect"

        self.status_item.title = f"Status: Ready (Language: {name})"

    def copy_last_transcription(self, _):
        """Copies the most recently dictated text onto the system pasteboard."""
        text = self.app_core.last_transcribed_text
        if text:
            import AppKit

            pb = AppKit.NSPasteboard.generalPasteboard()
            pb.clearContents()
            pb.setString_forType_(text, AppKit.NSPasteboardTypeString)
            rumps.notification("SunrahaHu", "Copied to Clipboard", f"'{text[:40]}...'")
        else:
            rumps.notification("SunrahaHu", "Clipboard Empty", "No recent dictation found yet.")

    def open_history_log(self, _):
        """Opens ~/.sunrahahu_history.txt in default text editor."""
        import subprocess

        from sunrahahu.app import HISTORY_LOG_PATH

        if not HISTORY_LOG_PATH.exists():
            with open(HISTORY_LOG_PATH, "w", encoding="utf-8") as f:
                f.write("# SunrahaHu Dictation History\n")
        subprocess.run(["open", str(HISTORY_LOG_PATH)], check=False)

    def test_voice(self, _):
        from sunrahahu.feedback import play_listening_cue

        play_listening_cue(async_play=True)


def main():
    print("=" * 50)
    print(" SunrahaHu (सुन रहा हूँ) - Whisper Large-V3-Turbo")
    print(" Global Shortcut: Cmd + Opt + .")
    print(" Press once: Says 'सुन रहा हूँ' and starts recording")
    print(" Press again: Stops recording and pastes text into active window")
    print("=" * 50)
    SunrahaHuMenuBar().run()


if __name__ == "__main__":
    main()

import threading

import rumps
from PyObjCTools import AppHelper

from sunrahahu.app import SunrahaHuApp


# [spec: UI-001]
class SunrahaHuMenuBar(rumps.App):
    def __init__(self):
        super().__init__("SunrahaHu", title="🎙️ Idle")
        self.app_core = SunrahaHuApp(on_status_change=self.on_status_change)

        # Menu items
        self.trigger_item = rumps.MenuItem("🎙️ Dictate (Toggle)", callback=self.manual_trigger)
        self.status_item = rumps.MenuItem("Status: Ready (Language: Auto)", callback=None)
        self.auto_stop_item = rumps.MenuItem("✓ Auto-Stop on Silence (1.3s)", callback=self.toggle_auto_stop)

        # Language selection submenu
        self.lang_menu = rumps.MenuItem("🌐 Language")
        self.lang_auto = rumps.MenuItem("✓ Auto Detect", callback=lambda sender: self.select_language(None, sender))
        self.lang_roman = rumps.MenuItem(
            "  Roman Script (English + Hindi + Bengali)", callback=lambda sender: self.select_language("roman", sender)
        )
        self.lang_bn = rumps.MenuItem("  বাংলা (Bengali)", callback=lambda sender: self.select_language("bn", sender))
        self.lang_hi = rumps.MenuItem("  हिन्दी (Hindi)", callback=lambda sender: self.select_language("hi", sender))
        self.lang_en = rumps.MenuItem("  English", callback=lambda sender: self.select_language("en", sender))
        self.lang_menu.update([self.lang_auto, self.lang_roman, self.lang_bn, self.lang_hi, self.lang_en])

        # Microphone selection submenu
        self.mic_menu = rumps.MenuItem("🎤 Microphone")
        self.refresh_microphones()

        self.menu = [
            self.trigger_item,
            self.status_item,
            None,  # Separator
            self.auto_stop_item,
            self.lang_menu,
            self.mic_menu,
            None,  # Separator
            rumps.MenuItem("Say 'सुन रहा हूँ' test", callback=self.test_voice),
            None,
        ]

    def refresh_microphones(self, sender=None):
        """Query and populate available input microphones with active checkmark."""
        import sounddevice as sd

        try:
            sd._terminate()
            sd._initialize()
            devices = sd.query_devices()
            default_input_idx = sd.default.device[0]
        except Exception as e:
            print(f"[SunrahaHu Error] Querying microphones: {e}")
            devices = []
            default_input_idx = None

        items = []
        default_name = "Default"
        if default_input_idx is not None and 0 <= default_input_idx < len(devices):
            default_name = devices[default_input_idx].get("name", "Default")

        is_default_selected = self.app_core.selected_device is None
        default_title = f"{'✓' if is_default_selected else ' '} System Default ({default_name})"
        items.append(rumps.MenuItem(default_title, callback=lambda s: self.select_microphone(None, s)))

        # Add all available physical/virtual input devices
        for idx, dev in enumerate(devices):
            if dev.get("max_input_channels", 0) > 0:
                is_selected = self.app_core.selected_device == idx
                item_title = f"{'✓' if is_selected else ' '} {dev['name']}"
                items.append(
                    rumps.MenuItem(
                        item_title,
                        callback=lambda s, dev_id=idx: self.select_microphone(dev_id, s),
                    )
                )

        items.append(None)  # Separator
        items.append(rumps.MenuItem("🔄 Refresh Devices", callback=self.refresh_microphones))

        if getattr(self.mic_menu, "_menu", None) is not None:
            self.mic_menu.clear()
        else:
            for k in list(self.mic_menu.keys()):
                del self.mic_menu[k]

        self.mic_menu.update(items)

    def select_microphone(self, device_id, sender):
        """Switch recording input microphone."""
        self.app_core.set_device(device_id)
        self.refresh_microphones()

    def on_status_change(self, status: str):
        def _update():
            if status == "recording":
                self.title = "🔴 सुन रहा हूँ..."
                self.status_item.title = "Status: Recording..."
                self.trigger_item.title = "⏹️ Stop Recording"
            elif status == "transcribing":
                self.title = "⚡ Transcribing..."
                self.status_item.title = "Status: Transcribing..."
                self.trigger_item.title = "⚡ Transcribing..."
            else:
                self.title = "🎙️ Idle"
                self.status_item.title = "Status: Ready"
                self.trigger_item.title = "🎙️ Dictate (Toggle)"

        try:
            AppHelper.callAfter(_update)
        except Exception:
            _update()

    def manual_trigger(self, _):
        threading.Thread(target=self.app_core.toggle_recording, daemon=True).start()

    def toggle_auto_stop(self, _):
        enabled = not self.app_core.auto_stop_enabled
        self.app_core.set_auto_stop(enabled)
        self.auto_stop_item.title = "✓ Auto-Stop on Silence (1.3s)" if enabled else "  Auto-Stop on Silence (1.3s)"

    def select_language(self, lang_code, sender):
        self.app_core.set_language(lang_code)

        # Update checkmarks
        self.lang_auto.title = "  Auto Detect"
        self.lang_roman.title = "  Roman Script (English + Hindi + Bengali)"
        self.lang_bn.title = "  বাংলা (Bengali)"
        self.lang_hi.title = "  हिन्दी (Hindi)"
        self.lang_en.title = "  English"

        name = "Auto"
        if lang_code in ("roman", "hinglish"):
            self.lang_roman.title = "✓ Roman Script (English + Hindi + Bengali)"
            name = "Roman Script (EN + HI + BN)"
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

    def test_voice(self, _):
        from sunrahahu.feedback import play_listening_cue

        play_listening_cue(async_play=True)


def main():
    print("=" * 50)
    print(" SunrahaHu (सुन रहा हूँ) - Whisper Large-V3-Turbo")
    print(" Menu Bar Mode: Click '🎙️ Dictate (Toggle)' in the menu bar")
    print(" Click once: Says 'सुन रहा हूँ' and starts recording")
    print(" Click again: Stops recording and types text into active window")
    print("=" * 50)
    SunrahaHuMenuBar().run()


if __name__ == "__main__":
    main()

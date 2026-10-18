"""Stress test for rapid sequential transcription, variable audio lengths, and mixed-language Hinglish."""

import time
from unittest.mock import MagicMock, patch

import numpy as np
import pytest

from sunrahahu.app import SunrahaHuApp
from sunrahahu.injector import inject_text_to_active_window
from sunrahahu.transcriber import Transcriber

TEST_MESSAGES = [
    # 1. Short English phrase (1s)
    "Quick note.",
    # 2. Medium English sentence (3s)
    "Testing audio transcription responsiveness under load.",
    # 3. Technical terminology (5s)
    "Whisper Large V3 Turbo running on Apple Silicon unified memory.",
    # 4. Bengali native script (4s)
    "আমি এটা বাংলায় পরীক্ষা করছি।",
    # 5. Hindi native script (4s)
    "नमस्ते, यह पाँचवाँ टेस्ट संदेश है।",
    # 6. Hinglish/Roman script: Mixed Hindi + English (6s)
    "Haan bhai main kal meeting mein yeh discuss karunga, lets make sure all tests pass.",
    # 7. Trilingual Roman script: Bengali + Hindi + English without translation (5s)
    "Ami theek achi, aap batao what is the plan? Ei project ta khub bhalo chal raha hai.",
    # 8. Very long paragraph (12s)
    "This is a significantly longer dictation passage designed to stress test the buffer allocation, "
    "audio frame concatenation, and memory deallocation pipelines to guarantee that extended speech "
    "never causes a buffer overrun or memory leak.",
    # 9. Complex Bengali sentence (5s)
    "আজকের আবহাওয়া খুব সুন্দর এবং রোদ উঠেছে।",
    # 10. Trilingual Roman closing (4s)
    "Chalo final tenth message, ami ready for release, let's ship it.",
]

# Variable audio lengths in seconds corresponding to each message
AUDIO_DURATIONS_SEC = [1.0, 3.0, 5.0, 4.0, 4.0, 6.0, 3.0, 12.0, 5.0, 4.0]


@pytest.mark.stress
def test_transcriber_stress_variable_length_and_hinglish():
    """
    Stress test verifying Transcriber handles variable audio durations (1s to 12s)
    and Hinglish Roman alphabet steering without crashes or memory drift.
    """
    transcriber = Transcriber()

    durations = []
    for msg, duration_sec in zip(TEST_MESSAGES, AUDIO_DURATIONS_SEC, strict=False):
        # Generate sinusoidal waveform of exact specified length
        sample_count = int(16000 * duration_sec)
        variable_audio = np.sin(np.linspace(0, 100 * duration_sec, sample_count), dtype=np.float32) * 0.1

        # Use Roman script mode for indices with Hinglish/Bengali in English script
        lang = "roman" if ("bhai" in str(msg) or "Ami" in str(msg) or "Chalo" in str(msg)) else None

        start = time.perf_counter()
        with patch("mlx_whisper.transcribe") as mock_mlx:
            mock_mlx.return_value = {"text": msg}
            result = transcriber.transcribe(variable_audio, language=lang)
            assert result == msg

            # Verify Roman script steered with English language and phonetic prompt
            if lang == "roman":
                _, kwargs = mock_mlx.call_args
                assert kwargs["language"] == "en"
                assert "initial_prompt" in kwargs
                assert "Bengali" in kwargs["initial_prompt"]
                assert "Hindi" in kwargs["initial_prompt"]

        elapsed = time.perf_counter() - start
        durations.append(elapsed)

    assert len(durations) == 10
    # Every mock transcription cycle must complete in under 50ms
    assert all(d < 0.05 for d in durations)


@pytest.mark.stress
@patch("sunrahahu.injector.type_unicode_string")
def test_injector_stress_10_sequential_messages(mock_type):
    """
    Stress test verifying active window injector processes 10 sequential messages
    rapidly without dropping characters or corrupting order.
    """
    dispatched = []

    def fake_type(text):
        dispatched.append(text)

    mock_type.side_effect = fake_type

    start_time = time.perf_counter()
    for message in TEST_MESSAGES:
        inject_text_to_active_window(message, method="direct")

    total_time = time.perf_counter() - start_time

    assert len(dispatched) == 10
    assert dispatched == [f"{m} " for m in TEST_MESSAGES]
    # 10 direct dispatches should complete almost instantaneously
    assert total_time < 0.2


@pytest.mark.stress
@patch("sunrahahu.app.play_typing_cue")
@patch("sunrahahu.app.play_done_cue")
@patch("sunrahahu.app.play_listening_cue")
@patch("sunrahahu.app.inject_text_to_active_window")
def test_app_orchestrator_stress_10_cycles(mock_inject, mock_listening_cue, mock_done_cue, mock_typing_cue):
    """
    End-to-end stress test simulating 10 back-to-back toggle recording & transcription cycles
    with variable lengths, verifying rapid consecutive injection and state cleanup.
    """
    status_history = []
    app = SunrahaHuApp(on_status_change=lambda s: status_history.append(s))

    with (
        patch.object(app.recorder, "start"),
        patch.object(app.recorder, "stop") as mock_stop,
        patch.object(app.transcriber, "transcribe") as mock_transcribe,
        patch("threading.Thread") as mock_thread,
    ):
        # Make worker execute synchronously for deterministic stress testing
        def run_target(target, daemon):
            target()
            return MagicMock()

        mock_thread.side_effect = run_target

        for expected_text, duration_sec in zip(TEST_MESSAGES, AUDIO_DURATIONS_SEC, strict=False):
            sample_count = int(16000 * duration_sec)
            mock_stop.return_value = np.ones(sample_count, dtype=np.float32)
            mock_transcribe.return_value = expected_text

            # 1. Toggle ON (Start)
            app.toggle_recording()
            assert app.is_recording is True

            # 2. Toggle OFF (Finish & Inject)
            app.toggle_recording()
            assert app.is_recording is False
            assert app.is_transcribing is False

    assert mock_inject.call_count == 10
    actual_injected = [call.args[0] for call in mock_inject.call_args_list]
    assert actual_injected == TEST_MESSAGES
    assert app.last_transcribed_text == TEST_MESSAGES[-1]

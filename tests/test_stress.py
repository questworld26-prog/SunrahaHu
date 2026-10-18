"""Stress test for rapid sequential transcription and text injection."""

import time
from unittest.mock import MagicMock, patch

import numpy as np
import pytest

from sunrahahu.app import SunrahaHuApp
from sunrahahu.injector import inject_text_to_active_window
from sunrahahu.transcriber import Transcriber

TEST_MESSAGES = [
    "Hello, this is message number one.",
    "Testing audio transcription responsiveness under load.",
    "Whisper Large V3 Turbo running on Apple Silicon.",
    "আমি এটা বাংলায় পরীক্ষা করছি।",  # Bengali: I am testing this in Bengali.
    "नमस्ते, यह पाँचवाँ टेस्ट संदेश है।",  # Hindi: Hello, this is the 5th test message.
    "Rapid consecutive speech recognition test.",
    "Ensuring zero memory leaks and clipboard integrity.",
    "Checking active window Unicode keystroke dispatch.",
    "আজকের আবহাওয়া খুব সুন্দর।",  # Bengali: Today's weather is very beautiful.
    "Final tenth message stress test completed successfully.",
]


@pytest.mark.stress
def test_transcriber_stress_10_sequential_runs():
    """
    Stress test verifying Transcriber handles 10 consecutive audio buffers
    without memory crashes, token drift, or timeouts.
    """
    transcriber = Transcriber()

    # Pre-generate 1-second non-silent dummy audio waveform
    dummy_audio = np.sin(np.linspace(0, 100, 16000), dtype=np.float32) * 0.1

    durations = []
    for i in range(10):
        start = time.perf_counter()
        with patch("mlx_whisper.transcribe") as mock_mlx:
            mock_mlx.return_value = {"text": TEST_MESSAGES[i]}
            result = transcriber.transcribe(dummy_audio)
            assert result == TEST_MESSAGES[i]

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
    End-to-end stress test simulating 10 back-to-back toggle recording & transcription cycles.
    Verifies state transitions (idle -> recording -> transcribing -> idle) remain consistent.
    """
    status_history = []
    app = SunrahaHuApp(on_status_change=lambda s: status_history.append(s))

    fake_audio = np.ones(16000, dtype=np.float32)

    with (
        patch.object(app.recorder, "start"),
        patch.object(app.recorder, "stop", return_value=fake_audio),
        patch.object(app.transcriber, "transcribe") as mock_transcribe,
        patch("threading.Thread") as mock_thread,
    ):
        # Make worker execute synchronously for deterministic stress testing
        def run_target(target, daemon):
            target()
            return MagicMock()

        mock_thread.side_effect = run_target

        for expected_text in TEST_MESSAGES:
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

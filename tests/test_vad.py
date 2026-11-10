"""Tests for Silero Neural Voice Activity Detector."""

import numpy as np

from sunrahahu.vad import SileroVAD


# [verifies: VAD-001/AC-VAD-001.1]
def test_silero_vad_init():
    vad = SileroVAD()
    assert vad.window_size == 512
    assert vad.context_size == 64
    assert vad.threshold == 0.5


# [verifies: VAD-001/AC-VAD-001.2]
def test_silero_vad_invalid_chunk_size():
    vad = SileroVAD()
    is_speech, prob = vad.is_speech(np.zeros(256, dtype=np.float32))
    assert is_speech is False
    assert prob == 0.0


# [verifies: VAD-001/AC-VAD-001.3]
def test_silero_vad_silence():
    vad = SileroVAD()
    silence = np.zeros(512, dtype=np.float32)
    is_speech, prob = vad.is_speech(silence)
    assert is_speech is False
    assert prob < 0.1


# [verifies: VAD-001/AC-VAD-001.3]
def test_silero_vad_fan_noise_resilience():
    vad = SileroVAD()
    # High amplitude white/pink noise simulating loud room fan / AC
    np.random.seed(42)
    fan_noise = np.random.normal(0, 0.03, 512).astype(np.float32)
    is_speech, prob = vad.is_speech(fan_noise)
    assert is_speech is False
    assert prob < 0.15

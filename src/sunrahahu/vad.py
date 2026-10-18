"""Silero Neural Voice Activity Detector (VAD) via ONNX Runtime."""

import os

import numpy as np
import onnxruntime as ort

MODEL_PATH = os.path.join(os.path.dirname(__file__), "assets", "silero_vad.onnx")


class SileroVAD:
    """
    Neural Voice Activity Detector using the Silero VAD v5 ONNX model.
    Immune to background fans, air conditioners, room reverberation, and variable microphone gains.
    """

    def __init__(
        self,
        model_path: str = MODEL_PATH,
        threshold: float = 0.5,
        sample_rate: int = 16000,
    ):
        self.threshold = threshold
        self.sample_rate = sample_rate
        self.window_size = 512  # 32ms at 16kHz
        self.context_size = 64  # required context prefix for Silero v5
        self.sr_tensor = np.array(sample_rate, dtype=np.int64)

        opts = ort.SessionOptions()
        opts.inter_op_num_threads = 1
        opts.intra_op_num_threads = 1
        opts.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL

        self.session = ort.InferenceSession(model_path, opts, providers=["CPUExecutionProvider"])
        self.reset()

    def reset(self):
        """Reset hidden state and context buffer for a new audio recording."""
        self._state = np.zeros((2, 1, 128), dtype=np.float32)
        self._context = np.zeros((1, self.context_size), dtype=np.float32)

    def is_speech(self, chunk: np.ndarray) -> tuple[bool, float]:
        """
        Evaluate if a 512-sample (32ms) audio chunk contains human speech.
        Returns (is_speech, probability).
        """
        if len(chunk) != self.window_size:
            return False, 0.0

        audio = chunk.reshape(1, self.window_size).astype(np.float32)
        x = np.concatenate([self._context, audio], axis=1)

        out, self._state = self.session.run(
            None,
            {
                "input": x,
                "state": self._state,
                "sr": self.sr_tensor,
            },
        )
        self._context = x[:, -self.context_size :]
        prob = float(out[0][0])
        return prob >= self.threshold, prob

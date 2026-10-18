"""Whisper Large-V3-Turbo transcription engine using MLX on Apple Silicon."""

import mlx_whisper
import numpy as np

MODEL_NAME = "mlx-community/whisper-large-v3-turbo"


class Transcriber:
    def __init__(self, model_name: str = MODEL_NAME):
        self.model_name = model_name

    def transcribe(
        self,
        audio_data: np.ndarray,
        language: str = None,
        task: str = "transcribe",
    ) -> str:
        """
        Transcribes or translates 16kHz float32 audio buffer into text.
        task: 'transcribe' (native language) or 'translate' (translates to English)
        """
        if audio_data is None or len(audio_data) == 0:
            return ""

        # Require at least 0.4 seconds of audio
        if len(audio_data) < 16000 * 0.4:
            return ""

        kwargs = {
            "path_or_hf_repo": self.model_name,
            "task": task,
        }
        if language:
            kwargs["language"] = language

        result = mlx_whisper.transcribe(audio_data, **kwargs)
        text = result.get("text", "").strip()
        return text

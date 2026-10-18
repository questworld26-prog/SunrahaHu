"""Whisper Large-V3-Turbo transcription engine using MLX on Apple Silicon."""

import mlx_whisper
import numpy as np

MODEL_NAME = "mlx-community/whisper-large-v3-turbo"

# Common repetitive Whisper hallucinations on silence / non-speech noise
COMMON_HALLUCINATIONS = {
    "thank you.",
    "thank you",
    "thanks for watching!",
    "thanks for watching.",
    "subscribe to my channel",
    "please subscribe",
    "you",
    ".",
    "...",
    "!",
}


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
        Transcribes 16kHz float32 audio buffer into text.
        Includes silence detection, audio normalization, and hallucination filtering.
        """
        if audio_data is None or len(audio_data) == 0:
            return ""

        # Edge case: Short burst noise (< 0.5s)
        if len(audio_data) < 16000 * 0.5:
            return ""

        # Edge case: Pure silence / low-energy ambient noise
        # Calculate Root Mean Square (RMS) energy
        rms = np.sqrt(np.mean(np.square(audio_data)))
        if rms < 0.003:  # Background room noise threshold
            return ""

        # Normalize audio volume to prevent clipping or whispering under-gain
        max_abs = np.max(np.abs(audio_data))
        normalized_audio = (audio_data / max_abs * 0.95) if max_abs > 0 else audio_data

        kwargs = {
            "path_or_hf_repo": self.model_name,
            "task": task,
            "no_speech_threshold": 0.6,
        }
        if language:
            kwargs["language"] = language

        try:
            result = mlx_whisper.transcribe(normalized_audio, **kwargs)
            text = result.get("text", "").strip()

            # Filter known Whisper silence hallucinations
            if text.lower() in COMMON_HALLUCINATIONS:
                return ""

            return text
        except Exception as e:
            print(f"[Transcriber Error]: {e}")
            return ""

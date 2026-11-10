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

# Steering prompt for multilingual Romanized script (English + Hindi + Bengali)
# Forces phonetic transcription using English Latin characters without translating
ROMAN_PHONETIC_PROMPT = (
    "Transcribe exactly what is spoken using the English Latin alphabet (phonetic Roman script) "
    "without translating. Support mixed English, Hindi, and Bengali: "
    "e.g. 'Ami bhalo achi, tumi kemon acho? Main theek hoon, lets start the work. "
    "Haan bhai kal dekhte hai, ei project ta khub bhalo.'"
)


# [spec: STT-001]
# [spec: STT-002]
class Transcriber:
    def __init__(self, model_name: str = MODEL_NAME):
        self.model_name = model_name

    def transcribe(
        self,
        audio_data: np.ndarray,
        language: str | None = None,
        task: str = "transcribe",
    ) -> str:
        """
        Transcribes 16kHz float32 audio buffer into text.
        Includes silence detection, audio normalization, Roman phonetic steering, and hallucination filtering.
        """
        if audio_data is None or len(audio_data) == 0:
            return ""

        # Edge case: Short burst noise (< 0.5s)
        if len(audio_data) < 16000 * 0.5:
            return ""

        # Remove DC offset if present
        audio_data = audio_data - np.mean(audio_data)

        # Edge case: Pure silence / digital flatline (< -80 dBFS)
        # Low threshold (0.0001) prevents discarding quiet Bluetooth headsets / AirPods,
        # while rejecting true flatlines before heavy inference.
        rms = float(np.sqrt(np.mean(np.square(audio_data))))
        if rms < 0.0001:
            return ""

        # Normalize audio volume to prevent clipping or whispering under-gain
        max_abs = float(np.max(np.abs(audio_data)))
        if max_abs < 0.0002:
            return ""
        normalized_audio = (audio_data / max_abs * 0.95) if max_abs > 0 else audio_data

        kwargs = {
            "path_or_hf_repo": self.model_name,
            "task": task,
            "no_speech_threshold": 0.6,
        }

        # Language handling:
        # 'roman' or 'hinglish': Steers Whisper to transcribe English + Hindi + Bengali phonetically in English alphabet
        if language in ("roman", "hinglish"):
            kwargs["language"] = "en"
            kwargs["initial_prompt"] = ROMAN_PHONETIC_PROMPT
        elif language:
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

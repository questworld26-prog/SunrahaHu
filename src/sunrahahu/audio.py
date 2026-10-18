"""Audio recording utility for SunrahaHu."""

import queue

import numpy as np
import sounddevice as sd


class AudioRecorder:
    def __init__(self, sample_rate: int = 16000, channels: int = 1):
        self.sample_rate = sample_rate
        self.channels = channels
        self.audio_queue = queue.Queue()
        self.stream = None
        self.is_recording = False

    def _callback(self, indata, frames, time_info, status):
        if self.is_recording:
            self.audio_queue.put(indata.copy())

    def start(self):
        """Start capturing audio cleanly with input device validation."""
        # Drain previous queue items
        while not self.audio_queue.empty():
            try:
                self.audio_queue.get_nowait()
            except queue.Empty:
                break

        # Stop existing stream if already open
        if self.stream is not None:
            try:
                self.stream.abort(ignore_errors=True)
                self.stream.close(ignore_errors=True)
            except Exception:
                pass
            self.stream = None

        self.is_recording = True
        try:
            self.stream = sd.InputStream(
                samplerate=self.sample_rate,
                channels=self.channels,
                dtype="float32",
                callback=self._callback,
            )
            self.stream.start()
        except Exception as e:
            self.is_recording = False
            self.stream = None
            print(f"[AudioRecorder Error] Failed to start audio input stream: {e}")
            raise

    def stop(self) -> np.ndarray:
        """Stop capturing audio and return recorded numpy float32 buffer."""
        self.is_recording = False
        if self.stream is not None:
            try:
                # Use abort() instead of stop() on macOS CoreAudio
                # stop() waits for pending buffer delivery which deadlocks in HALC_IOThread mutex
                self.stream.abort(ignore_errors=True)
                self.stream.close(ignore_errors=True)
            except Exception:
                pass
            self.stream = None

        chunks = []
        while not self.audio_queue.empty():
            try:
                chunks.append(self.audio_queue.get_nowait())
            except queue.Empty:
                break

        if not chunks:
            return np.array([], dtype=np.float32)

        audio_data = np.concatenate(chunks, axis=0)
        return audio_data.flatten()

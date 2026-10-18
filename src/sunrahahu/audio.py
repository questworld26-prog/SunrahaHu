"""Audio recording utility for SunrahaHu."""

import queue
import threading

import numpy as np
import sounddevice as sd


class AudioRecorder:
    def __init__(
        self,
        sample_rate: int = 16000,
        channels: int = 1,
        vad_enabled: bool = True,
        speech_threshold: float = 0.0035,
        silence_threshold: float = 0.0025,
        silence_duration: float = 1.3,
        min_speech_duration: float = 0.08,
        max_initial_silence: float = 6.0,
        on_silence_detected=None,
        on_initial_timeout=None,
    ):
        self.sample_rate = sample_rate
        self.channels = channels
        self.vad_enabled = vad_enabled
        self.speech_threshold = speech_threshold
        self.silence_threshold = silence_threshold
        self.silence_duration = silence_duration
        self.min_speech_duration = min_speech_duration
        self.max_initial_silence = max_initial_silence

        self.silence_duration_frames = int(silence_duration * sample_rate)
        self.min_speech_frames = int(min_speech_duration * sample_rate)
        self.max_initial_silence_frames = int(max_initial_silence * sample_rate)

        self.on_silence_detected = on_silence_detected
        self.on_initial_timeout = on_initial_timeout

        self.audio_queue = queue.Queue()
        self.stream = None
        self.is_recording = False

        # VAD state tracking
        self.has_speech_started = False
        self.speech_frames = 0
        self.silence_frames = 0
        self.initial_silence_frames = 0
        self.vad_triggered = False

    def _process_vad(self, indata, frames):
        """Process incoming audio frame with RMS energy thresholding for silence detection."""
        rms = float(np.sqrt(np.mean(np.square(indata))))

        if not self.has_speech_started:
            if rms >= self.speech_threshold:
                self.speech_frames += frames
                if self.speech_frames >= self.min_speech_frames:
                    self.has_speech_started = True
                    self.silence_frames = 0
            else:
                self.initial_silence_frames += frames
                if self.initial_silence_frames >= self.max_initial_silence_frames:
                    self.vad_triggered = True
                    # If grace period expires, trigger transcription so quiet speech is never discarded
                    cb = self.on_initial_timeout or self.on_silence_detected
                    if cb:
                        threading.Thread(target=cb, daemon=True).start()
        else:
            if rms < self.silence_threshold:
                self.silence_frames += frames
                if self.silence_frames >= self.silence_duration_frames:
                    self.vad_triggered = True
                    if self.on_silence_detected:
                        threading.Thread(target=self.on_silence_detected, daemon=True).start()
            else:
                self.silence_frames = 0

    def _callback(self, indata, frames, time_info, status):
        if not self.is_recording:
            return

        self.audio_queue.put(indata.copy())

        if self.vad_enabled and not self.vad_triggered:
            self._process_vad(indata, frames)

    def start(self):
        """Start capturing audio cleanly with input device validation."""
        # Reset VAD tracking counters
        self.has_speech_started = False
        self.consecutive_speech_frames = 0
        self.silence_frames = 0
        self.initial_silence_frames = 0
        self.vad_triggered = False

        # Drain previous queue items
        while not self.audio_queue.empty():
            try:
                self.audio_queue.get_nowait()
            except queue.Empty:
                break

        # Stop existing stream if already open
        if self.stream is not None:
            old_stream = self.stream
            self.stream = None

            def _close_old():
                try:
                    old_stream.abort(ignore_errors=True)
                    old_stream.close(ignore_errors=True)
                except Exception:
                    pass

            t = threading.Thread(target=_close_old, daemon=True)
            t.start()
            t.join(timeout=0.2)

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
        stream = self.stream
        self.stream = None

        if stream is not None:

            def _close_stream():
                try:
                    stream.abort(ignore_errors=True)
                    stream.close(ignore_errors=True)
                except Exception:
                    pass

            # Close stream on a background thread with timeout to prevent CoreAudio HALC_IOThread deadlocks
            t = threading.Thread(target=_close_stream, daemon=True)
            t.start()
            t.join(timeout=0.2)

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

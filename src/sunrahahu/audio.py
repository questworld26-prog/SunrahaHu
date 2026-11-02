"""Audio recording utility for SunrahaHu."""

import queue
import threading

import numpy as np
import sounddevice as sd

from sunrahahu.vad import SileroVAD


class AudioRecorder:
    def __init__(
        self,
        device: int | str | None = None,
        sample_rate: int = 16000,
        channels: int = 1,
        vad_enabled: bool = True,
        speech_prob_threshold: float = 0.5,
        silence_duration: float = 1.3,
        min_speech_duration: float = 0.15,
        max_initial_silence: float = 6.0,
        on_silence_detected=None,
        on_initial_timeout=None,
    ):
        self.device = device
        self.sample_rate = sample_rate
        self.channels = channels
        self.vad_enabled = vad_enabled
        self.speech_prob_threshold = speech_prob_threshold
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

        # Silero VAD neural network instance
        self.vad = None
        try:
            self.vad = SileroVAD(threshold=speech_prob_threshold, sample_rate=sample_rate)
        except Exception as e:
            print(f"[AudioRecorder Warning] Failed to initialize SileroVAD: {e}")

        # VAD state tracking
        self.vad_buffer = np.array([], dtype=np.float32)
        self.has_speech_started = False
        self.speech_frames = 0
        self.silence_frames = 0
        self.initial_silence_frames = 0
        self.vad_triggered = False

    def _process_vad_chunk(self, chunk: np.ndarray):
        """Process a 512-sample (32ms) window through Silero VAD."""
        is_speech, _prob = self.vad.is_speech(chunk)

        if not self.has_speech_started:
            if is_speech:
                self.speech_frames += 512
                if self.speech_frames >= self.min_speech_frames:
                    self.has_speech_started = True
                    self.silence_frames = 0
            else:
                self.initial_silence_frames += 512
                if self.initial_silence_frames >= self.max_initial_silence_frames:
                    self.vad_triggered = True
                    cb = self.on_initial_timeout or self.on_silence_detected
                    if cb:
                        threading.Thread(target=cb, daemon=True).start()
        else:
            if not is_speech:
                self.silence_frames += 512
                if self.silence_frames >= self.silence_duration_frames:
                    self.vad_triggered = True
                    if self.on_silence_detected:
                        threading.Thread(target=self.on_silence_detected, daemon=True).start()
            else:
                self.silence_frames = 0

    def _process_vad(self, indata):
        """Buffer incoming audio into 512-sample chunks for Silero VAD evaluation."""
        if self.vad is None:
            return

        mono = indata[:, 0] if indata.ndim > 1 else indata
        self.vad_buffer = np.concatenate([self.vad_buffer, mono.flatten()])

        while len(self.vad_buffer) >= 512 and not self.vad_triggered:
            chunk = self.vad_buffer[:512]
            self.vad_buffer = self.vad_buffer[512:]
            self._process_vad_chunk(chunk)

    def _callback(self, indata, frames, time_info, status):
        if not self.is_recording:
            return

        self.audio_queue.put(indata.copy())

        if self.vad_enabled and not self.vad_triggered:
            self._process_vad(indata)

    def _reset_state(self):
        """Reset internal VAD counters and tracking buffers."""
        if self.vad:
            self.vad.reset()
        self.vad_buffer = np.array([], dtype=np.float32)
        self.has_speech_started = False
        self.speech_frames = 0
        self.silence_frames = 0
        self.initial_silence_frames = 0
        self.vad_triggered = False

    def _drain_queue(self):
        """Empty any leftover audio frames from queue."""
        while not self.audio_queue.empty():
            try:
                self.audio_queue.get_nowait()
            except queue.Empty:
                break

    def _close_stream(self, stream):
        """Safely close a PortAudio stream on a background thread to prevent CoreAudio HALC_IOThread deadlocks."""
        if stream is None:
            return

        def _do_close():
            try:
                stream.abort(ignore_errors=True)
                stream.close(ignore_errors=True)
            except Exception:
                pass

        t = threading.Thread(target=_do_close, daemon=True)
        t.start()
        t.join(timeout=0.2)

    def start(self):
        """Start capturing audio cleanly with input device validation."""
        self._reset_state()
        self._drain_queue()

        if self.stream is not None:
            old_stream = self.stream
            self.stream = None
            self._close_stream(old_stream)

        # Refresh PortAudio cache to detect dynamically connected/disconnected Bluetooth headsets
        try:
            sd._terminate()
            sd._initialize()
        except Exception:
            pass

        self.is_recording = True
        try:
            self.stream = sd.InputStream(
                device=self.device,
                samplerate=self.sample_rate,
                channels=self.channels,
                dtype="float32",
                callback=self._callback,
            )
            self.stream.start()
            try:
                active_dev = getattr(self.stream, "device", self.device)
                if active_dev is not None:
                    dev_info = sd.query_devices(active_dev)
                    print(f"[AudioRecorder] Listening on '{dev_info['name']}' at {self.sample_rate}Hz")
            except Exception:
                pass
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
        self._close_stream(stream)

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

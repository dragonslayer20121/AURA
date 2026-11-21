from __future__ import annotations

import threading
import time
import numpy as np
from PyQt6.QtCore import QThread, pyqtSignal


class AudioCapture(QThread):
    level_changed = pyqtSignal(float)
    capture_error = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self._stop_event = threading.Event()
        self._stream = None
        self._audio = None

    def start(self, priority=None):
        self._stop_event.clear()
        if not self.isRunning():
            super().start()

    def stop(self):
        self._stop_event.set()
        try:
            if self._stream is not None:
                self._stream.stop_stream()
                self._stream.close()
        except Exception:
            pass
        try:
            if self._audio is not None:
                self._audio.terminate()
        except Exception:
            pass
        self._stream = None
        self._audio = None
        if self.isRunning():
            self.wait(1500)

    def run(self):
        try:
            import pyaudiowpatch as pyaudio
            self._audio = pyaudio.PyAudio()
            device = self._audio.get_default_wasapi_loopback()
            channels = max(1, min(2, int(device.get("maxInputChannels", 2))))
            rate = int(device.get("defaultSampleRate", 48000))
            self._stream = self._audio.open(
                format=pyaudio.paInt16,
                channels=channels,
                rate=rate,
                input=True,
                input_device_index=device["index"],
                frames_per_buffer=1024,
            )
            smoothed = 0.0
            while not self._stop_event.is_set():
                data = self._stream.read(1024, exception_on_overflow=False)
                samples = np.frombuffer(data, dtype=np.int16).astype(np.float32) / 32768.0
                if samples.size:
                    rms = float(np.sqrt(np.mean(samples * samples)))
                    peak = min(1.0, rms * 4.5)
                    smoothed = smoothed * 0.72 + peak * 0.28
                    self.level_changed.emit(smoothed)
        except Exception as exc:
            self.capture_error.emit(str(exc))
            while not self._stop_event.is_set():
                self.level_changed.emit(0.0)
                time.sleep(0.1)
        finally:
            try:
                if self._stream is not None:
                    self._stream.stop_stream()
                    self._stream.close()
            except Exception:
                pass
            try:
                if self._audio is not None:
                    self._audio.terminate()
            except Exception:
                pass
            self._stream = None
            self._audio = None

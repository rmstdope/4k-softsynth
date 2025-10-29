"""
Audio device management for real-time audio playback
Handles audio device initialization and sample playback
"""

import logging
import threading
import time
from typing import Optional, Callable

import numpy as np

try:
    import pyaudio  # pylint: disable=import-error
    PYAUDIO_AVAILABLE = True
except ImportError:
    PYAUDIO_AVAILABLE = False
    print("Warning: PyAudio not available. Audio playback will be simulated.")


# pylint: disable=too-many-instance-attributes
class Audio:
    """Audio device manager for real-time audio playback"""

    def __init__(self, sample_rate: int = 44100, channels: int = 1,
                 chunk_size: int = 1024, format_bits: int = 32):
        """Initialize the audio device

        Args:
            sample_rate: Audio sample rate in Hz (default: 44100)
            channels: Number of audio channels (default: 1 for mono)
            chunk_size: Audio buffer size in samples (default: 1024)
            format_bits: Bit depth - 16 or 32 (default: 32)
        """
        self.sample_rate = sample_rate
        self.channels = channels
        self.chunk_size = chunk_size
        self.format_bits = format_bits

        # Audio format mapping
        if format_bits == 16:
            self.np_format = np.int16
            self.pa_format = pyaudio.paInt16 if PYAUDIO_AVAILABLE else None
            self.sample_max = 32767.0
        else:  # 32-bit float
            self.np_format = np.float32
            self.pa_format = pyaudio.paFloat32 if PYAUDIO_AVAILABLE else None
            self.sample_max = 1.0

        self.pyaudio_instance = None
        self.stream = None
        self.is_initialized = False
        self.is_playing = False

        # Playback control
        self._playback_thread = None
        self._stop_playback = threading.Event()
        self._playback_callback = None

        # Logging
        self.logger = logging.getLogger(__name__)

        # Initialize the audio system
        self.initialize()

    def initialize(self) -> bool:
        """Initialize the audio system

        Returns:
            True if initialization successful, False otherwise
        """
        if not PYAUDIO_AVAILABLE:
            self.logger.warning("PyAudio not available, running in simulation mode")
            self.is_initialized = True  # Allow simulation mode
            return True

        try:
            self.pyaudio_instance = pyaudio.PyAudio()

            # Get default output device info
            default_device = self.pyaudio_instance.get_default_output_device_info()
            self.logger.info("Default audio device: %s", default_device['name'])
            self.logger.info("Max output channels: %s", default_device['maxOutputChannels'])

            # Create audio stream
            self.stream = self.pyaudio_instance.open(
                format=self.pa_format,
                channels=self.channels,
                rate=self.sample_rate,
                output=True,
                frames_per_buffer=self.chunk_size
            )

            self.is_initialized = True
            self.logger.info("Audio initialized: %sHz, %sch, %sbit",
                           self.sample_rate, self.channels, self.format_bits)
            return True

        except (OSError, IOError, ValueError) as e:
            self.logger.error("Audio initialization failed: %s", e)
            self.is_initialized = False
            return False

    def play_samples(self, samples: np.ndarray, blocking: bool = True,
                    callback: Optional[Callable] = None) -> bool:
        """Play an array of audio samples

        Args:
            samples: NumPy array of audio samples (float values -1.0 to 1.0)
            blocking: If True, block until playback completes
            callback: Optional callback function called when playback finishes

        Returns:
            True if playback started successfully, False otherwise
        """
        if not self.is_initialized:
            self.logger.error("Audio system not initialized")
            return False

        # Ensure samples are in the correct format
        if not isinstance(samples, np.ndarray):
            samples = np.array(samples, dtype=np.float32)

        # Convert to correct number of channels if needed
        if len(samples.shape) == 1 and self.channels > 1:
            # Mono to multi-channel: duplicate the mono signal
            samples = np.tile(samples.reshape(-1, 1), (1, self.channels))
        elif len(samples.shape) == 2 and samples.shape[1] != self.channels:
            self.logger.warning("Sample channels (%s) != device channels (%s)",
                              samples.shape[1], self.channels)
            # Take first channel or average channels
            if self.channels == 1:
                samples = np.mean(samples, axis=1)
            else:
                samples = samples[:, :self.channels]

        # Ensure samples are in valid range
        samples = np.clip(samples, -1.0, 1.0)

        # Store callback
        self._playback_callback = callback

        if blocking:
            return self._play_samples_blocking(samples)
        return self._play_samples_async(samples)

    def _play_samples_blocking(self, samples: np.ndarray) -> bool:
        """Play samples in blocking mode"""
        if not PYAUDIO_AVAILABLE:
            # Simulate playback
            duration = len(samples) / self.sample_rate
            self.logger.info("Simulating audio playback: %.3fs, %s samples",
                           duration, len(samples))
            time.sleep(duration)
            if self._playback_callback:
                self._playback_callback()
            return True

        try:
            self.is_playing = True

            # Convert samples to the correct format
            if self.format_bits == 16:
                audio_data = (samples * self.sample_max).astype(np.int16)
            else:
                audio_data = samples.astype(np.float32)

            # Convert to bytes and play
            audio_bytes = audio_data.tobytes()
            self.stream.write(audio_bytes)

            self.is_playing = False

            if self._playback_callback:
                self._playback_callback()

            return True

        except (OSError, IOError, ValueError) as e:
            self.logger.error("Audio playback error: %s", e)
            self.is_playing = False
            return False

    def _play_samples_async(self, samples: np.ndarray) -> bool:
        """Play samples in non-blocking mode"""
        if self.is_playing:
            self.logger.warning("Audio already playing, stopping previous playback")
            self.stop()

        self._stop_playback.clear()
        self._playback_thread = threading.Thread(
            target=self._playback_worker,
            args=(samples,)
        )
        self._playback_thread.daemon = True
        self._playback_thread.start()
        return True

    def _playback_worker(self, samples: np.ndarray):
        """Worker thread for non-blocking playback"""
        try:
            self._play_samples_blocking(samples)
        except (OSError, IOError, ValueError) as e:
            self.logger.error("Playback worker error: %s", e)
        finally:
            self.is_playing = False

    def stop(self):
        """Stop current audio playback"""
        if self.is_playing:
            self._stop_playback.set()
            if self._playback_thread and self._playback_thread.is_alive():
                self._playback_thread.join(timeout=1.0)
            self.is_playing = False
            self.logger.info("Audio playback stopped")

    def get_device_info(self) -> dict:
        """Get information about the current audio device

        Returns:
            Dictionary with device information
        """
        info = {
            'sample_rate': self.sample_rate,
            'channels': self.channels,
            'chunk_size': self.chunk_size,
            'format_bits': self.format_bits,
            'is_initialized': self.is_initialized,
            'is_playing': self.is_playing,
            'pyaudio_available': PYAUDIO_AVAILABLE
        }

        if PYAUDIO_AVAILABLE and self.pyaudio_instance:
            try:
                device_info = self.pyaudio_instance.get_default_output_device_info()
                info.update({
                    'device_name': device_info.get('name', 'Unknown'),
                    'max_output_channels': device_info.get('maxOutputChannels', 0),
                    'default_sample_rate': device_info.get('defaultSampleRate', 0)
                })
            except (OSError, IOError, ValueError) as e:
                self.logger.warning("Could not get device info: %s", e)

        return info

    def set_volume(self, volume: float):
        """Set playback volume (0.0 to 1.0)

        Note: This is a placeholder. Volume control would need to be
        implemented at the sample level or through system audio APIs.

        Args:
            volume: Volume level from 0.0 (silent) to 1.0 (full volume)
        """
        volume = max(0.0, min(1.0, volume))
        self.logger.info("Volume set to %.2f (not implemented)", volume)
        # TODO: Implement volume control  # pylint: disable=fixme

    def cleanup(self):
        """Clean up audio resources"""
        self.stop()

        if self.stream:
            try:
                self.stream.stop_stream()
                self.stream.close()
            except (OSError, IOError, ValueError) as e:
                self.logger.warning("Error closing audio stream: %s", e)
            finally:
                self.stream = None

        if self.pyaudio_instance:
            try:
                self.pyaudio_instance.terminate()
            except (OSError, IOError, ValueError) as e:
                self.logger.warning("Error terminating PyAudio: %s", e)
            finally:
                self.pyaudio_instance = None

        self.is_initialized = False
        self.logger.info("Audio cleanup completed")

    def __del__(self):
        """Destructor to ensure cleanup"""
        self.cleanup()

    def __enter__(self):
        """Context manager entry"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.cleanup()


# Convenience function for simple playback
def play_audio(samples: np.ndarray, sample_rate: int = 44100,
               blocking: bool = True) -> bool:
    """Convenience function to play audio samples

    Args:
        samples: NumPy array of audio samples (float values -1.0 to 1.0)
        sample_rate: Sample rate in Hz
        blocking: Whether to block until playback completes

    Returns:
        True if playback successful, False otherwise
    """
    with Audio(sample_rate=sample_rate) as audio:
        return audio.play_samples(samples, blocking=blocking)

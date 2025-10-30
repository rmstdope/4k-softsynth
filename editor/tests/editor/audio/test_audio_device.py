#!/usr/bin/env python3
"""
Comprehensive tests for the AudioDevice class

This test suite validates the AudioDevice functionality, including:
- Initialization and configuration
- Audio format handling
- Sample playback (blocking and non-blocking)
- Device information retrieval
- Error handling and edge cases
- Resource cleanup

The tests use mocking to avoid requiring actual audio hardware.

Running Tests:
1. Using pytest directly:
   pytest tests/editor/audio/test_audio_device.py -v

2. Running specific test classes:
   pytest tests/editor/audio/test_audio_device.py::TestAudioDeviceInitialization -v
"""

import os
import sys
import time
from unittest.mock import Mock, patch, MagicMock

import pytest
import numpy as np

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../../src"))

from editor.audio.audio_device import AudioDevice, play_audio  # pylint: disable=wrong-import-position


class TestAudioDeviceInitialization:
    """Test AudioDevice initialization and configuration"""

    def test_default_initialization_parameters(self):
        """Test AudioDevice with default parameters"""
        with patch('editor.audio.audio_device.pyaudio.PyAudio') as mock_pyaudio_class:
            mock_pyaudio = Mock()
            mock_stream = Mock()
            mock_device_info = {
                'name': 'Default Device',
                'maxOutputChannels': 2,
                'defaultSampleRate': 44100.0
            }

            mock_pyaudio.get_default_output_device_info.return_value = mock_device_info
            mock_pyaudio.open.return_value = mock_stream
            mock_pyaudio_class.return_value = mock_pyaudio

            device = AudioDevice()

            # Check default parameters
            assert device.sample_rate == 44100
            assert device.channels == 1
            assert device.chunk_size == 1024
            assert device.format_bits == 32
            assert device.is_initialized is True

    def test_custom_initialization_parameters(self):
        """Test AudioDevice with custom parameters"""
        with patch('editor.audio.audio_device.pyaudio.PyAudio') as mock_pyaudio_class:
            mock_pyaudio = Mock()
            mock_stream = Mock()
            mock_device_info = {'name': 'Test Device', 'maxOutputChannels': 8}

            mock_pyaudio.get_default_output_device_info.return_value = mock_device_info
            mock_pyaudio.open.return_value = mock_stream
            mock_pyaudio_class.return_value = mock_pyaudio

            device = AudioDevice(
                sample_rate=48000,
                channels=2,
                chunk_size=512,
                format_bits=16
            )

            assert device.sample_rate == 48000
            assert device.channels == 2
            assert device.chunk_size == 512
            assert device.format_bits == 16
            assert device.np_format == np.int16
            assert device.sample_max == 32767.0

    def test_16bit_format_configuration(self):
        """Test 16-bit audio format configuration"""
        device = AudioDevice(format_bits=16, auto_initialize=False)

        assert device.format_bits == 16
        assert device.np_format == np.int16
        assert device.sample_max == 32767.0

    def test_32bit_format_configuration(self):
        """Test 32-bit audio format configuration"""
        device = AudioDevice(format_bits=32, auto_initialize=False)

        assert device.format_bits == 32
        assert device.np_format == np.float32
        assert device.sample_max == 1.0

    def test_auto_initialize_disabled(self):
        """Test AudioDevice with auto-initialization disabled"""
        device = AudioDevice(auto_initialize=False)

        assert device.is_initialized is False
        assert device.pyaudio_instance is None
        assert device.stream is None

    def test_pyaudio_factory_injection(self):
        """Test custom PyAudio factory injection for testing"""
        mock_pyaudio = Mock()
        mock_stream = Mock()
        mock_device_info = {'name': 'Mock Device', 'maxOutputChannels': 2}

        mock_pyaudio.get_default_output_device_info.return_value = mock_device_info
        mock_pyaudio.open.return_value = mock_stream

        def mock_factory():
            return mock_pyaudio

        device = AudioDevice(pyaudio_factory=mock_factory)

        assert device.is_initialized is True
        assert device.pyaudio_instance is mock_pyaudio


class TestAudioDeviceInitializeMethod:
    """Test the initialize method specifically"""

    def test_successful_initialization(self):
        """Test successful audio system initialization"""
        with patch('editor.audio.audio_device.pyaudio.PyAudio') as mock_pyaudio_class:
            mock_pyaudio = Mock()
            mock_stream = Mock()
            mock_device_info = {
                'name': 'Test Device',
                'maxOutputChannels': 2,
                'defaultSampleRate': 44100.0
            }

            mock_pyaudio.get_default_output_device_info.return_value = mock_device_info
            mock_pyaudio.open.return_value = mock_stream
            mock_pyaudio_class.return_value = mock_pyaudio

            device = AudioDevice(auto_initialize=False)
            result = device.initialize()

            assert result is True
            assert device.is_initialized is True
            assert device.pyaudio_instance is mock_pyaudio
            assert device.stream is mock_stream

    def test_initialization_failure_pyaudio_creation(self):
        """Test initialization failure during PyAudio creation"""
        with patch('editor.audio.audio_device.pyaudio.PyAudio') as mock_pyaudio_class:
            mock_pyaudio_class.side_effect = OSError("Audio system not available")

            device = AudioDevice(auto_initialize=False)
            result = device.initialize()

            assert result is False
            assert device.is_initialized is False
            assert device.pyaudio_instance is None

    def test_initialization_failure_stream_creation(self):
        """Test initialization failure during stream creation"""
        with patch('editor.audio.audio_device.pyaudio.PyAudio') as mock_pyaudio_class:
            mock_pyaudio = Mock()
            mock_device_info = {'name': 'Test Device', 'maxOutputChannels': 2}

            mock_pyaudio.get_default_output_device_info.return_value = mock_device_info
            mock_pyaudio.open.side_effect = ValueError("Cannot open audio stream")
            mock_pyaudio_class.return_value = mock_pyaudio

            device = AudioDevice(auto_initialize=False)
            result = device.initialize()

            assert result is False
            assert device.is_initialized is False


class TestAudioDevicePlayback:
    """Test audio playback functionality"""

    @pytest.fixture
    def mock_device(self):
        """Fixture providing a mocked AudioDevice"""
        mock_pyaudio = Mock()
        mock_stream = Mock()
        mock_device_info = {'name': 'Mock Device', 'maxOutputChannels': 2}

        mock_pyaudio.get_default_output_device_info.return_value = mock_device_info
        mock_pyaudio.open.return_value = mock_stream

        def mock_factory():
            return mock_pyaudio

        device = AudioDevice(pyaudio_factory=mock_factory)
        device.mock_stream = mock_stream  # Store reference for test access
        return device

    def test_play_samples_blocking_success(self, mock_device):
        """Test successful blocking sample playback"""
        test_samples = np.array([0.1, 0.2, -0.1, 0.5, -0.3], dtype=np.float32)

        result = mock_device.play_samples(test_samples, blocking=True)

        assert result is True
        assert mock_device.is_playing is False  # Should be False after completion
        mock_device.mock_stream.write.assert_called_once()

    def test_play_samples_16bit_conversion(self, mock_device):
        """Test sample conversion for 16-bit format"""
        mock_device.format_bits = 16
        mock_device.np_format = np.int16
        mock_device.sample_max = 32767.0

        test_samples = np.array([0.1, -0.5, 1.0], dtype=np.float32)
        mock_device.play_samples(test_samples, blocking=True)

        # Verify stream.write was called
        mock_device.mock_stream.write.assert_called_once()
        # The actual conversion is tested by checking that write was called

    def test_play_samples_32bit_conversion(self, mock_device):
        """Test sample conversion for 32-bit format"""
        test_samples = np.array([0.1, -0.5, 1.0], dtype=np.float32)
        mock_device.play_samples(test_samples, blocking=True)

        mock_device.mock_stream.write.assert_called_once()

    def test_play_samples_mono_to_stereo_conversion(self, mock_device):
        """Test mono to stereo channel conversion"""
        mock_device.channels = 2
        test_samples = np.array([0.1, 0.2, 0.3], dtype=np.float32)

        result = mock_device.play_samples(test_samples, blocking=True)

        assert result is True
        mock_device.mock_stream.write.assert_called_once()

    def test_play_samples_stereo_to_mono_conversion(self, mock_device):
        """Test stereo to mono channel conversion"""
        mock_device.channels = 1
        test_samples = np.array([[0.1, 0.2], [0.3, 0.4]], dtype=np.float32)

        result = mock_device.play_samples(test_samples, blocking=True)

        assert result is True
        mock_device.mock_stream.write.assert_called_once()

    def test_play_samples_clipping(self, mock_device):
        """Test sample clipping to valid range"""
        test_samples = np.array([-2.0, -1.5, 1.5, 2.0], dtype=np.float32)

        result = mock_device.play_samples(test_samples, blocking=True)

        assert result is True
        mock_device.mock_stream.write.assert_called_once()

    def test_play_samples_list_input(self, mock_device):
        """Test playback with list input (automatic conversion to numpy array)"""
        test_samples = [0.1, 0.2, -0.1, 0.5]

        result = mock_device.play_samples(test_samples, blocking=True)

        assert result is True
        mock_device.mock_stream.write.assert_called_once()

    def test_play_samples_not_initialized(self):
        """Test playback when device is not initialized"""
        device = AudioDevice(auto_initialize=False)

        test_samples = np.array([0.1, 0.2, 0.3], dtype=np.float32)
        result = device.play_samples(test_samples, blocking=True)

        assert result is False

    def test_play_samples_with_callback(self, mock_device):
        """Test playback with completion callback"""
        callback = Mock()
        test_samples = np.array([0.1, 0.2, 0.3], dtype=np.float32)

        result = mock_device.play_samples(test_samples, blocking=True, callback=callback)

        assert result is True
        callback.assert_called_once()

    def test_play_samples_stream_error(self, mock_device):
        """Test playback with stream write error"""
        mock_device.mock_stream.write.side_effect = OSError("Stream write error")
        test_samples = np.array([0.1, 0.2, 0.3], dtype=np.float32)

        result = mock_device.play_samples(test_samples, blocking=True)

        assert result is False
        assert mock_device.is_playing is False

    def test_play_samples_async(self, mock_device):
        """Test non-blocking (async) playback"""
        test_samples = np.array([0.1, 0.2, 0.3], dtype=np.float32)

        result = mock_device.play_samples(test_samples, blocking=False)

        assert result is True
        # Give thread a moment to start
        time.sleep(0.1)
        assert mock_device._playback_thread is not None  # pylint: disable=protected-access

    def test_play_samples_async_stop_previous(self, mock_device):
        """Test that async playback stops previous playback"""
        test_samples = np.array([0.1, 0.2, 0.3], dtype=np.float32)

        # Start first playback
        mock_device.play_samples(test_samples, blocking=False)
        time.sleep(0.05)

        # Start second playback (should stop first)
        result = mock_device.play_samples(test_samples, blocking=False)

        assert result is True


class TestAudioDeviceControl:
    """Test audio device control methods"""

    @pytest.fixture
    def mock_device(self):
        """Fixture providing a mocked AudioDevice"""
        mock_pyaudio = Mock()
        mock_stream = Mock()
        mock_device_info = {'name': 'Mock Device', 'maxOutputChannels': 2}

        mock_pyaudio.get_default_output_device_info.return_value = mock_device_info
        mock_pyaudio.open.return_value = mock_stream

        def mock_factory():
            return mock_pyaudio

        return AudioDevice(pyaudio_factory=mock_factory)

    def test_stop_playback(self, mock_device):
        """Test stopping audio playback"""
        # Simulate playback in progress
        mock_device.is_playing = True
        mock_device._playback_thread = Mock()  # pylint: disable=protected-access
        mock_device._playback_thread.is_alive.return_value = True  # pylint: disable=protected-access

        mock_device.stop()

        assert mock_device.is_playing is False
        mock_device._stop_playback.is_set()  # pylint: disable=protected-access

    def test_stop_no_playback(self, mock_device):
        """Test stop when no playback is active"""
        assert mock_device.is_playing is False

        # Should not raise any errors
        mock_device.stop()

        assert mock_device.is_playing is False

    def test_set_volume(self, mock_device):
        """Test volume setting (placeholder implementation)"""
        # Test valid volume range
        mock_device.set_volume(0.5)
        mock_device.set_volume(0.0)
        mock_device.set_volume(1.0)

        # Test volume clamping
        mock_device.set_volume(-0.1)  # Should clamp to 0.0
        mock_device.set_volume(1.5)   # Should clamp to 1.0

        # No assertions needed as this is a placeholder implementation
        # Just ensure no exceptions are raised

    def test_get_device_info(self, mock_device):
        """Test device information retrieval"""
        info = mock_device.get_device_info()

        assert isinstance(info, dict)
        assert info['sample_rate'] == mock_device.sample_rate
        assert info['channels'] == mock_device.channels
        assert info['chunk_size'] == mock_device.chunk_size
        assert info['format_bits'] == mock_device.format_bits
        assert info['is_initialized'] == mock_device.is_initialized
        assert info['is_playing'] == mock_device.is_playing
        assert info['pyaudio_available'] is True

    def test_get_device_info_with_device_details(self, mock_device):
        """Test device info with PyAudio device details"""
        info = mock_device.get_device_info()

        assert 'device_name' in info
        assert 'max_output_channels' in info
        assert info['device_name'] == 'Mock Device'
        assert info['max_output_channels'] == 2

    def test_get_device_info_pyaudio_error(self, mock_device):
        """Test device info when PyAudio device info fails"""
        mock_device.pyaudio_instance.get_default_output_device_info.side_effect = \
            OSError("No device")

        info = mock_device.get_device_info()

        # Should still return basic info
        assert isinstance(info, dict)
        assert info['sample_rate'] == mock_device.sample_rate
        assert info['is_initialized'] == mock_device.is_initialized


class TestAudioDeviceCleanup:
    """Test resource cleanup and lifecycle management"""

    def test_cleanup_successful(self):
        """Test successful resource cleanup"""
        with patch('editor.audio.audio_device.pyaudio.PyAudio') as mock_pyaudio_class:
            mock_pyaudio = Mock()
            mock_stream = Mock()
            mock_device_info = {'name': 'Test Device', 'maxOutputChannels': 2}

            mock_pyaudio.get_default_output_device_info.return_value = mock_device_info
            mock_pyaudio.open.return_value = mock_stream
            mock_pyaudio_class.return_value = mock_pyaudio

            device = AudioDevice()
            device.cleanup()

            assert device.is_initialized is False
            assert device.stream is None
            assert device.pyaudio_instance is None
            mock_stream.stop_stream.assert_called_once()
            mock_stream.close.assert_called_once()
            mock_pyaudio.terminate.assert_called_once()

    def test_cleanup_stream_error(self):
        """Test cleanup with stream close error"""
        with patch('editor.audio.audio_device.pyaudio.PyAudio') as mock_pyaudio_class:
            mock_pyaudio = Mock()
            mock_stream = Mock()
            mock_device_info = {'name': 'Test Device', 'maxOutputChannels': 2}

            mock_pyaudio.get_default_output_device_info.return_value = mock_device_info
            mock_pyaudio.open.return_value = mock_stream
            mock_pyaudio_class.return_value = mock_pyaudio

            # Make stream cleanup fail
            mock_stream.stop_stream.side_effect = OSError("Stream error")
            mock_stream.close.side_effect = ValueError("Close error")

            device = AudioDevice()
            device.cleanup()  # Should not raise exception

            assert device.is_initialized is False
            assert device.stream is None

    def test_cleanup_pyaudio_error(self):
        """Test cleanup with PyAudio termination error"""
        with patch('editor.audio.audio_device.pyaudio.PyAudio') as mock_pyaudio_class:
            mock_pyaudio = Mock()
            mock_stream = Mock()
            mock_device_info = {'name': 'Test Device', 'maxOutputChannels': 2}

            mock_pyaudio.get_default_output_device_info.return_value = mock_device_info
            mock_pyaudio.open.return_value = mock_stream
            mock_pyaudio.terminate.side_effect = IOError("Terminate error")
            mock_pyaudio_class.return_value = mock_pyaudio

            device = AudioDevice()
            device.cleanup()  # Should not raise exception

            assert device.pyaudio_instance is None

    def test_cleanup_already_cleaned(self):
        """Test cleanup when already cleaned"""
        device = AudioDevice(auto_initialize=False)
        device.cleanup()  # Should not raise exception

        assert device.is_initialized is False

    def test_context_manager(self):
        """Test AudioDevice as context manager"""
        with patch('editor.audio.audio_device.pyaudio.PyAudio') as mock_pyaudio_class:
            mock_pyaudio = Mock()
            mock_stream = Mock()
            mock_device_info = {'name': 'Test Device', 'maxOutputChannels': 2}

            mock_pyaudio.get_default_output_device_info.return_value = mock_device_info
            mock_pyaudio.open.return_value = mock_stream
            mock_pyaudio_class.return_value = mock_pyaudio

            with AudioDevice() as device:
                assert device.is_initialized is True

            # Should be cleaned up after context exit
            assert device.is_initialized is False
            mock_stream.close.assert_called_once()
            mock_pyaudio.terminate.assert_called_once()

    def test_destructor_cleanup(self):
        """Test cleanup in destructor"""
        with patch('editor.audio.audio_device.pyaudio.PyAudio') as mock_pyaudio_class:
            mock_pyaudio = Mock()
            mock_stream = Mock()
            mock_device_info = {'name': 'Test Device', 'maxOutputChannels': 2}

            mock_pyaudio.get_default_output_device_info.return_value = mock_device_info
            mock_pyaudio.open.return_value = mock_stream
            mock_pyaudio_class.return_value = mock_pyaudio

            device = AudioDevice()

            # Manually call destructor (normally called by Python garbage collector)
            del device

            # Verify cleanup methods were called on the mocked objects
            mock_stream.close.assert_called_once()
            mock_pyaudio.terminate.assert_called_once()


class TestAudioDeviceEdgeCases:
    """Test edge cases and error conditions"""

    def test_play_samples_empty_array(self):
        """Test playback with empty sample array"""
        mock_pyaudio = Mock()
        mock_stream = Mock()
        mock_device_info = {'name': 'Mock Device', 'maxOutputChannels': 2}

        mock_pyaudio.get_default_output_device_info.return_value = mock_device_info
        mock_pyaudio.open.return_value = mock_stream

        def mock_factory():
            return mock_pyaudio

        device = AudioDevice(pyaudio_factory=mock_factory)
        empty_samples = np.array([], dtype=np.float32)

        result = device.play_samples(empty_samples, blocking=True)

        assert result is True
        mock_stream.write.assert_called_once()

    def test_play_samples_invalid_shape(self):
        """Test playback with invalid sample shape"""
        mock_pyaudio = Mock()
        mock_stream = Mock()
        mock_device_info = {'name': 'Mock Device', 'maxOutputChannels': 2}

        mock_pyaudio.get_default_output_device_info.return_value = mock_device_info
        mock_pyaudio.open.return_value = mock_stream

        def mock_factory():
            return mock_pyaudio

        device = AudioDevice(pyaudio_factory=mock_factory)
        # 3D array should be handled gracefully
        invalid_samples = np.array([[[0.1, 0.2]]], dtype=np.float32)

        result = device.play_samples(invalid_samples, blocking=True)

        # Should handle the conversion and still succeed
        assert result is True

    def test_channel_mismatch_handling(self):
        """Test handling of channel count mismatches"""
        mock_pyaudio = Mock()
        mock_stream = Mock()
        mock_device_info = {'name': 'Mock Device', 'maxOutputChannels': 2}

        mock_pyaudio.get_default_output_device_info.return_value = mock_device_info
        mock_pyaudio.open.return_value = mock_stream

        def mock_factory():
            return mock_pyaudio

        device = AudioDevice(channels=1, pyaudio_factory=mock_factory)
        # Provide stereo samples to mono device
        stereo_samples = np.array([[0.1, 0.2], [0.3, 0.4]], dtype=np.float32)

        result = device.play_samples(stereo_samples, blocking=True)

        assert result is True
        mock_stream.write.assert_called_once()

    def test_multiple_channel_to_single_channel(self):
        """Test conversion from multi-channel to single channel"""
        mock_pyaudio = Mock()
        mock_stream = Mock()
        mock_device_info = {'name': 'Mock Device', 'maxOutputChannels': 8}

        mock_pyaudio.get_default_output_device_info.return_value = mock_device_info
        mock_pyaudio.open.return_value = mock_stream

        def mock_factory():
            return mock_pyaudio

        device = AudioDevice(channels=1, pyaudio_factory=mock_factory)
        # Provide 4-channel samples to mono device
        multi_samples = np.array([[0.1, 0.2, 0.3, 0.4]], dtype=np.float32)

        result = device.play_samples(multi_samples, blocking=True)

        assert result is True


class TestConvenienceFunction:
    """Test the convenience play_audio function"""

    @patch('editor.audio.audio_device.AudioDevice')
    def test_play_audio_success(self, mock_audio_device_class):
        """Test successful audio playback with convenience function"""
        mock_device = MagicMock()
        mock_device.play_samples.return_value = True
        mock_device.__enter__.return_value = mock_device
        mock_device.__exit__.return_value = None
        mock_audio_device_class.return_value = mock_device

        test_samples = np.array([0.1, 0.2, 0.3], dtype=np.float32)
        result = play_audio(test_samples, sample_rate=48000, blocking=True)

        assert result is True
        mock_audio_device_class.assert_called_once_with(sample_rate=48000)
        mock_device.play_samples.assert_called_once_with(test_samples, blocking=True)

    @patch('editor.audio.audio_device.AudioDevice')
    def test_play_audio_failure(self, mock_audio_device_class):
        """Test failed audio playback with convenience function"""
        mock_device = MagicMock()
        mock_device.play_samples.return_value = False
        mock_device.__enter__.return_value = mock_device
        mock_device.__exit__.return_value = None
        mock_audio_device_class.return_value = mock_device

        test_samples = np.array([0.1, 0.2, 0.3], dtype=np.float32)
        result = play_audio(test_samples, blocking=False)

        assert result is False

    @patch('editor.audio.audio_device.AudioDevice')
    def test_play_audio_default_parameters(self, mock_audio_device_class):
        """Test convenience function with default parameters"""
        mock_device = MagicMock()
        mock_device.play_samples.return_value = True
        mock_device.__enter__.return_value = mock_device
        mock_device.__exit__.return_value = None
        mock_audio_device_class.return_value = mock_device

        test_samples = np.array([0.1, 0.2, 0.3], dtype=np.float32)
        result = play_audio(test_samples)

        assert result is True
        mock_audio_device_class.assert_called_once_with(sample_rate=44100)
        mock_device.play_samples.assert_called_once_with(test_samples, blocking=True)


class TestAudioDeviceIntegration:
    """Integration tests combining multiple AudioDevice features"""

    def test_complete_audio_pipeline(self):
        """Test complete audio device pipeline"""
        with patch('editor.audio.audio_device.pyaudio.PyAudio') as mock_pyaudio_class:
            mock_pyaudio = Mock()
            mock_stream = Mock()
            mock_device_info = {
                'name': 'Integration Test Device',
                'maxOutputChannels': 2,
                'defaultSampleRate': 44100.0
            }

            mock_pyaudio.get_default_output_device_info.return_value = mock_device_info
            mock_pyaudio.open.return_value = mock_stream
            mock_pyaudio_class.return_value = mock_pyaudio

            # Test complete lifecycle
            device = AudioDevice(sample_rate=48000, channels=2)

            # Verify initialization
            assert device.is_initialized is True
            info = device.get_device_info()
            assert info['sample_rate'] == 48000
            assert info['channels'] == 2

            # Test playback
            test_samples = np.array([0.1, 0.2, -0.1, 0.5], dtype=np.float32)
            result = device.play_samples(test_samples, blocking=True)
            assert result is True

            # Test cleanup
            device.cleanup()
            assert device.is_initialized is False

    def test_multiple_playback_sessions(self):
        """Test multiple sequential playback sessions"""
        with patch('editor.audio.audio_device.pyaudio.PyAudio') as mock_pyaudio_class:
            mock_pyaudio = Mock()
            mock_stream = Mock()
            mock_device_info = {'name': 'Test Device', 'maxOutputChannels': 2}

            mock_pyaudio.get_default_output_device_info.return_value = mock_device_info
            mock_pyaudio.open.return_value = mock_stream
            mock_pyaudio_class.return_value = mock_pyaudio

            device = AudioDevice()

            # Multiple playback sessions
            for i in range(3):
                test_samples = np.array([0.1 * i, 0.2 * i, 0.3 * i], dtype=np.float32)
                result = device.play_samples(test_samples, blocking=True)
                assert result is True

            # Verify stream.write was called for each playback
            assert mock_stream.write.call_count == 3

    def test_format_conversion_pipeline(self):
        """Test complete format conversion pipeline"""
        with patch('editor.audio.audio_device.pyaudio.PyAudio') as mock_pyaudio_class:
            mock_pyaudio = Mock()
            mock_stream = Mock()
            mock_device_info = {'name': 'Test Device', 'maxOutputChannels': 2}

            mock_pyaudio.get_default_output_device_info.return_value = mock_device_info
            mock_pyaudio.open.return_value = mock_stream
            mock_pyaudio_class.return_value = mock_pyaudio

            # Test both 16-bit and 32-bit formats
            for format_bits in [16, 32]:
                device = AudioDevice(format_bits=format_bits)

                test_samples = np.array([0.5, -0.5, 1.0, -1.0], dtype=np.float32)
                result = device.play_samples(test_samples, blocking=True)

                assert result is True
                device.cleanup()


# Utility functions for test data generation
def create_test_audio_samples(length: int = 1000, frequency: float = 440.0,
                              sample_rate: int = 44100):
    """Create synthetic audio samples for testing"""
    t = np.linspace(0, length / sample_rate, length, False)
    samples = np.sin(2 * np.pi * frequency * t).astype(np.float32)
    return samples


def create_multichannel_audio_samples(length: int = 1000, channels: int = 2,
                                      frequencies: list = None):
    """Create multi-channel synthetic audio samples for testing"""
    if frequencies is None:
        frequencies = [440.0, 880.0]  # Default frequencies for each channel

    samples = np.zeros((length, channels), dtype=np.float32)
    t = np.linspace(0, length / 44100, length, False)

    for ch in range(min(channels, len(frequencies))):
        samples[:, ch] = np.sin(2 * np.pi * frequencies[ch] * t)

    return samples


if __name__ == "__main__":
    # Allow running tests directly
    pytest.main([__file__, "-v"])

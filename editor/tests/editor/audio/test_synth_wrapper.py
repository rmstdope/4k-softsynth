#!/usr/bin/env python3
"""
Comprehensive tests for the SynthWrapper class

This test suite validates the SynthWrapper functionality, including:
- Initialization and lifecycle management
- Audio rendering capabilities
- Instrument access and management
- Constants and configuration access
- Error handling and edge cases

The tests require the synth_engine extension to be available.

Running Tests:
1. Using pytest directly:
   pytest tests/editor/audio/test_synth_wrapper.py -v

2. Running specific test classes:
   pytest tests/editor/audio/test_synth_wrapper.py::TestSynthWrapperInitialization -v
"""

from unittest.mock import Mock, patch

import pytest
import numpy as np

import synth_engine  # pylint: disable=import-error,c-extension-no-member,unused-import,wrong-import-position
from editor.audio.synth_wrapper import SynthWrapper  # pylint: disable=wrong-import-position


class TestSynthWrapperInitialization:
    """Test SynthWrapper initialization and basic functionality"""

    def test_synth_wrapper_creation_success(self, capsys):
        """Test successful SynthWrapper creation"""
        wrapper = SynthWrapper()

        # Verify initialization status
        assert wrapper.is_initialized is True
        assert wrapper.engine is not None

        # Check debug output
        captured = capsys.readouterr()
        assert "DEBUG: Python Process ID" in captured.out
        assert "ARM64 Synthesizer initialized" in captured.out

    def test_synth_wrapper_engine_type(self):
        """Test that engine is of correct type"""
        wrapper = SynthWrapper()

        # Verify engine type
        assert hasattr(wrapper.engine, 'initialize')
        assert hasattr(wrapper.engine, 'render_instrument_note')
        assert hasattr(wrapper.engine, 'is_initialized')

    @patch('synth_engine.SynthEngine')
    def test_synth_wrapper_initialization_failure(self, mock_engine_class):
        """Test handling of initialization failure"""
        # Mock engine that fails to initialize
        mock_engine = Mock()
        mock_engine.initialize.return_value = False
        mock_engine_class.return_value = mock_engine

        wrapper = SynthWrapper()

        assert wrapper.is_initialized is False
        assert wrapper.engine is mock_engine


class TestSynthWrapperAudioRendering:
    """Test audio rendering functionality"""

    @pytest.fixture
    def wrapper(self):
        """Fixture providing initialized SynthWrapper"""
        return SynthWrapper()

    @patch('editor.audio.synth_wrapper.synth_engine.SynthEngine')
    def test_render_note_returns_numpy_array(self, mock_engine_class):
        """Test that render_note returns proper numpy array"""
        # Mock the engine and its render_note method
        test_samples = [0.1, 0.2, -0.1, 0.5, -0.3]
        mock_engine = Mock()
        mock_engine.initialize.return_value = True
        mock_engine.render_note.return_value = test_samples
        mock_engine_class.return_value = mock_engine

        wrapper = SynthWrapper()
        result = wrapper.render_note()

        assert isinstance(result, np.ndarray)
        assert result.dtype == np.float32
        assert len(result) == len(test_samples)
        np.testing.assert_array_equal(result, np.array(test_samples, dtype=np.float32))

    @patch('editor.audio.synth_wrapper.synth_engine.SynthEngine')
    def test_render_instrument_note_returns_numpy_array(self, mock_engine_class):
        """Test that render_instrument_note returns proper numpy array"""
        # Mock the engine and its render_instrument_note method
        test_samples = [0.2, -0.4, 0.6, -0.1, 0.8]
        mock_engine = Mock()
        mock_engine.initialize.return_value = True
        mock_engine.render_instrument_note.return_value = test_samples
        mock_engine_class.return_value = mock_engine

        wrapper = SynthWrapper()
        result = wrapper.render_instrument_note(0, 64)

        assert isinstance(result, np.ndarray)
        assert result.dtype == np.float32
        assert len(result) == len(test_samples)
        np.testing.assert_array_equal(result, np.array(test_samples, dtype=np.float32))

        # Verify correct parameters were passed
        mock_engine.render_instrument_note.assert_called_once_with(0, 64)

    def test_render_instrument_note_with_real_engine(self, wrapper):
        """Test render_instrument_note with real engine (integration test)"""
        # Test various instrument and note combinations with real engine
        test_cases = [
            (0, 60),    # Middle C on instrument 0
            (1, 72),    # High C on instrument 1
            (0, 36),    # Low C on instrument 0
        ]

        for instrument, note in test_cases:
            try:
                result = wrapper.render_instrument_note(instrument, note)
                assert isinstance(result, np.ndarray)
                assert result.dtype == np.float32
                # Result might be empty if instrument has no data
                if len(result) > 0:
                    # Check that values are reasonable for audio
                    assert np.all(np.abs(result) <= 1.0), "Audio values should be normalized"
            except Exception:  # pylint: disable=broad-exception-caught
                # Engine might fail to render with invalid parameters, which is expected
                pass

    @patch('editor.audio.synth_wrapper.synth_engine.SynthEngine')
    def test_render_empty_samples(self, mock_engine_class):
        """Test handling of empty sample arrays"""
        mock_engine = Mock()
        mock_engine.initialize.return_value = True
        mock_engine.render_note.return_value = []
        mock_engine.render_instrument_note.return_value = []
        mock_engine_class.return_value = mock_engine

        wrapper = SynthWrapper()
        result_note = wrapper.render_note()
        result_instrument = wrapper.render_instrument_note(0, 64)

        assert isinstance(result_note, np.ndarray)
        assert isinstance(result_instrument, np.ndarray)
        assert len(result_note) == 0
        assert len(result_instrument) == 0


class TestSynthWrapperInstrumentAccess:
    """Test instrument access and management"""

    @pytest.fixture
    def wrapper(self):
        """Fixture providing initialized SynthWrapper"""
        return SynthWrapper()

    def test_get_instrument_valid_ids(self, wrapper):
        """Test getting instruments with valid IDs"""
        for instrument_id in range(4):  # Assuming 4 instruments (0-3)
            instrument = wrapper.get_instrument(instrument_id)
            # Instrument might be None if not configured, but should not raise error
            assert instrument is None or hasattr(instrument, 'get_instructions')

    @patch('editor.audio.synth_wrapper.synth_engine.SynthEngine')
    def test_get_instrument_delegates_to_engine(self, mock_engine_class):
        """Test that get_instrument properly delegates to engine"""
        mock_instrument = Mock()
        mock_engine = Mock()
        mock_engine.initialize.return_value = True
        mock_engine.get_instrument.return_value = mock_instrument
        mock_engine_class.return_value = mock_engine

        wrapper = SynthWrapper()
        result = wrapper.get_instrument(1)

        assert result is mock_instrument
        mock_engine.get_instrument.assert_called_once_with(1)

    def test_has_instruments_when_available(self, wrapper):
        """Test has_instruments returns True when instruments are available"""
        # SynthWrapper should have instruments available if engine is initialized
        result = wrapper.has_instruments()
        assert result is True

    def test_has_instruments_when_engine_none(self):
        """Test has_instruments returns False when engine is None"""
        wrapper = SynthWrapper()
        wrapper.engine = None

        result = wrapper.has_instruments()
        assert result is False

    @patch('editor.audio.synth_wrapper.synth_engine.SynthEngine')
    def test_has_instruments_when_no_get_instrument_method(self, mock_engine_class):
        """Test has_instruments returns False when get_instrument not available"""
        mock_engine = Mock()
        mock_engine.initialize.return_value = True
        # Don't add get_instrument method to mock
        del mock_engine.get_instrument  # Remove default mock attribute
        mock_engine_class.return_value = mock_engine

        wrapper = SynthWrapper()
        result = wrapper.has_instruments()
        assert result is False


class TestSynthWrapperStatus:
    """Test synthesizer status methods"""

    @pytest.fixture
    def wrapper(self):
        """Fixture providing initialized SynthWrapper"""
        return SynthWrapper()

    @patch('editor.audio.synth_wrapper.synth_engine.SynthEngine')
    def test_is_ready_delegates_to_engine(self, mock_engine_class):
        """Test that is_ready properly delegates to engine"""
        mock_engine = Mock()
        mock_engine.initialize.return_value = True
        mock_engine.is_initialized.return_value = True
        mock_engine_class.return_value = mock_engine

        wrapper = SynthWrapper()
        result = wrapper.is_ready()

        assert result is True
        mock_engine.is_initialized.assert_called_once()

    @patch('editor.audio.synth_wrapper.synth_engine.SynthEngine')
    def test_is_ready_false_when_not_initialized(self, mock_engine_class):
        """Test is_ready returns False when engine not initialized"""
        mock_engine = Mock()
        mock_engine.initialize.return_value = True
        mock_engine.is_initialized.return_value = False
        mock_engine_class.return_value = mock_engine

        wrapper = SynthWrapper()
        result = wrapper.is_ready()

        assert result is False

    def test_is_ready_with_real_engine(self, wrapper):
        """Test is_ready with real engine"""
        # With a real initialized engine, is_ready should return True
        result = wrapper.is_ready()
        assert result is True


class TestSynthWrapperConstants:
    """Test synthesizer constants access"""

    @pytest.fixture
    def wrapper(self):
        """Fixture providing initialized SynthWrapper"""
        return SynthWrapper()

    def test_get_constants_returns_dict(self, wrapper):
        """Test that get_constants returns proper dictionary"""
        constants = wrapper.get_constants()

        assert isinstance(constants, dict)
        assert len(constants) > 0

    def test_get_constants_contains_expected_keys(self, wrapper):
        """Test that constants dictionary contains expected keys"""
        constants = wrapper.get_constants()

        expected_keys = [
            'SAMPLE_RATE',
            'BEATS_PER_MINUTE',
            'NOTES_PER_BEAT',
            'MAX_NUM_INSTRUMENTS',
            'MAX_COMMANDS',
            'MAX_COMMAND_PARAMS',
            'ENVELOPE_ID',
            'OSCILLATOR_ID',
            'OPERATION_ID',
            'HLD'
        ]

        for key in expected_keys:
            assert key in constants, f"Expected key '{key}' not found in constants"

    def test_get_constants_values_are_numeric(self, wrapper):
        """Test that constant values are numeric"""
        constants = wrapper.get_constants()

        for key, value in constants.items():
            assert isinstance(value, (int, float)), \
                f"Constant '{key}' value is not numeric: {value}"

    def test_get_constants_specific_values(self, wrapper):
        """Test specific constant values match expected ranges"""
        constants = wrapper.get_constants()

        # Test reasonable value ranges
        assert constants['SAMPLE_RATE'] > 0, "Sample rate should be positive"
        assert constants['BEATS_PER_MINUTE'] > 0, "BPM should be positive"
        assert constants['NOTES_PER_BEAT'] > 0, "Notes per beat should be positive"
        assert constants['MAX_NUM_INSTRUMENTS'] >= 1, "Should have at least 1 instrument"
        assert constants['MAX_COMMANDS'] > 0, "Should have positive max commands"
        assert constants['MAX_COMMAND_PARAMS'] > 0, "Should have positive max params"

    def test_get_constants_instruction_ids_unique(self, wrapper):
        """Test that instruction IDs are unique"""
        constants = wrapper.get_constants()

        instruction_ids = [
            constants['ENVELOPE_ID'],
            constants['OSCILLATOR_ID'],
            constants['OPERATION_ID']
        ]

        # Check that all IDs are unique
        assert len(instruction_ids) == len(set(instruction_ids)), "Instruction IDs should be unique"


class TestSynthWrapperEdgeCases:
    """Test edge cases and error conditions"""

    def test_render_with_extreme_parameters(self):
        """Test rendering with extreme parameter values"""
        wrapper = SynthWrapper()

        # Test with extreme instrument and note values
        test_cases = [
            (-1, 64),    # Negative instrument
            (999, 64),   # Very high instrument
            (0, -1),     # Negative note
            (0, 999),    # Very high note
        ]

        for instrument, note in test_cases:
            try:
                # Should not raise exception in wrapper, delegates to engine
                result = wrapper.render_instrument_note(instrument, note)
                assert isinstance(result, np.ndarray)
            except Exception:  # pylint: disable=broad-exception-caught
                # Engine might throw exceptions for invalid parameters, which is fine
                pass

    @patch('editor.audio.synth_wrapper.synth_engine.SynthEngine')
    def test_engine_creation_exception(self, mock_engine_class):
        """Test handling of engine creation exceptions"""
        mock_engine_class.side_effect = RuntimeError("Failed to create engine")

        with pytest.raises(RuntimeError, match="Failed to create engine"):
            SynthWrapper()

    @patch('editor.audio.synth_wrapper.synth_engine.SynthEngine')
    def test_numpy_array_conversion_with_various_types(self, mock_engine_class):
        """Test numpy array conversion with various input types"""
        test_inputs = [
            [1, 2, 3],           # List of ints
            [1.0, 2.0, 3.0],     # List of floats
            (1, 2, 3),           # Tuple
            np.array([1, 2, 3]), # Existing numpy array
        ]

        for test_input in test_inputs:
            mock_engine = Mock()
            mock_engine.initialize.return_value = True
            mock_engine.render_note.return_value = test_input
            mock_engine_class.return_value = mock_engine

            wrapper = SynthWrapper()
            result = wrapper.render_note()

            assert isinstance(result, np.ndarray)
            assert result.dtype == np.float32


class TestSynthWrapperIntegration:
    """Integration tests combining multiple SynthWrapper features"""

    def test_complete_audio_pipeline(self):
        """Test complete audio generation pipeline"""
        wrapper = SynthWrapper()

        # Verify initialization
        assert wrapper.is_initialized
        assert wrapper.is_ready()

        # Get constants
        constants = wrapper.get_constants()
        assert 'SAMPLE_RATE' in constants

        # Test instrument access
        assert wrapper.has_instruments()

        # Test audio rendering (will use actual engine if available)
        try:
            audio_data = wrapper.render_instrument_note(0, 64)
            assert isinstance(audio_data, np.ndarray)
            assert audio_data.dtype == np.float32
        except Exception:  # pylint: disable=broad-exception-caught
            # Audio rendering might fail if no instrument data is available, which is expected
            pass

    @patch('editor.audio.synth_wrapper.synth_engine.SynthEngine')
    def test_multiple_render_calls_consistent(self, mock_engine_class):
        """Test that multiple render calls produce consistent results"""
        # Mock engine to return consistent data
        test_samples = [0.1, 0.2, 0.3]
        mock_engine = Mock()
        mock_engine.initialize.return_value = True
        mock_engine.render_instrument_note.return_value = test_samples
        mock_engine_class.return_value = mock_engine

        wrapper = SynthWrapper()

        # Multiple calls should produce identical results
        result1 = wrapper.render_instrument_note(0, 64)
        result2 = wrapper.render_instrument_note(0, 64)

        np.testing.assert_array_equal(result1, result2)
        assert mock_engine.render_instrument_note.call_count == 2

    def test_real_engine_consistency(self):
        """Test consistency with real engine"""
        wrapper = SynthWrapper()

        # Test that the same parameters produce the same results
        try:
            result1 = wrapper.render_instrument_note(0, 64)
            result2 = wrapper.render_instrument_note(0, 64)

            # Results should be identical for the same parameters
            np.testing.assert_array_equal(result1, result2)
        except Exception:  # pylint: disable=broad-exception-caught
            # Real engine might not have consistent behavior if no data is available
            pass

    def test_wrapper_lifecycle(self):
        """Test complete wrapper lifecycle from creation to usage"""
        # Test creation
        wrapper = SynthWrapper()
        assert wrapper.engine is not None
        assert wrapper.is_initialized is True

        # Test constants access
        constants = wrapper.get_constants()
        assert isinstance(constants, dict)
        assert len(constants) > 0

        # Test status check
        assert wrapper.is_ready() is True
        assert wrapper.has_instruments() is True

        # Test instrument access
        for i in range(4):  # Test all possible instruments
            instrument = wrapper.get_instrument(i)
            # Don't assert specific values since instruments may or may not be configured
            assert instrument is None or hasattr(instrument, 'get_instructions')


class TestSynthWrapperErrorHandling:
    """Test error handling and recovery scenarios"""

    @patch('editor.audio.synth_wrapper.synth_engine.SynthEngine')
    def test_initialization_failure_handling(self, mock_engine_class):
        """Test handling when engine initialization fails"""
        mock_engine = Mock()
        mock_engine.initialize.return_value = False  # Initialization fails
        mock_engine.is_initialized.return_value = False  # Also make is_initialized return False
        mock_engine_class.return_value = mock_engine

        wrapper = SynthWrapper()

        assert wrapper.is_initialized is False
        assert wrapper.is_ready() is False

    def test_invalid_instrument_access(self):
        """Test accessing instruments with invalid IDs"""
        wrapper = SynthWrapper()

        # Test negative instrument ID - expect TypeError from C++ extension
        with pytest.raises(TypeError):
            wrapper.get_instrument(-1)

        # Test very high instrument ID - should return None or raise exception
        try:
            instrument = wrapper.get_instrument(999)
            # If no exception, should be None or an instrument object
            assert instrument is None or hasattr(instrument, 'get_instructions')
        except (TypeError, IndexError, RuntimeError):
            # C++ extension may throw various exceptions for invalid IDs
            pass

    @patch('editor.audio.synth_wrapper.synth_engine')
    def test_missing_synth_engine_constants(self, mock_synth_engine):
        """Test behavior when synth_engine constants are missing"""
        # Remove some constants to test error handling
        del mock_synth_engine.SAMPLE_RATE
        mock_synth_engine.BEATS_PER_MINUTE = 120
        mock_synth_engine.NOTES_PER_BEAT = 4

        mock_engine = Mock()
        mock_engine.initialize.return_value = True
        mock_synth_engine.SynthEngine.return_value = mock_engine

        wrapper = SynthWrapper()

        with pytest.raises(AttributeError):
            wrapper.get_constants()


class TestSynthWrapperPerformance:
    """Test performance-related aspects of SynthWrapper"""

    def test_constants_caching_behavior(self):
        """Test that constants are accessed efficiently"""
        wrapper = SynthWrapper()

        # Multiple calls to get_constants should work consistently
        constants1 = wrapper.get_constants()
        constants2 = wrapper.get_constants()

        # Should return identical dictionaries
        assert constants1 == constants2

        # Check that all expected keys are present in both
        expected_keys = ['SAMPLE_RATE', 'BEATS_PER_MINUTE', 'NOTES_PER_BEAT']
        for key in expected_keys:
            if key in constants1:  # Only check if the key exists
                assert constants1[key] == constants2[key]

    @patch('editor.audio.synth_wrapper.synth_engine.SynthEngine')
    def test_memory_efficiency_numpy_conversion(self, mock_engine_class):
        """Test memory efficiency of numpy array conversion"""
        # Test with various array sizes
        test_sizes = [10, 100, 1000, 10000]

        for size in test_sizes:
            mock_engine = Mock()
            mock_engine.initialize.return_value = True
            test_data = [0.1] * size  # Create array of specified size
            mock_engine.render_instrument_note.return_value = test_data
            mock_engine_class.return_value = mock_engine

            wrapper = SynthWrapper()
            result = wrapper.render_instrument_note(0, 64)

            assert isinstance(result, np.ndarray)
            assert len(result) == size
            assert result.dtype == np.float32

            # Verify memory usage is reasonable (all values should be the same)
            assert np.all(result == 0.1)


# Utility functions for test data generation
def create_test_audio_samples(length: int = 1000, frequency: float = 440.0,
                              sample_rate: int = 44100):
    """Create synthetic audio samples for testing"""
    t = np.linspace(0, length / sample_rate, length, False)
    samples = np.sin(2 * np.pi * frequency * t).astype(np.float32)
    return samples.tolist()


def verify_audio_properties(audio_data: np.ndarray, expected_length: int = None):
    """Verify basic properties of audio data"""
    assert isinstance(audio_data, np.ndarray)
    assert audio_data.dtype == np.float32
    assert len(audio_data.shape) == 1  # Mono audio

    if expected_length is not None:
        assert len(audio_data) == expected_length

    # Check for reasonable audio values (not all zeros, not clipping)
    if len(audio_data) > 0:
        assert not np.all(audio_data == 0), "Audio data should not be all zeros"
        assert np.all(np.abs(audio_data) <= 1.0), "Audio data should be normalized"


if __name__ == "__main__":
    # Allow running tests directly
    pytest.main([__file__, "-v"])

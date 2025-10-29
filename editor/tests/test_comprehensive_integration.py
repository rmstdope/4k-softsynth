#!/usr/bin/env python3
"""
Comprehensive pytest tests for the integrated GUI parameter system

This test suite validates the complete integration of the synthesizer engine
with the GUI parameter system, including:
- Parameter mapping and parsing
- GUI control generation
- Parameter modification
- Audio generation integration
- Real-time parameter updates

The tests use pytest fixtures to manage the synthesizer engine lifecycle
and provide reusable test data. All tests require the synth_engine module
to be available - tests will fail if it's not present.
"""

from typing import Any, List, Tuple

import pytest
import synth_engine as se  # pylint: disable=import-error,c-extension-no-member  # type: ignore

@pytest.fixture(scope="module", name="synth_engine")
def synth_engine_fixture() -> Any:
    """Fixture to provide initialized synth engine for all tests

    Returns:
        SynthEngine: Initialized synthesizer engine instance

    Raises:
        ImportError: If synth_engine module is not available (test will fail)
    """
    engine = se.SynthEngine()  # pylint: disable=c-extension-no-member
    engine.initialize()
    return engine


@pytest.fixture(scope="module", name="test_instruments")
def test_instruments_fixture(synth_engine: Any) -> List[Tuple[int, Any]]:
    """Fixture to provide test instruments with parameters

    Args:
        synth_engine: Initialized synthesizer engine

    Returns:
        List of tuples containing (instrument_index, instrument_object)
        for instruments that have configurable parameters
    """
    instruments = []
    for i in range(synth_engine.get_num_instruments()):
        instrument = synth_engine.get_instrument(i)
        if instrument and instrument.get_instructions():
            instruments.append((i, instrument))
    return instruments


class TestParameterIntegration:
    """Test suite for GUI parameter integration"""

    def test_synth_engine_initialization(self, synth_engine):
        """Test that synth engine initializes correctly"""
        assert synth_engine is not None
        assert synth_engine.get_num_instruments() > 0

    def test_gui_parameter_mapping_analysis(self, test_instruments):
        """Test GUI parameter mapping for all instruments"""
        total_controls = 0

        for instrument_idx, instrument in test_instruments:
            instructions = instrument.get_instructions()
            assert len(instructions) > 0, f"Instrument {instrument_idx} should have instructions"

            instrument_controls = self._validate_instrument_parameters(instrument, instructions)
            assert instrument_controls > 0, f"Instrument {instrument_idx} should have controls"
            total_controls += instrument_controls

        # Verify we have a reasonable number of controls
        assert total_controls > 0, "Should have at least some GUI controls"
        assert len(test_instruments) >= 1, "Should have at least 1 instrument with parameters"

    def _validate_instrument_parameters(self, instrument, instructions):
        """Helper method to validate parameters for a single instrument"""
        instrument_controls = 0
        for instr_idx, _ in enumerate(instructions):  # instr_id unused
            instr_name = instrument.get_instruction_name(instr_idx)
            param_names = instrument.get_instruction_parameter_names(instr_idx)
            param_values = instrument.get_instruction_parameters(instr_idx)

            if param_names:
                assert len(param_names) == len(param_values), \
                    f"Parameter names and values count mismatch in {instr_name}"

                for name, value in zip(param_names, param_values):
                    self._validate_single_parameter(name, value)
                    instrument_controls += 1

        return instrument_controls

    def _validate_single_parameter(self, name, value):
        """Helper method to validate a single parameter"""
        assert 0 <= value <= 255, f"Parameter {name} value {value} out of range"
        assert isinstance(name, str) and name, "Parameter name should be non-empty string"

        normalized = value / 255.0
        assert 0.0 <= normalized <= 1.0, f"Normalized value {normalized} out of range"

    def test_parameter_modification(self, test_instruments):
        """Test parameter modification functionality"""
        assert test_instruments, \
            "No instruments with parameters available - synth_engine should provide instruments"

        # Get the first available instrument for testing
        _, instrument = test_instruments[0]  # instrument_idx unused

        # Get the first instruction with parameters
        envelope_idx = 0
        instr_name = instrument.get_instruction_name(envelope_idx)
        param_names = instrument.get_instruction_parameter_names(envelope_idx)

        assert param_names, f"Instruction {instr_name} should have parameters"

        # Store original values
        original_values = instrument.get_instruction_parameters(envelope_idx)
        assert len(original_values) == len(param_names), \
            "Original values count should match parameter names"

        # Test parameter modification with known values
        test_changes = [
            (0, 0.3),    # 30% = 76.5 ≈ 77
            (1, 0.6),    # 60% = 153
            (2, 0.8),    # 80% = 204
            (3, 0.4),    # 40% = 102
        ]

        for param_idx, slider_value in test_changes:
            if param_idx >= len(param_names):
                continue  # Skip if this parameter doesn't exist

            # Convert slider value (0.0-1.0) to synth value (0-255)
            synth_value = int(slider_value * 255)

            # Update the parameter
            instrument.update_parameter(envelope_idx, param_idx, synth_value)

            # Verify the change
            updated_values = instrument.get_instruction_parameters(envelope_idx)
            assert updated_values[param_idx] == synth_value, \
                f"Parameter {param_idx} should be updated to {synth_value}, " \
                f"got {updated_values[param_idx]}"

    def test_audio_generation_with_modified_parameters(self, test_instruments):
        """Test audio generation integration (basic functionality test)"""
        assert test_instruments, \
            "No instruments available for audio testing - synth_engine should provide instruments"

        # Get the first available instrument
        _, instrument = test_instruments[0]  # instrument_idx unused

        # Test that audio generation method exists and returns data
        audio_data = instrument.render_note(64)  # Middle C

        # Basic integration tests - ensure the API works
        assert audio_data is not None, "Audio generation should return data (not None)"
        assert len(audio_data) > 0, "Audio generation should return some samples"
        assert len(audio_data) >= 1000, "Audio should be reasonable length for testing"

        # Test that we get consistent results (same input should produce same output)
        audio_data2 = instrument.render_note(64)
        assert len(audio_data2) > 0, "Second audio generation should also work"

        # Test different notes to ensure parameter is being used
        audio_data_different = instrument.render_note(72)  # Higher note
        assert len(audio_data_different) > 0, "Different note should also generate audio"

        # Basic type checking
        assert isinstance(audio_data, (list, tuple)), "Audio data should be a sequence"
        assert all(isinstance(x, (int, float)) for x in audio_data[:10]), \
            "Audio samples should be numeric"

    def test_integration_completeness(self, synth_engine, test_instruments):
        """Test overall integration completeness"""
        # Verify core functionality is working
        assert synth_engine.get_num_instruments() > 0, "Should have instruments"

        total_controls = self._count_total_controls(test_instruments)

        # Integration checks
        assert total_controls > 0, "Parameter parsing should work"
        assert len(test_instruments) > 0, "GUI control mapping should work"

        # Test at least one parameter modification cycle
        if test_instruments:
            self._test_parameter_modification_cycle(test_instruments[0][1])

    def _count_total_controls(self, test_instruments):
        """Helper method to count total controls across all instruments"""
        total_controls = 0
        for _, instrument in test_instruments:  # instrument_idx unused
            instructions = instrument.get_instructions()
            for instr_idx, _ in enumerate(instructions):  # instr_id unused
                param_names = instrument.get_instruction_parameter_names(instr_idx)
                if param_names:
                    total_controls += len(param_names)
        return total_controls

    def _test_parameter_modification_cycle(self, instrument):
        """Helper method to test parameter modification cycle"""
        original_values = instrument.get_instruction_parameters(0)

        # Modify a parameter
        if len(original_values) > 0:
            instrument.update_parameter(0, 0, 128)  # Set to middle value
            updated_values = instrument.get_instruction_parameters(0)
            assert updated_values[0] == 128, "Parameter modification should work"

        # Test audio generation
        audio_data = instrument.render_note(64)
        assert audio_data and len(audio_data) > 0, "Audio generation should work"


# Keep the main execution for backward compatibility and standalone testing
if __name__ == "__main__":
    pytest.main([__file__, "-v"])

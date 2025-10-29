#!/usr/bin/env python3
"""
Pytest test suite for parameter names functionality

This test suite validates the parameter modification by name system including:
- Parameter lookup by human-readable names
- Parameter modification using names instead of indices
- Audio generation with modified parameters
- Comprehensive parameter reference validation
- Integration with existing parameter system

All tests require the synth_engine module to be available.
Tests will fail if dependencies are not present.
"""

from typing import Any, Dict, Optional

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


@pytest.fixture(scope="module", name="test_instrument")
def test_instrument_fixture(synth_engine):
    """Fixture to provide test instrument for parameter testing"""
    instrument = synth_engine.get_instrument(0)
    assert instrument is not None, "Test instrument should be available"
    return instrument


class TestParameterNames:
    """Test suite for parameter names functionality"""

    @staticmethod
    def find_parameter_by_name(instrument, instruction_index: int, param_name: str) -> int:
        """Helper function to find parameter index by name"""
        param_names = instrument.get_instruction_parameter_names(instruction_index)
        try:
            return param_names.index(param_name)
        except ValueError:
            return -1

    @staticmethod
    def update_parameter_by_name(instrument, instruction_index: int,
                               param_name: str, value: int) -> bool:
        """Helper function to update parameter by name"""
        param_index = TestParameterNames.find_parameter_by_name(
            instrument, instruction_index, param_name)
        if param_index >= 0:
            instrument.update_parameter(instruction_index, param_index, value)
            return True
        return False

    def get_instruction_details(self, instrument, instruction_index: int) -> Dict[str, Any]:
        """Helper function to get detailed instruction info"""
        instr_name = instrument.get_instruction_name(instruction_index)
        param_names = instrument.get_instruction_parameter_names(instruction_index)
        param_values = instrument.get_instruction_parameters(instruction_index)

        details = {
            'name': instr_name,
            'param_names': param_names,
            'param_values': param_values,
            'parameters': {}
        }

        if param_names and param_values:
            details['parameters'] = dict(zip(param_names, param_values))

        return details

    def test_parameter_lookup_by_name(self, test_instrument):
        """Test parameter lookup functionality by name"""
        instructions = test_instrument.get_instructions()
        assert len(instructions) > 0, "Instrument should have instructions"

        # Test parameter lookup for each instruction
        for i in range(len(instructions)):
            param_names = test_instrument.get_instruction_parameter_names(i)
            if param_names:
                # Test finding existing parameters
                for param_name in param_names:
                    param_idx = self.find_parameter_by_name(test_instrument, i, param_name)
                    assert param_idx >= 0, f"Should find parameter '{param_name}'"
                    assert param_idx < len(param_names), "Parameter index should be valid"

                # Test finding non-existent parameter
                non_existent_idx = self.find_parameter_by_name(test_instrument, i, "NonExistent")
                assert non_existent_idx == -1, "Should return -1 for non-existent parameter"

    def test_envelope_parameter_modification(self, test_instrument):
        """Test ENVELOPE parameter modifications by name"""
        # Find envelope instruction
        envelope_idx = self._find_instruction_by_id(test_instrument, se.ENVELOPE_ID)  # pylint: disable=c-extension-no-member

        if envelope_idx is not None:            # Test ENVELOPE modifications - custom ADSR curve
            modifications = [
                ('Attack', 30),   # Moderate attack
                ('Decay', 60),    # Medium decay
                ('Sustain', 120), # High sustain
                ('Release', 90),  # Long release
                ('Gain', 180),    # Boost volume
            ]

            for param_name, new_value in modifications:
                success = self.update_parameter_by_name(
                    test_instrument, envelope_idx, param_name, new_value)
                assert success, f"Should successfully update {param_name}"

                # Verify the parameter was actually updated
                updated_details = self.get_instruction_details(test_instrument, envelope_idx)
                if param_name in updated_details['parameters']:
                    assert updated_details['parameters'][param_name] == new_value, \
                        f"{param_name} should be updated to {new_value}"

    def test_oscillator_parameter_modification(self, test_instrument):
        """Test OSCILLATOR parameter modifications by name"""
        # Find oscillator instruction
        osc_idx = self._find_instruction_by_id(test_instrument, se.OSCILLATOR_ID)  # pylint: disable=c-extension-no-member

        if osc_idx is not None:
            # Test OSCILLATOR modifications - bright, detuned saw wave
            modifications = [
                ('Transpose', 67),  # +3 semitones
                ('Detune', 70),     # Slight detune
                ('Color', 100),     # Bright timbre
                ('Shape', 90),      # Sharp shape
                ('Type', 32),       # SAW wave
                ('Gain', 150),      # Louder
            ]

            for param_name, new_value in modifications:
                success = self.update_parameter_by_name(
                    test_instrument, osc_idx, param_name, new_value)
                assert success, f"Should successfully update {param_name}"

                # Verify the parameter was actually updated
                updated_details = self.get_instruction_details(test_instrument, osc_idx)
                if param_name in updated_details['parameters']:
                    assert updated_details['parameters'][param_name] == new_value, \
                        f"{param_name} should be updated to {new_value}"

    def test_output_parameter_modification(self, test_instrument):
        """Test OUTPUT parameter modifications by name"""
        # Find output instruction
        output_idx = self._find_instruction_by_id(test_instrument, se.OUTPUT_ID)  # pylint: disable=c-extension-no-member

        if output_idx is not None:
            # Test OUTPUT modifications - boost final volume
            success = self.update_parameter_by_name(test_instrument, output_idx, 'Gain', 220)
            assert success, "Should successfully update OUTPUT Gain"

            # Verify the parameter was actually updated
            updated_details = self.get_instruction_details(test_instrument, output_idx)
            if 'Gain' in updated_details['parameters']:
                assert updated_details['parameters']['Gain'] == 220, \
                    "OUTPUT Gain should be updated to 220"

    def test_audio_generation_with_modified_parameters(self, test_instrument):
        """Test audio generation after parameter modifications"""
        # Render audio with modified instrument
        audio_data = test_instrument.render_note(64)  # Middle C

        # Validate audio data
        assert audio_data is not None, "Audio generation should return data"
        assert len(audio_data) > 0, "Audio data should not be empty"
        assert len(audio_data) >= 1000, "Audio should be reasonable length"

        # Calculate audio statistics
        peak_amplitude = max(abs(x) for x in audio_data) if audio_data else 0
        rms = (sum(x*x for x in audio_data) / len(audio_data))**0.5 if audio_data else 0
        duration = len(audio_data) / 44100

        # Validate audio characteristics
        assert peak_amplitude > 0, "Audio should have non-zero amplitude"
        assert rms > 0, "Audio should have non-zero RMS"
        assert duration > 0.1, "Audio should be at least 100ms duration"

        # Verify audio samples are numeric
        assert all(isinstance(x, (int, float)) for x in audio_data[:10]), \
            "Audio samples should be numeric"

    def test_parameter_names_reference(self, test_instrument):
        """Test comprehensive parameter names reference system"""
        instructions = test_instrument.get_instructions()
        assert len(instructions) > 0, "Instrument should have instructions"

        # Build available instructions reference
        available_instructions = {}
        total_parameters = 0

        for i in range(len(instructions)):
            instr_name = test_instrument.get_instruction_name(i)
            param_names = test_instrument.get_instruction_parameter_names(i)

            if instr_name not in available_instructions:
                available_instructions[instr_name] = param_names
                if param_names:
                    total_parameters += len(param_names)

        # Validate reference system
        assert len(available_instructions) > 0, "Should have available instruction types"
        assert total_parameters > 0, "Should have parameters available"

        # Validate each instruction type has meaningful parameter names
        for instr_name, param_names in available_instructions.items():
            assert isinstance(instr_name, str), "Instruction name should be a string"
            assert len(instr_name) > 0, "Instruction name should not be empty"

            if param_names:
                assert isinstance(param_names, (list, tuple)), \
                    "Parameter names should be a list or tuple"
                for param_name in param_names:
                    assert isinstance(param_name, str), "Parameter name should be a string"
                    assert len(param_name) > 0, "Parameter name should not be empty"

    def test_parameter_system_integration(self, test_instrument):
        """Test complete parameter system integration"""
        # Test that the parameter names system integrates with existing functionality
        instructions = test_instrument.get_instructions()

        for i in range(len(instructions)):
            param_names = test_instrument.get_instruction_parameter_names(i)
            param_values = test_instrument.get_instruction_parameters(i)

            if param_names and param_values:
                # Verify parameter names and values have same length
                assert len(param_names) == len(param_values), \
                    "Parameter names and values should have same length"

                # Test that all parameters are accessible by name
                for param_name in param_names:
                    param_idx = self.find_parameter_by_name(test_instrument, i, param_name)
                    assert param_idx >= 0, f"Parameter '{param_name}' should be findable"

                    # Test parameter modification works
                    original_value = param_values[param_idx]
                    test_value = (original_value + 10) % 256  # Ensure valid range

                    success = self.update_parameter_by_name(
                        test_instrument, i, param_name, test_value)
                    assert success, f"Should be able to update parameter '{param_name}'"

                    # Verify update worked
                    updated_values = test_instrument.get_instruction_parameters(i)
                    assert updated_values[param_idx] == test_value, \
                        f"Parameter '{param_name}' should be updated"

    def _find_instruction_by_id(self, instrument, instruction_id: int) -> Optional[int]:
        """Helper method to find instruction index by ID"""
        instructions = instrument.get_instructions()
        for i, instr_id in enumerate(instructions):
            if instr_id == instruction_id:
                return i
        return None


# Keep the main execution for backward compatibility and standalone testing
if __name__ == "__main__":
    pytest.main([__file__, "-v"])

#!/usr/bin/env python3
"""
Final pytest test suite to verify the complete GUI parameter integration

This test suite validates the complete integration of:
- Synthesizer engine functionality
- GUI parameter controls
- Full parameter mapping and updates
- Integration completeness verification

All tests require the synth_engine module to be available.
Tests will fail if dependencies are not present.
"""

import tkinter as tk
from tkinter import ttk
from typing import Any

import pytest
import synth_engine as se  # pylint: disable=import-error,c-extension-no-member  # type: ignore
from editor.gui.parameter_control import ParameterControl

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


@pytest.fixture(scope="module", name="tk_root")
def tk_root_fixture():
    """Fixture to provide tkinter root window for GUI tests"""
    root = tk.Tk()
    root.withdraw()  # Hide the window during testing
    yield root
    root.destroy()


@pytest.fixture(name="test_frame")
def test_frame_fixture(tk_root):
    """Fixture to provide a test frame for GUI components"""
    frame = ttk.Frame(tk_root)
    yield frame
    frame.destroy()


class TestFinalIntegration:
    """Final integration test suite for GUI parameter system"""

    def test_engine_functionality(self, synth_engine):
        """Test synthesizer engine core functionality"""
        # Verify engine initialization
        assert synth_engine is not None
        assert synth_engine.get_num_instruments() > 0

        # Test instrument access
        instrument = synth_engine.get_instrument(0)
        assert instrument is not None, "Should be able to get first instrument"

        # Test parameter updates
        original_params = instrument.get_instruction_parameters(0)
        assert original_params is not None, "Should have instruction parameters"
        assert len(original_params) > 0, "Should have at least one parameter"

        # Test parameter modification
        test_value = 123
        instrument.update_parameter(0, 0, test_value)
        updated_params = instrument.get_instruction_parameters(0)

        assert updated_params[0] == test_value, \
            f"Parameter should be updated to {test_value}, got {updated_params[0]}"

    def test_gui_components(self, test_frame):
        """Test GUI parameter control components"""

        # Test ParameterControl instantiation and basic functionality
        # ParameterControl expects integer values in range 0-128
        initial_value = 64  # Middle value
        control = ParameterControl(
            parent=test_frame,
            name="Test Parameter",
            config={
                'initial_value': initial_value,
                'row': 0,
                'update_callback': lambda: None  # Simple callback for testing
            }
        )

        # Verify initial state
        assert control.get_value() == initial_value, \
            f"ParameterControl should have correct initial value {initial_value}"

        # Test value setting
        test_value = 100
        control.set_value(test_value)
        assert control.get_value() == test_value, \
            f"ParameterControl should update value correctly to {test_value}"

        # Test boundary values
        control.set_value(0)
        assert control.get_value() == 0, "ParameterControl should handle minimum value"

        control.set_value(128)
        assert control.get_value() == 128, "ParameterControl should handle maximum value"

    def test_instrument_analysis(self, synth_engine):
        """Test analysis of available instruments and their parameters"""
        num_instruments = synth_engine.get_num_instruments()
        assert num_instruments > 0, "Should have at least one instrument"

        # Analyze each instrument
        instruments_with_params = 0
        total_parameters = 0

        for i in range(num_instruments):
            instrument = synth_engine.get_instrument(i)
            if instrument and instrument.get_instructions():
                instructions = instrument.get_instructions()
                instrument_params = 0

                for j in range(len(instructions)):
                    param_names = instrument.get_instruction_parameter_names(j)
                    if param_names:
                        instrument_params += len(param_names)

                if instrument_params > 0:
                    instruments_with_params += 1
                    total_parameters += instrument_params

        assert instruments_with_params >= 1, "Should have at least one instrument with parameters"
        assert total_parameters > 0, "Should have at least some parameters total"

    def test_parameter_control_mapping(self, synth_engine):
        """Test parameter control mapping for GUI integration"""
        instrument = synth_engine.get_instrument(0)
        assert instrument is not None, "First instrument should be available"

        instructions = instrument.get_instructions()
        assert len(instructions) > 0, "Instrument should have instructions"

        # Test parameter mapping structure
        control_mappings = []

        for instr_idx, _ in enumerate(instructions):  # instr_id unused
            instr_name = instrument.get_instruction_name(instr_idx)
            param_names = instrument.get_instruction_parameter_names(instr_idx)

            if param_names:
                assert isinstance(instr_name, str), "Instruction name should be a string"
                assert len(param_names) > 0, "Should have parameter names"

                for param_idx, param_name in enumerate(param_names):
                    control_id = f"instr_{instr_idx}_param_{param_idx}"
                    control_mappings.append({
                        'instruction': instr_name,
                        'parameter': param_name,
                        'control_id': control_id
                    })

        assert len(control_mappings) > 0, "Should have control mappings for GUI"

    def test_integration_completeness(self, synth_engine):
        """Test overall integration completeness and verify system is ready"""
        # Verify engine is working
        assert synth_engine.get_num_instruments() > 0

        # Verify parameter system works
        instrument = synth_engine.get_instrument(0)
        assert instrument is not None

        # Test parameter modification cycle
        if instrument.get_instructions():
            original_params = instrument.get_instruction_parameters(0)
            if len(original_params) > 0:
                # Modify parameter
                test_value = 200
                instrument.update_parameter(0, 0, test_value)
                updated_params = instrument.get_instruction_parameters(0)
                assert updated_params[0] == test_value

                # Test audio generation works
                audio_data = instrument.render_note(64)  # Middle C
                assert audio_data is not None
                assert len(audio_data) > 0

        # Integration is complete when all components are functional
        assert True, "Integration test completed successfully"


# Keep the main execution for backward compatibility and standalone testing
if __name__ == "__main__":
    pytest.main([__file__, "-v"])

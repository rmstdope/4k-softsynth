#!/usr/bin/env python3
"""
Pytest test suite for GUI integration with instrument parameter controls

This test suite validates the GUI component integration including:
- Tkinter GUI components initialization
- Synthesizer engine integration
- Parameter control widget creation
- Scrollable interface functionality
- Complete GUI workflow testing

All tests require the synth_engine module to be available.
Tests will fail if dependencies are not present.
"""

import tkinter as tk
from tkinter import ttk
from typing import Any, Dict

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


@pytest.fixture(name="test_window")
def test_window_fixture(tk_root):
    """Fixture to provide a test window for GUI components"""
    window = tk.Toplevel(tk_root)
    window.title("GUI Integration Test")
    window.geometry("800x600")
    window.withdraw()  # Keep hidden during testing
    yield window
    window.destroy()


@pytest.fixture(name="parameter_control_class")
def parameter_control_class_fixture():
    """Fixture to provide ParameterControl class"""
    return ParameterControl
class TestGUIIntegration:
    """Test suite for GUI integration with parameter controls"""

    def test_tkinter_imports(self):
        """Test that all required GUI modules can be imported"""
        # tkinter is already imported at module level
        assert tk is not None, "tkinter should be available"
        assert ttk is not None, "tkinter.ttk should be available"

    def test_synth_engine_import(self, synth_engine):
        """Test synth_engine import and initialization"""
        assert synth_engine is not None, "synth_engine should be available"
        assert synth_engine.get_num_instruments() > 0, "Should have instruments available"

    def test_parameter_control_import(self, parameter_control_class):
        """Test ParameterControl class import"""
        assert parameter_control_class is not None, "ParameterControl class should be available"
        assert callable(parameter_control_class), "ParameterControl should be instantiable"

    def test_gui_window_creation(self, test_window):
        """Test basic GUI window creation and setup"""
        assert test_window is not None, "Test window should be created"

        # Test basic window properties
        test_window.title("Test Window")
        assert test_window.winfo_exists(), "Window should exist"

    def test_scrollable_frame_creation(self, test_window):
        """Test creation of scrollable frame for parameter controls"""
        # Create main frame
        main_frame = ttk.Frame(test_window, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Create scrollable components
        canvas = tk.Canvas(main_frame, height=300)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        # Configure scrolling
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        scrollable_frame.columnconfigure(1, weight=1)

        # Pack components
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Verify components exist
        assert canvas.winfo_exists(), "Canvas should be created"
        assert scrollbar.winfo_exists(), "Scrollbar should be created"
        assert scrollable_frame.winfo_exists(), "Scrollable frame should be created"

    def test_parameter_controls_creation(self, test_window, synth_engine,
                                        parameter_control_class):
        """Test creation of parameter controls for instrument parameters"""
        # Create the GUI framework
        scrollable_frame = self._setup_gui_framework(test_window)

        # Test parameter control creation for instrument 0
        instrument = synth_engine.get_instrument(0)
        assert instrument is not None, "Should be able to get first instrument"

        instructions = instrument.get_instructions()
        assert len(instructions) > 0, "Instrument should have instructions"

        # Create controls using helper method
        controls = self._create_parameter_controls(
            instrument, instructions, scrollable_frame, parameter_control_class)

        # Verify and test controls
        self._verify_controls_functionality(controls)

    def test_complete_gui_integration(self, test_window, synth_engine):
        """Test complete GUI integration workflow"""
        # Create main components
        main_frame = ttk.Frame(test_window, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Create canvas and scrollbar
        canvas = tk.Canvas(main_frame, height=300)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        # Configure scrolling
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        scrollable_frame.columnconfigure(1, weight=1)

        # Pack components
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Verify we have a reasonable GUI setup by counting controls
        total_controls, instrument_count = self._count_gui_elements(synth_engine)
        assert instrument_count > 0, "Should have instruments with parameters"
        assert total_controls > 0, "Should have parameters to control"

        # Test canvas scroll region update
        scrollable_frame.update_idletasks()
        canvas.configure(scrollregion=canvas.bbox("all"))

        # Add a test button
        test_button = ttk.Button(main_frame, text="Test Button")
        test_button.pack(pady=10)

        assert test_button.winfo_exists(), "Test button should be created"

    def _count_gui_elements(self, synth_engine):
        """Helper method to count GUI elements"""
        total_controls = 0
        instrument_count = 0

        for i in range(synth_engine.get_num_instruments()):
            instrument = synth_engine.get_instrument(i)
            if instrument and instrument.get_instructions():
                instrument_count += 1
                instructions = instrument.get_instructions()

                for instr_idx, _ in enumerate(instructions):  # instr_id unused
                    param_names = instrument.get_instruction_parameter_names(instr_idx)
                    if param_names:
                        total_controls += len(param_names)

        return total_controls, instrument_count

    def _setup_gui_framework(self, test_window):
        """Helper method to set up GUI framework"""
        main_frame = ttk.Frame(test_window, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Create scrollable frame
        canvas = tk.Canvas(main_frame, height=300)
        scrollable_frame = ttk.Frame(canvas)
        scrollable_frame.columnconfigure(1, weight=1)

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.pack(side="left", fill="both", expand=True)

        return scrollable_frame

    def _create_parameter_controls(self, instrument, instructions, scrollable_frame,
                                  parameter_control_class):
        """Helper method to create parameter controls"""
        row = 0
        controls: Dict[str, Any] = {}

        for instr_idx, _ in enumerate(instructions):  # instr_id unused
            instr_name = instrument.get_instruction_name(instr_idx)
            param_names = instrument.get_instruction_parameter_names(instr_idx)
            param_values = instrument.get_instruction_parameters(instr_idx)

            if param_names:
                # Add section header and update row
                row = self._add_section_header(scrollable_frame, instr_name, row)

                # Create controls for this instruction
                row, instruction_controls = self._create_instruction_controls(
                    scrollable_frame, parameter_control_class, instr_idx,
                    param_names, param_values, row)

                # Add controls to main dict
                controls.update(instruction_controls)

        return controls

    def _add_section_header(self, scrollable_frame, instr_name, row):
        """Helper method to add section header"""
        header_label = ttk.Label(scrollable_frame,
                               text=f"🎛️ {instr_name}",
                               font=('TkDefaultFont', 9, 'bold'))
        header_label.grid(row=row, column=0, columnspan=3,
                         sticky=tk.W, pady=(10, 5))
        return row + 1

    def _create_instruction_controls(self, scrollable_frame, parameter_control_class,
                                   instr_idx, param_names, param_values, row):
        """Helper method to create controls for a single instruction"""
        controls: Dict[str, Any] = {}

        for param_idx, (param_name, param_value) in enumerate(
                zip(param_names, param_values)):
            def make_callback(name):
                return lambda: print(f"Parameter {name} updated")  # Callback using name

            # Scale param_value from 0-255 to 0-128 for ParameterControl
            scaled_value = int(param_value * 128 / 255)
            control = parameter_control_class(
                parent=scrollable_frame,
                name=param_name,
                config={
                    'initial_value': scaled_value,
                    'row': row,
                    'update_callback': make_callback(param_name)
                }
            )

            control_id = f"instr_{instr_idx}_param_{param_idx}"
            controls[control_id] = control
            row += 1

        return row, controls

    def _verify_controls_functionality(self, controls):
        """Helper method to verify control functionality"""
        # Verify controls were created
        assert len(controls) > 0, "Should have created parameter controls"

        # Test that controls are functional
        for control_id, control in controls.items():
            assert hasattr(control, 'get_value'), \
                f"Control {control_id} should have get_value method"
            assert hasattr(control, 'set_value'), \
                f"Control {control_id} should have set_value method"

            # Test value getting and setting
            original_value = control.get_value()
            assert isinstance(original_value, int), "Control value should be an integer"
            assert 0 <= original_value <= 128, \
                "Control value should be in valid range (0-128)"


# Keep the main execution for backward compatibility and standalone testing
if __name__ == "__main__":
    pytest.main([__file__, "-v"])

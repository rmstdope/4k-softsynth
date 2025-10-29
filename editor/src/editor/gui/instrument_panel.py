"""Instrument panel component for the audio editor."""

import tkinter as tk
from tkinter import ttk
from .parameter_control import ParameterControl

try:
    import synth_engine
except ImportError:
    synth_engine = None


class InstrumentPanel:
    """Manages instrument selection and parameter controls."""

    def __init__(self, main_editor):
        """Initialize the instrument panel.

        Args:
            main_editor: Reference to the main editor controller
        """
        self.main_editor = main_editor
        self.instrument_var = None
        self.scrollable_frame = None
        self.container_frame = None
        self.adsr_controls = {}

    def create_instrument_section(self, parent_frame):
        """Create instrument control section."""
        instrument_frame = ttk.LabelFrame(parent_frame, text="Instrument Controls",
                                        padding="5")
        instrument_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S),
                            pady=(0, 10))

        # Instrument selector
        ttk.Label(instrument_frame, text="Instrument:").grid(row=0, column=0,
                                                           sticky=tk.W)
        self.instrument_var = tk.StringVar(value="Instrument 0")
        instrument_values = ["Instrument 0", "Instrument 1",
                           "Instrument 2", "Instrument 3"]
        instrument_combo = ttk.Combobox(instrument_frame,
                                      textvariable=self.instrument_var,
                                      values=instrument_values)
        instrument_combo.grid(row=0, column=1, sticky=(tk.W, tk.E),
                            padx=(5, 0))
        instrument_combo.bind('<<ComboboxSelected>>', self.on_instrument_change)

        # Instrument controls
        ttk.Label(instrument_frame, text="Instrument controls:").grid(
            row=1, column=0, columnspan=2, sticky=tk.W, pady=(10, 5))

        self._create_instrument_controllers(instrument_frame)
        instrument_frame.columnconfigure(1, weight=1)

    def _create_instrument_controllers(self, parent_frame):
        """Create instrument control sliders with value fields in a scrollable frame."""
        # Create a scrollable frame for all instrument parameter controls
        container_frame, scrollable_frame = self._create_scrollable_frame(parent_frame)
        container_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S),
                           pady=(5, 0))

        # Configure parent frame to expand the scrollable area
        parent_frame.rowconfigure(2, weight=1)

        # Store reference to scrollable frame for dynamic updates
        self.scrollable_frame = scrollable_frame
        self.container_frame = container_frame

        # Create initial instrument controls
        self._create_controls_for_current_instrument()

    def _create_controls_for_current_instrument(self):
        """Create parameter controls for the currently selected instrument."""
        # Clear existing controls
        self._clear_instrument_controls()

        # Get current instrument and validate
        instrument = self._get_current_instrument()
        if not instrument:
            return

        instructions = instrument.get_instructions()
        if not instructions:
            self._show_no_parameters_message()
            return

        # Create controls for all parameters of all instructions
        row = 0
        for instr_idx, _ in enumerate(instructions):
            instr_name = instrument.get_instruction_name(instr_idx)
            param_names = instrument.get_instruction_parameter_names(instr_idx)
            param_values = instrument.get_instruction_parameters_full(instr_idx)

            # Add section header for this instruction
            if param_names:  # Only show header if there are parameters to display
                self._create_instruction_header(instr_name, row)
                row += 1

                # Get parameter ranges and types for this instruction
                param_ranges = instrument.get_instruction_parameter_ranges(instr_idx)
                param_types = instrument.get_instruction_parameter_types(instr_idx)

                # Create parameter controls
                for param_idx, (param_name, param_value) in enumerate(
                    zip(param_names, param_values)):
                    param_info = {
                        'instr_idx': instr_idx,
                        'param_idx': param_idx,
                        'param_name': param_name,
                        'param_value': param_value,
                        'param_ranges': param_ranges,
                        'param_types': param_types,
                        'row': row
                    }
                    self._create_single_parameter_control(param_info)
                    row += 1

        # Update canvas scroll region
        self._update_scroll_region()

    def _get_current_instrument(self):
        """Get and validate the current instrument."""
        if not hasattr(self.main_editor, 'synth') or not self.main_editor.synth:
            self._show_no_instrument_message()
            return None

        if not self.main_editor.synth.has_instruments():
            self._show_no_instrument_message()
            return None

        instrument = self.main_editor.synth.get_instrument(self.main_editor.current_instrument)
        if not instrument:
            self._show_no_instrument_message()
            return None

        return instrument

    def _create_instruction_header(self, instr_name, row):
        """Create a header label for an instruction section."""
        header_label = ttk.Label(self.scrollable_frame,
                               text=f"🎛️ {instr_name}",
                               font=('TkDefaultFont', 9, 'bold'))
        header_label.grid(row=row, column=0, columnspan=3,
                         sticky=tk.W, pady=(10, 5))

    def _create_single_parameter_control(self, param_info):
        """Create a single parameter control.

        Args:
            param_info: Dict containing 'instr_idx', 'param_idx', 'param_name',
                       'param_value', 'param_ranges', 'param_types', 'row'
        """
        instr_idx = param_info['instr_idx']
        param_idx = param_info['param_idx']
        param_name = param_info['param_name']
        param_value = param_info['param_value']
        param_ranges = param_info['param_ranges']
        param_types = param_info['param_types']
        row = param_info['row']

        # Create unique control ID for this parameter
        control_id = f"instr_{instr_idx}_param_{param_idx}"

        # Get min/max/step values for this parameter (default to 0-128, step=1 if not available)
        min_val, max_val, step_val = (0, 128, 1)
        if param_idx < len(param_ranges):
            param_range = param_ranges[param_idx]
            min_val = param_range.min_value
            max_val = param_range.max_value
            step_val = param_range.step

        # Get parameter type (default to UINT8 if not available)
        param_type = 0  # UINT8
        if param_idx < len(param_types):
            param_type = param_types[param_idx]

        # Determine type name for display
        type_name = "uint8"
        if synth_engine and param_type == synth_engine.PARAM_TYPE_UINT16:
            type_name = "uint16"

        control = ParameterControl(
            parent=self.scrollable_frame,
            name=param_name,
            config={
                'initial_value': param_value,
                'row': row,
                'min_value': min_val,
                'max_value': max_val,
                'step_value': step_val,
                'param_type': param_type,
                'type_name': type_name,
                'update_callback': self._create_parameter_callback(instr_idx, param_idx)
            }
        )

        # Store control with unique ID
        self.adsr_controls[control_id] = control

    def _update_scroll_region(self):
        """Update the canvas scroll region."""
        self.scrollable_frame.update_idletasks()
        self.container_frame.canvas.configure(scrollregion=self.container_frame.canvas.bbox("all"))

    def _clear_instrument_controls(self):
        """Clear all existing instrument parameter controls."""
        # Destroy all existing controls
        for control_id in list(self.adsr_controls.keys()):
            # Destroy the widgets (they're in the scrollable frame)
            # The ParameterControl class doesn't have explicit cleanup,
            # but the widgets will be destroyed with the parent
            del self.adsr_controls[control_id]

        # Clear all widgets from scrollable frame
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

    def _show_no_instrument_message(self):
        """Show message when no instrument is available."""
        msg_label = ttk.Label(self.scrollable_frame,
                            text="❌ No instrument data available",
                            foreground="red")
        msg_label.grid(row=0, column=0, pady=20)

    def _show_no_parameters_message(self):
        """Show message when instrument has no parameters."""
        msg_label = ttk.Label(self.scrollable_frame,
                            text="ℹ️ This instrument has no configurable parameters",
                            foreground="gray")
        msg_label.grid(row=0, column=0, pady=20)

    def _on_instrument_parameter_change(self, instruction_index, param_index):
        """Handle parameter changes for instrument parameters."""
        # Get the control ID and retrieve the control
        control_id = f"instr_{instruction_index}_param_{param_index}"
        control = self.adsr_controls.get(control_id)

        if not control:
            return

        # Get the parameter value (0-255 range)
        param_value = control.get_value()

        # Update the instrument parameter
        try:
            instrument = self.main_editor.synth.get_instrument(self.main_editor.current_instrument)
            if instrument:
                instrument.update_parameter(instruction_index, param_index, param_value)

                # Log the change with human-readable names
                instr_name = instrument.get_instruction_name(instruction_index)
                param_names = instrument.get_instruction_parameter_names(instruction_index)
                param_name = (param_names[param_index] if param_index < len(param_names)
                             else f"Param{param_index}")

                if hasattr(self.main_editor, 'logger'):
                    self.main_editor.logger.debug("Updated %s.%s = %s", instr_name,
                                                   param_name, param_value)

                # Update synthesizer and refresh visualization
                self.update_synth_parameters()

        except (AttributeError, IndexError, ValueError) as e:
            if hasattr(self.main_editor, 'logger'):
                self.main_editor.logger.error("Error updating instrument parameter: %s", e)

    def _create_parameter_callback(self, instruction_index, param_index):
        """Create a callback function for a specific parameter."""
        return lambda: self._on_instrument_parameter_change(instruction_index, param_index)

    def _create_scrollable_frame(self, parent):
        """Create a scrollable frame with canvas and scrollbar."""
        # Create main container frame
        container_frame = ttk.Frame(parent)

        # Create canvas and scrollbar
        canvas = tk.Canvas(container_frame, height=150, highlightthickness=0)
        scrollbar = ttk.Scrollbar(container_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        # Configure scrolling
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        # Create window in canvas
        canvas_window = canvas.create_window((0, 0), window=scrollable_frame,
                                            anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Configure scrollable frame to expand to canvas width
        def _on_canvas_configure(event):
            canvas.itemconfig(canvas_window, width=event.width)

        canvas.bind('<Configure>', _on_canvas_configure)

        # Configure grid columns for ADSR controls
        scrollable_frame.columnconfigure(0, weight=0)  # Label column
        scrollable_frame.columnconfigure(1, weight=10)  # Slider column - wider sliders
        scrollable_frame.columnconfigure(2, weight=0)  # Value field column

        # Pack canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Bind mousewheel to canvas for better UX
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")

        canvas.bind("<MouseWheel>", _on_mousewheel)  # Windows/Mac
        canvas.bind("<Button-4>", lambda e: canvas.yview_scroll(-1, "units"))  # Linux
        canvas.bind("<Button-5>", lambda e: canvas.yview_scroll(1, "units"))   # Linux

        # Store references for later access if needed
        container_frame.scrollable_frame = scrollable_frame
        container_frame.canvas = canvas

        return container_frame, scrollable_frame

    def on_instrument_change(self, _event):
        """Handle instrument selection change."""
        # Update current instrument based on selection
        instrument_text = self.instrument_var.get()
        try:
            # Extract instrument number from "Instrument X" format
            instrument_num = int(instrument_text.split()[-1])
            self.main_editor.current_instrument = instrument_num

            if (hasattr(self.main_editor, 'components') and
                self.main_editor.components and
                hasattr(self.main_editor.components, 'status_panel')):
                self.main_editor.components.status_panel.log_output(
                    f"🎹 Switched to {instrument_text}")

            # Recreate controls for the new instrument
            self._create_controls_for_current_instrument()

            # Update synthesizer parameters and refresh waveform
            self.update_synth_parameters()

        except (ValueError, IndexError) as e:
            if hasattr(self.main_editor, 'logger'):
                self.main_editor.logger.error("Error changing instrument: %s", e)

    def get_parameter_value(self, param_name):
        """Get a parameter value by name.

        Args:
            param_name: The name of the parameter

        Returns:
            The parameter value or None if not found
        """
        # Search through all controls for matching parameter name
        for control in self.adsr_controls.values():
            if hasattr(control, 'name') and control.name == param_name:
                return control.get_value()
        return None

    def set_parameter_value(self, param_name, value):
        """Set a parameter value by name.

        Args:
            param_name: The name of the parameter
            value: The value to set

        Returns:
            True if parameter was found and set, False otherwise
        """
        # Search through all controls for matching parameter name
        for control in self.adsr_controls.values():
            if hasattr(control, 'name') and control.name == param_name:
                control.set_value(value)
                return True
        return False

    def update_synth_parameters(self):
        """Update synthesizer parameters and refresh displays."""
        try:
            # Update the synthesizer with current parameters
            if hasattr(self.main_editor, 'synth') and self.main_editor.synth:
                # Get current instrument parameters and update synth
                # This would typically involve calling synth update methods
                pass

            # Refresh waveform display if available
            if (hasattr(self.main_editor, 'components') and
                self.main_editor.components and
                hasattr(self.main_editor.components, 'waveform_display')):
                self.main_editor.components.waveform_display.auto_update_waveform_from_synth()

        except (RuntimeError, ValueError) as e:
            if hasattr(self.main_editor, 'logger'):
                self.main_editor.logger.error("Error updating synth parameters: %s", e)

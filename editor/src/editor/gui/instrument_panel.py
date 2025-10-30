"""Instrument panel component for the audio editor using CustomTkinter."""

import customtkinter as ctk
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
        instrument_frame = ctk.CTkFrame(parent_frame, corner_radius=10)
        instrument_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=(0, 10))

        # Title label
        title_label = ctk.CTkLabel(instrument_frame, text="Instrument Controls", 
                                  font=ctk.CTkFont(size=16, weight="bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(15, 10))

        # Instrument selector
        ctk.CTkLabel(instrument_frame, text="Instrument:").grid(row=1, column=0,
                                                               sticky="w", padx=(15, 5))
        instrument_values = ["Instrument 0", "Instrument 1",
                           "Instrument 2", "Instrument 3"]
        self.instrument_combo = ctk.CTkComboBox(instrument_frame,
                                               values=instrument_values,
                                               command=self.on_instrument_change,
                                               width=150)
        self.instrument_combo.set("Instrument 0")
        self.instrument_combo.grid(row=1, column=1, sticky="ew", padx=(5, 15))

        # Instrument controls
        ctk.CTkLabel(instrument_frame, text="Instrument controls:").grid(
            row=2, column=0, columnspan=2, sticky="w", padx=(15, 5), pady=(15, 5))

        self._create_instrument_controllers(instrument_frame)
        instrument_frame.columnconfigure(1, weight=1)

    def _create_instrument_controllers(self, parent_frame):
        """Create instrument control sliders with value fields in a scrollable frame."""
        # Create a scrollable frame for all instrument parameter controls
        container_frame, scrollable_frame = self._create_scrollable_frame(parent_frame)
        container_frame.grid(row=3, column=0, columnspan=2, sticky="nsew",
                           padx=15, pady=(5, 15))

        # Configure parent frame to expand the scrollable area
        parent_frame.rowconfigure(3, weight=1)

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

                # Get string-based parameter values for enum parameters
                params_as_strings = instrument.get_instruction_parameters_as_strings(instr_idx)

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
                        'params_as_strings': params_as_strings,
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
        header_label = ctk.CTkLabel(self.scrollable_frame,
                                   text=f"🎛️ {instr_name}",
                                   font=ctk.CTkFont(size=12, weight="bold"))
        header_label.grid(row=row, column=0, columnspan=3,
                         sticky="w", pady=(10, 5))

    def _create_single_parameter_control(self, param_info):
        """Create a single parameter control.

        Args:
            param_info: Dict containing parameter information
        """
        # Extract parameter information
        control_id = f"instr_{param_info['instr_idx']}_param_{param_info['param_idx']}"
        min_val, max_val, step_val = self._get_parameter_range(param_info)
        param_type = self._get_parameter_type(param_info)
        type_name = self._get_type_name(param_type)
        enum_options = self._get_enum_options(param_info, param_type)
        initial_value = self._get_initial_value(param_info, param_type)

        # Create the parameter control
        control = ParameterControl(
            parent=self.scrollable_frame,
            name=param_info['param_name'],
            config={
                'initial_value': initial_value,
                'row': param_info['row'],
                'min_value': min_val,
                'max_value': max_val,
                'step_value': step_val,
                'param_type': param_type,
                'type_name': type_name,
                'enum_options': enum_options,
                'update_callback': self._create_parameter_callback(
                    param_info['instr_idx'], param_info['param_idx'])
            }
        )

        # Store control with unique ID
        self.adsr_controls[control_id] = control

    def _get_parameter_range(self, param_info):
        """Get parameter range values."""
        min_val, max_val, step_val = (0, 128, 1)  # defaults
        param_ranges = param_info['param_ranges']
        param_idx = param_info['param_idx']

        if param_idx < len(param_ranges):
            param_range = param_ranges[param_idx]
            min_val = param_range.min_value
            max_val = param_range.max_value
            step_val = param_range.step

        return min_val, max_val, step_val

    def _get_parameter_type(self, param_info):
        """Get parameter type."""
        param_type = 0  # UINT8 default
        param_types = param_info['param_types']
        param_idx = param_info['param_idx']

        if param_idx < len(param_types):
            param_type = param_types[param_idx]
        return param_type

    def _get_type_name(self, param_type):
        """Get type name for display."""
        type_name = "uint8"
        if synth_engine and param_type == synth_engine.PARAM_TYPE_UINT16:  # pylint: disable=c-extension-no-member
            type_name = "uint16"
        elif synth_engine and param_type == synth_engine.PARAM_TYPE_ENUM:  # pylint: disable=c-extension-no-member
            type_name = "enum"
        return type_name

    def _get_enum_options(self, param_info, param_type):
        """Get enum options if this is an enum parameter."""
        enum_options = []
        if not (synth_engine and param_type == synth_engine.PARAM_TYPE_ENUM):  # pylint: disable=c-extension-no-member
            return enum_options

        try:
            instrument = self._get_current_instrument()
            if not instrument:
                return enum_options

            param_enums = instrument.get_instruction_parameter_enums(param_info['instr_idx'])
            param_idx = param_info['param_idx']

            if param_idx >= len(param_enums) or not param_enums[param_idx]:
                return enum_options

            enum_obj = param_enums[param_idx]
            enum_options = self._extract_enum_names(enum_obj)

        except Exception as e:  # pylint: disable=broad-exception-caught
            if hasattr(self.main_editor, 'logger'):
                self.main_editor.logger.warning("Error getting enum options: %s", e)

        return enum_options

    def _extract_enum_names(self, enum_obj):
        """Extract enum names from enum object."""
        enum_options = []
        consecutive_unknowns = 0

        for i in range(256):  # Maximum uint8_t values
            try:
                name = enum_obj.get_name(i)
                if name and name != "UNKNOWN":
                    enum_options.append(name)
                    consecutive_unknowns = 0  # Reset counter
                else:
                    consecutive_unknowns += 1
                    # Stop if we've seen many consecutive unknowns
                    if consecutive_unknowns > 50:
                        break
            except (RuntimeError, IndexError):
                consecutive_unknowns += 1
                if consecutive_unknowns > 50:
                    break

        return enum_options

    def _get_initial_value(self, param_info, param_type):
        """Get initial value for parameter."""
        initial_value = param_info['param_value']

        # For enum parameters, use the string value
        if (synth_engine and param_type == synth_engine.PARAM_TYPE_ENUM and  # pylint: disable=c-extension-no-member
                param_info['param_idx'] < len(param_info['params_as_strings'])):
            initial_value = param_info['params_as_strings'][param_info['param_idx']]

        return initial_value

    def _update_scroll_region(self):
        """Update the scroll region - CTkScrollableFrame handles this automatically."""
        # CustomTkinter's CTkScrollableFrame handles scrolling automatically
        pass

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
        msg_label = ctk.CTkLabel(self.scrollable_frame,
                               text="❌ No instrument data available",
                               text_color="red")
        msg_label.grid(row=0, column=0, pady=20)

    def _show_no_parameters_message(self):
        """Show message when instrument has no parameters."""
        msg_label = ctk.CTkLabel(self.scrollable_frame,
                               text="ℹ️ This instrument has no configurable parameters",
                               text_color="gray")
        msg_label.grid(row=0, column=0, pady=20)

    def _on_instrument_parameter_change(self, instruction_index, param_index):
        """Handle parameter changes for instrument parameters."""
        # Get the control ID and retrieve the control
        control_id = f"instr_{instruction_index}_param_{param_index}"
        control = self.adsr_controls.get(control_id)

        if not control:
            return

        # Update the instrument parameter
        try:
            instrument = self.main_editor.synth.get_instrument(self.main_editor.current_instrument)
            if not instrument:
                return

            # Check if this is an enum parameter
            if (synth_engine and hasattr(control, 'is_enum') and control.is_enum):
                # For enum parameters, use string-based update
                selected_text = control.var.get()
                if selected_text and selected_text != "UNKNOWN":
                    instrument.update_parameter_with_string(
                        instruction_index, param_index, selected_text)
                    param_display_value = selected_text
                else:
                    return  # Don't update if invalid selection
            else:
                # For numeric parameters, use integer value
                param_value = control.get_value()
                instrument.update_parameter(instruction_index, param_index, param_value)
                param_display_value = str(param_value)

            # Log the change with human-readable names
            instr_name = instrument.get_instruction_name(instruction_index)
            param_names = instrument.get_instruction_parameter_names(instruction_index)
            param_name = (param_names[param_index] if param_index < len(param_names)
                         else f"Param{param_index}")

            if hasattr(self.main_editor, 'logger'):
                self.main_editor.logger.debug("Updated %s.%s = %s", instr_name,
                                               param_name, param_display_value)

            # Update synthesizer and refresh visualization
            self.update_synth_parameters()

        except (AttributeError, IndexError, ValueError) as e:
            if hasattr(self.main_editor, 'logger'):
                self.main_editor.logger.error("Error updating instrument parameter: %s", e)

    def _create_parameter_callback(self, instruction_index, param_index):
        """Create a callback function for a specific parameter."""
        return lambda: self._on_instrument_parameter_change(
            instruction_index, param_index)

    def _create_scrollable_frame(self, parent):
        """Create a scrollable frame using CustomTkinter's CTkScrollableFrame."""
        # Create scrollable frame - CustomTkinter handles scrolling internally
        # Increased height to provide more space for parameter controls
        scrollable_frame = ctk.CTkScrollableFrame(parent, height=300, corner_radius=10)
        
        # Configure grid columns for parameter controls with wider sliders
        scrollable_frame.columnconfigure(0, weight=0, minsize=150)  # Label column - wider for readability
        scrollable_frame.columnconfigure(1, weight=5, minsize=300)  # Slider column - much wider and expandable
        scrollable_frame.columnconfigure(2, weight=0, minsize=100)  # Value field column - slightly wider

        return scrollable_frame, scrollable_frame

    def on_instrument_change(self, instrument_text):
        """Handle instrument selection change."""
        # Update current instrument based on selection
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

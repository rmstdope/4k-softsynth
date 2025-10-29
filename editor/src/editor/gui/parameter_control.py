"""
Parameter Control Widget for 4K Softsynth Editor
A reusable slider-value pair control for parameters with enum support
"""

from typing import Optional, Callable, Dict, Any
import tkinter as tk
from tkinter import ttk

try:
    import synth_engine
except ImportError:
    synth_engine = None


class ParameterControl:
    """A reusable parameter control supporting sliders and dropdowns for enum parameters"""

    def __init__(self, parent: tk.Widget, name: str, config: Dict[str, Any]) -> None:
        """Initialize a parameter control

        Args:
            parent: Parent tkinter widget
            name: Display name for the parameter
            config: Dict with 'initial_value', 'row', optional 'update_callback', 
                   optional 'min_value', 'max_value', 'step_value', 'param_type', 'type_name',
                   optional 'enum_options' (list of strings for enum parameters)
        """
        self.name = name
        self.min_val = config.get('min_value', 0)
        self.max_val = config.get('max_value', 128)
        self.step_val = config.get('step_value', 1)
        self.param_type = config.get('param_type', 0)
        self.type_name = config.get('type_name', 'uint8')
        self.enum_options = config.get('enum_options', [])
        self.update_callback: Optional[Callable[[], None]] = config.get('update_callback')
        
        # Check if this is an enum parameter
        self.is_enum = (synth_engine is not None and 
                       self.param_type == synth_engine.PARAM_TYPE_ENUM and 
                       self.enum_options)

        # Create the control widgets
        self._create_widgets(parent, config['row'], config['initial_value'])

    def _create_widgets(self, parent: tk.Widget, row: int, initial_value) -> None:
        """Create the label and control widgets (slider+entry for numeric, dropdown for enum)"""
        # Determine type name for display
        type_display = "enum" if self.is_enum else self.type_name
        label_text = f"{self.name} ({type_display}):"
        ttk.Label(parent, text=label_text).grid(row=row, column=0, sticky=tk.W)

        if self.is_enum:
            self._create_enum_widgets(parent, row, initial_value)
        else:
            self._create_numeric_widgets(parent, row, initial_value)

    def _create_enum_widgets(self, parent: tk.Widget, row: int, initial_value) -> None:
        """Create dropdown widget for enum parameters"""
        # Variable for the dropdown
        if isinstance(initial_value, str):
            # If initial_value is already a string, use it directly
            initial_text = initial_value if initial_value in self.enum_options else "UNKNOWN"
        else:
            # If initial_value is numeric, treat it as an index (legacy behavior)
            initial_index = int(initial_value)
            initial_text = (self.enum_options[initial_index] 
                           if 0 <= initial_index < len(self.enum_options) 
                           else "UNKNOWN")
        
        self.var = tk.StringVar(value=initial_text)
        
        # Dropdown (Combobox)
        self.combobox = ttk.Combobox(parent, textvariable=self.var, 
                                    values=self.enum_options, 
                                    state="readonly", width=12)
        self.combobox.grid(row=row, column=1, sticky=(tk.W, tk.E), padx=(5, 5))
        self.combobox.bind('<<ComboboxSelected>>', self._on_enum_change)
        
        # No entry field needed for enums - the dropdown shows the value
        # Create empty widget in column 2 to maintain layout
        ttk.Label(parent, text="").grid(row=row, column=2)

    def _create_numeric_widgets(self, parent: tk.Widget, row: int, initial_value: float) -> None:
        """Create slider and entry widgets for numeric parameters"""
        # Variable for the slider
        self.var = tk.IntVar(value=int(initial_value))

        # Slider (tkinter Scale doesn't have native step support, so we'll handle it in callbacks)
        self.scale = ttk.Scale(parent, from_=self.min_val, to=self.max_val,
                              variable=self.var, orient=tk.HORIZONTAL,
                              command=self._on_slider_change)
        self.scale.grid(row=row, column=1, sticky=(tk.W, tk.E), padx=(5, 5))

        # Entry field
        self.entry = ttk.Entry(parent, width=8, justify=tk.CENTER)
        self.entry.grid(row=row, column=2, sticky=tk.W, padx=(0, 5))
        self.entry.insert(0, f"{int(initial_value)}")
        self.entry.bind('<Return>', self._on_entry_change)
        self.entry.bind('<FocusOut>', self._on_entry_change)

    def _on_slider_change(self, value: str) -> None:
        """Handle slider changes for numeric parameters"""
        # Apply step quantization
        raw_value = int(float(value))
        quantized_value = self._quantize_to_step(raw_value)
        
        # Update the variable if quantization changed the value
        if quantized_value != raw_value:
            self.var.set(quantized_value)
        
        self.entry.delete(0, tk.END)
        self.entry.insert(0, f"{quantized_value}")
        if self.update_callback:
            self.update_callback()

    def _on_entry_change(self, _event: tk.Event) -> None:
        """Handle entry field changes for numeric parameters"""
        try:
            value = int(float(self.entry.get()))
            value = max(self.min_val, min(self.max_val, value))  # Clamp to valid range
            value = self._quantize_to_step(value)  # Apply step quantization
            self.var.set(value)
            self.entry.delete(0, tk.END)
            self.entry.insert(0, f"{value}")
            if self.update_callback:
                self.update_callback()
        except ValueError:
            # Reset to current slider value if invalid input
            self.entry.delete(0, tk.END)
            self.entry.insert(0, f"{self.var.get()}")

    def _on_enum_change(self, _event: tk.Event) -> None:
        """Handle dropdown changes for enum parameters"""
        if self.update_callback:
            self.update_callback()

    def get_value(self) -> int:
        """Get the current parameter value as integer (enum index for enum parameters)"""
        if self.is_enum:
            # Return the index of the selected enum option
            selected_text = self.var.get()
            try:
                return self.enum_options.index(selected_text)
            except (ValueError, AttributeError):
                return 0  # Default to first option if invalid
        else:
            return self.var.get()

    def set_value(self, value) -> None:
        """Set the parameter value programmatically"""
        if self.is_enum:
            if isinstance(value, str):
                # Set enum by string name
                if value in self.enum_options:
                    self.var.set(value)
                else:
                    self.var.set("UNKNOWN")
            else:
                # Set enum by index (legacy behavior)
                index = int(value)
                if 0 <= index < len(self.enum_options):
                    self.var.set(self.enum_options[index])
                else:
                    self.var.set("UNKNOWN")
        else:
            # Set numeric value
            value = int(max(self.min_val, min(self.max_val, value)))
            value = self._quantize_to_step(value)
            self.var.set(value)
            self.entry.delete(0, tk.END)
            self.entry.insert(0, f"{value}")
    
    def _quantize_to_step(self, value: int) -> int:
        """Quantize a value to the nearest step increment"""
        if self.step_val <= 1:
            return value
        
        # Calculate the number of steps from min_val
        steps_from_min = round((value - self.min_val) / self.step_val)
        quantized = self.min_val + (steps_from_min * self.step_val)
        
        # Ensure we stay within bounds
        return max(self.min_val, min(self.max_val, quantized))

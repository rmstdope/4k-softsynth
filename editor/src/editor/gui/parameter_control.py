"""
Parameter Control Widget for 4K Softsynth Editor
A reusable slider-value pair control for parameters
"""

from typing import Optional, Callable, Dict, Any
import tkinter as tk
from tkinter import ttk


class ParameterControl:
    """A reusable slider-value pair control for parameters"""

    def __init__(self, parent: tk.Widget, name: str, config: Dict[str, Any]) -> None:
        """Initialize a parameter control

        Args:
            parent: Parent tkinter widget
            name: Display name for the parameter
            config: Dict with 'initial_value', 'row', optional 'update_callback', 
                   optional 'min_value', 'max_value', 'step_value', 'param_type', and 'type_name'
        """
        self.name = name
        self.min_val = config.get('min_value', 0)
        self.max_val = config.get('max_value', 128)
        self.step_val = config.get('step_value', 1)
        self.param_type = config.get('param_type', 0)
        self.type_name = config.get('type_name', 'uint8')
        self.update_callback: Optional[Callable[[], None]] = config.get('update_callback')

        # Create the control widgets
        self._create_widgets(parent, config['row'], config['initial_value'])

    def _create_widgets(self, parent: tk.Widget, row: int, initial_value: float) -> None:
        """Create the label, slider, and entry widgets"""
        # Label with parameter type information
        label_text = f"{self.name} ({self.type_name}):"
        ttk.Label(parent, text=label_text).grid(row=row, column=0, sticky=tk.W)

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
        """Handle slider changes"""
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
        """Handle entry field changes"""
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

    def get_value(self) -> int:
        """Get the current parameter value"""
        return self.var.get()

    def set_value(self, value: float) -> None:
        """Set the parameter value programmatically"""
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

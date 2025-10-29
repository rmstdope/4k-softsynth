"""
Wrapper for the ARM64 synthesizer engine
Provides Python interface to the native 4K softsynth ARM64 assembly
"""

import os
import numpy as np
import synth_engine  # pylint: disable=import-error

class SynthWrapper:
    """Python wrapper for the ARM64 synthesizer engine"""

    def __init__(self):
        """Initialize the synthesizer wrapper
        """
        print(f"🔍 DEBUG: Python Process ID = {os.getpid()}")
        print("   Use this PID to attach C++ debugger")
        # Create the ARM64 synth engine instance
        self.engine = synth_engine.SynthEngine()  # pylint: disable=c-extension-no-member
        self.is_initialized = self.engine.initialize()
        print("ARM64 Synthesizer initialized")

    def render_note(self) -> np.ndarray:
        """Render audio samples for one note from the ARM64 synthesizer

        Returns:
            NumPy array of mono audio samples
        """
        # Get samples from ARM64 engine
        samples = self.engine.render_note()
        return np.array(samples, dtype=np.float32)

    def render_instrument_note(self, instrument_num: int, note_num: int) -> np.ndarray:
        """Render audio samples for one note from the ARM64 synthesizer

        Returns:
            NumPy array of mono audio samples
        """
        # Get samples from ARM64 engine
        samples = self.engine.render_instrument_note(instrument_num, note_num)
        # samples = self.engine.render_instrument_note(1, note_num)
        return np.array(samples, dtype=np.float32)

    def is_ready(self) -> bool:
        """Check if the synthesizer is ready for use"""
        return self.engine.is_initialized()

    def get_constants(self) -> dict:
        """Get synthesizer constants from the ARM64 code

        Returns:
            Dictionary of constants
        """
        # pylint: disable=c-extension-no-member
        return {
            'SAMPLE_RATE': synth_engine.SAMPLE_RATE,
            'BEATS_PER_MINUTE': synth_engine.BEATS_PER_MINUTE,
            'NOTES_PER_BEAT': synth_engine.NOTES_PER_BEAT,
            'MAX_NUM_INSTRUMENTS': synth_engine.MAX_NUM_INSTRUMENTS,
            'MAX_COMMANDS': synth_engine.MAX_COMMANDS,
            'MAX_COMMAND_PARAMS': synth_engine.MAX_COMMAND_PARAMS,
            'ENVELOPE_ID': synth_engine.ENVELOPE_ID,
            'OSCILLATOR_ID': synth_engine.OSCILLATOR_ID,
            'OPERATION_ID': synth_engine.OPERATION_ID,
            'HLD': synth_engine.HLD,
        }

    def get_instrument(self, instrument_num: int):
        """Get an instrument object for parameter management
        
        Args:
            instrument_num: The instrument number (0-3)
            
        Returns:
            Instrument object or None if not found
        """
        return self.engine.get_instrument(instrument_num)

    def has_instruments(self) -> bool:
        """Check if the synthesizer has instrument data available
        
        Returns:
            True if instruments are available, False otherwise
        """
        return hasattr(self.engine, 'get_instrument') and self.engine is not None

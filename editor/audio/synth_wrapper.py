"""
Wrapper for the ARM64 synthesizer engine
Provides Python interface to the native 4K softsynth ARM64 assembly
"""

import os
import numpy as np

# Try to import the compiled C++ extension
try:
    import synth_engine  # pylint: disable=import-error
    SYNTH_ENGINE_AVAILABLE = True
except ImportError:
    print("Warning: synth_engine C++ extension not available. Running in simulation mode.")
    SYNTH_ENGINE_AVAILABLE = False

class SynthWrapper:
    """Python wrapper for the ARM64 synthesizer engine"""

    def __init__(self):
        """Initialize the synthesizer wrapper
        """
        self.engine = None
        self.is_initialized = False

        if SYNTH_ENGINE_AVAILABLE:
            try:
                print(f"🔍 DEBUG: Python Process ID = {os.getpid()}")
                print("   Use this PID to attach C++ debugger")
                # Create the ARM64 synth engine instance
                self.engine = synth_engine.SynthEngine()  # pylint: disable=c-extension-no-member
                self.is_initialized = self.engine.initialize()
                print("ARM64 Synthesizer initialized")
            except (ImportError, AttributeError, RuntimeError) as e:
                print(f"Error initializing ARM64 synthesizer: {e}")
                self.engine = None

    def render_note(self) -> np.ndarray:
        """Render audio samples for one note from the ARM64 synthesizer

        Returns:
            NumPy array of mono audio samples
        """
        if self.engine and self.is_initialized:
            try:
                # Get samples from ARM64 engine
                samples = self.engine.render_note()
                return np.array(samples, dtype=np.float32)
            except (AttributeError, RuntimeError, ValueError) as e:
                print(f"ARM64 render error: {e}")
                # Fall through to simulation mode
        return np.array([0], dtype=np.float32)

    def render_instrument_note(self, instrument_num: int, note_num: int) -> np.ndarray:
        """Render audio samples for one note from the ARM64 synthesizer

        Returns:
            NumPy array of mono audio samples
        """
        if self.engine and self.is_initialized:
            try:
                # Get samples from ARM64 engine
                samples = self.engine.render_instrument_note(instrument_num, note_num)
                # samples = self.engine.render_instrument_note(1, note_num)
                return np.array(samples, dtype=np.float32)
            except (AttributeError, RuntimeError, ValueError) as e:
                print(f"ARM64 render error: {e}")
                # Fall through to simulation mode
        return np.array([0], dtype=np.float32)

    # def set_parameter(self, instrument: int, parameter: int, value: float):
    #     """Set a synthesizer parameter in the transformed_parameters array

    #     Args:
    #         instrument: Instrument number (0-3) - currently unused, parameters are global
    #         parameter: Parameter index (0-15)
    #         value: Parameter value (0.0-1.0)
    #     """
    #     if self.engine and self.is_initialized:
    #         try:
    #             self.engine.set_transformed_parameter(parameter, value)
    #         except Exception as e:
    #             print(f"Parameter set error: {e}")
    #     else:
    #         # Simulation mode
    #         print(f"Set parameter: instrument={instrument}, param={parameter}, value={value}")

    # def trigger_note(self, instrument: int, note: int, velocity: float = 1.0):
    #     """Trigger a note on the specified instrument

    #     Args:
    #         instrument: Instrument number (0-3)
    #         note: MIDI note number (0-127)
    #         velocity: Note velocity (0.0-1.0)
    #     """
    #     if self.engine and self.is_initialized:
    #         try:
    #             self.engine.trigger_note(instrument, note, velocity)
    #         except Exception as e:
    #             print(f"Note trigger error: {e}")
    #     else:
    #         # Simulation mode
    #         print(f"Trigger note: instrument={instrument}, note={note}, velocity={velocity}")

    # def release_note(self, instrument: int, note: int):
    #     """Release a note on the specified instrument
    #     (not directly supported in current ARM64 code)

    #     Args:
    #         instrument: Instrument number (0-3)
    #         note: MIDI note number (0-127)
    #     """
    #     # The current ARM64 assembly doesn't have explicit note release
    #     # Notes are released through the envelope system
    #     print(f"Release note: instrument={instrument}, note={note} (handled by envelope)")

    # # ARM64 Assembly Function Wrappers
    # def call_transform_values(self):
    #     """Call the ARM64 transform_values function"""
    #     if self.engine and self.is_initialized:
    #         self.engine.call_transform_values()

    # def call_envelope_function(self):
    #     """Call the ARM64 envelope_function"""
    #     if self.engine and self.is_initialized:
    #         self.engine.call_envelope_function()

    # def call_storeval_function(self):
    #     """Call the ARM64 storeval_function"""
    #     if self.engine and self.is_initialized:
    #         self.engine.call_storeval_function()

    # def call_process_stack(self):
    #     """Call the ARM64 process_stack function"""
    #     if self.engine and self.is_initialized:
    #         self.engine.call_process_stack()

    # def call_new_instrument_note(self):
    #     """Call the ARM64 new_instrument_note function"""
    #     if self.engine and self.is_initialized:
    #         self.engine.call_new_instrument_note()

    # def set_adsr(self, instrument: int, attack: float, decay: float,
    #              sustain: float, release: float, gain: float = 1.0):
    #     """Set ADSR envelope parameters using the ARM64 engine

    #     Args:
    #         instrument: Instrument number (0-3) - currently not used in ARM64 code
    #         attack: Attack time (0.0-1.0)
    #         decay: Decay time (0.0-1.0)
    #         sustain: Sustain level (0.0-1.0)
    #         release: Release time (0.0-1.0)
    #         gain: Gain level (0.0-1.0)
    #     """
    #     if self.engine and self.is_initialized:
    #         try:
    #             self.engine.set_envelope_parameters(attack, decay, sustain, release, gain)
    #         except Exception as e:
    #             print(f"ADSR set error: {e}")
    #     else:
    #         # Simulation mode
    #         print(f"Set ADSR: instrument={instrument}, A={attack}, D={decay}, "
    #               f"S={sustain}, R={release}, G={gain}")

    # def set_oscillator(self, instrument: int, waveform_type: int, transpose: float,
    #                   detune: float, color: float, gain: float):
    #     """Set oscillator parameters using the ARM64 engine

    #     Args:
    #         instrument: Instrument number (0-3) - currently not used in ARM64 code
    #         waveform_type: Waveform type (0=sine, 1=saw, 2=square, etc.)
    #         transpose: Transpose in semitones
    #         detune: Detune amount
    #         color: Color/timbre parameter
    #         gain: Gain level (0.0-1.0)
    #     """
    #     if self.engine and self.is_initialized:
    #         try:
    #             self.engine.set_oscillator_parameters(
    #                 waveform_type, transpose, detune, color, gain)
    #         except Exception as e:
    #             print(f"Oscillator set error: {e}")
    #     else:
    #         # Simulation mode
    #         print(f"Set Oscillator: instrument={instrument}, type={waveform_type}, "
    #               f"transpose={transpose}, detune={detune}, color={color}, gain={gain}")

    # def get_transformed_parameter(self, index: int) -> float:
    #     """Get a parameter from the ARM64 transformed_parameters array

    #     Args:
    #         index: Parameter index (0-15)

    #     Returns:
    #         Parameter value
    #     """
    #     if self.engine and self.is_initialized:
    #         try:
    #             return self.engine.get_transformed_parameter(index)
    #         except Exception as e:
    #             print(f"Parameter get error: {e}")
    #     return 0.0

    def is_ready(self) -> bool:
        """Check if the synthesizer is ready for use"""
        if self.engine:
            return self.engine.is_initialized()
        return self.is_initialized

    def get_constants(self) -> dict:
        """Get synthesizer constants from the ARM64 code

        Returns:
            Dictionary of constants
        """
        if not SYNTH_ENGINE_AVAILABLE:
            return {}

        try:
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
        except (AttributeError, ImportError) as e:
            print(f"Constants access error: {e}")
            return {}

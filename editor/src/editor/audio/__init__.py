"""
Audio package for 4K Softsynth Editor
Contains audio processing and synthesizer integration components
"""

from .synth_wrapper import SynthWrapper
from .audio_device import Audio

__all__ = ['SynthWrapper', 'Audio']

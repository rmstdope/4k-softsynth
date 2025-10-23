"""
Test the synthesizer wrapper functionality
"""

import unittest
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from audio.synth_wrapper import SynthWrapper

class TestSynthWrapper(unittest.TestCase):
    """Test cases for SynthWrapper class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.synth = SynthWrapper()
    
    def test_initialization(self):
        """Test synthesizer initialization"""
        self.assertIsNotNone(self.synth)
        self.assertEqual(self.synth.get_sample_rate(), 44100)
        self.assertEqual(self.synth.get_buffer_size(), 1024)
    
    def test_render_audio(self):
        """Test audio rendering"""
        samples = self.synth.render_audio(1024)
        self.assertEqual(len(samples), 1024)
        self.assertTrue(all(isinstance(sample, float) for sample in samples))
    
    def test_parameter_setting(self):
        """Test parameter setting (simulation mode)"""
        # Should not raise exceptions
        self.synth.set_parameter(0, 1, 0.5)
        self.synth.set_adsr(0, 0.1, 0.2, 0.8, 0.3)
        self.synth.set_oscillator(0, 0, 0.0, 0.0, 1.0)
    
    def test_note_triggering(self):
        """Test note triggering (simulation mode)"""
        # Should not raise exceptions
        self.synth.trigger_note(0, 60, 1.0)
        self.synth.release_note(0, 60)

if __name__ == '__main__':
    unittest.main()
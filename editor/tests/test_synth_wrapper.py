"""
Test the synthesizer wrapper functionality
"""

import os
import sys
import unittest

# Add editor directory to path if not already there (for direct execution)
editor_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if editor_dir not in sys.path:
    sys.path.insert(0, editor_dir)

from audio.synth_wrapper import SynthWrapper

class TestSynthWrapper(unittest.TestCase):
    """Test cases for SynthWrapper class"""

    def setUp(self):
        """Set up test fixtures"""
        self.synth = SynthWrapper()

    def test_initialization(self):
        """Test synthesizer initialization"""
        self.assertIsNotNone(self.synth)


if __name__ == '__main__':
    unittest.main()

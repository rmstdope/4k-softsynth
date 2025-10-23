#!/usr/bin/env python3
"""
4K Softsynth Editor - Main Application
A GUI editor for the 4K softsynth using PySimpleGUI
"""

import sys
import os

# Add the current directory to the Python path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Check for GUI dependencies
GUI_AVAILABLE = True
GUI_ERROR = None

try:
    import tkinter
except ImportError:
    GUI_AVAILABLE = False
    GUI_ERROR = "tkinter not available - install tkinter support for Python"

try:
    import PySimpleGUI as sg
except ImportError:
    GUI_AVAILABLE = False
    GUI_ERROR = "PySimpleGUI not available - install with: pip install PySimpleGUI"

try:
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
except ImportError:
    GUI_AVAILABLE = False
    GUI_ERROR = "matplotlib not available - install with: pip install matplotlib"

try:
    import numpy as np
except ImportError:
    GUI_AVAILABLE = False
    GUI_ERROR = "numpy not available - install with: pip install numpy"

# Import our modules
from audio.synth_wrapper import SynthWrapper
from utils.logger import setup_logger

if GUI_AVAILABLE:
    from gui.main_window import MainWindow

def main():
    """Main entry point for the Audio Editor."""
    logger = setup_logger()
    logger.info("Starting Audio Editor")
    
    if not GUI_AVAILABLE:
        print(f"ERROR: GUI not available - {GUI_ERROR}")
        print("\nAlternative interfaces available:")
        print("1. Tkinter-based GUI (recommended):")
        print("   python tkinter_main.py")
        print("\n2. Command-line interface:")
        print("   python cli_main.py")
        print("\n3. Example ARM64 test:")
        print("   python example_arm64.py")
        print("\nTo fix PySimpleGUI on macOS:")
        print("  - PySimpleGUI may have compatibility issues on some macOS versions")
        print("  - Use the Tkinter GUI instead for better stability")
        return 1
    
    print("WARNING: PySimpleGUI interface is deprecated due to stability issues.")
    print("Recommended alternatives:")
    print("  python tkinter_main.py  # Stable GUI interface")
    print("  python cli_main.py      # Command-line interface")
    print("  python launch.py        # Smart launcher")
    
    # Initialize the synthesizer
    try:
        synth = SynthWrapper()
    except Exception as e:
        logger.error("Synthesizer initialization error: %s", e)
        print(f"ERROR: Failed to initialize synthesizer: {e}")
        return 1
    
    # Create and run the main window
    try:
        app = MainWindow(synth)
        app.run()
        logger.info("Application closed normally")
    except Exception as e:
        logger.error("Application error: %s", e)
        print(f"ERROR: Application failed: {e}")
        print("\nRecommended alternatives:")
        print("  python tkinter_main.py  # Stable GUI")
        print("  python cli_main.py      # Command-line")
        return 1
    
    return 0

if __name__ == "__main__":
    main()
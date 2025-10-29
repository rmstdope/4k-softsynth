"""
Main Editor Application for 4K Softsynth
Refactored with component architecture
"""

import tkinter as tk
from tkinter import ttk

import synth_engine  # pylint: disable=import-error
from editor.audio.synth_wrapper import SynthWrapper
from editor.audio.audio_device import AudioDevice
from editor.utils.logger import setup_logger
from .menu_manager import MenuManager
from .playback_controller import PlaybackController
from .waveform_display import WaveformDisplay
from .instrument_panel import InstrumentPanel
from .status_panel import StatusPanel


class Editor:
    """Main editor application controller."""
    
    def __init__(self):
        """Initialize the editor with component architecture."""
        self.root = None
        self.synth = None
        self.audio = None
        self.logger = setup_logger()
        
        # State variables
        self.current_instrument = 0
        
        # Synthesizer engine - initialized in initialize_synth
        self.synth_engine = None
        
        # UI Components - initialized after create_main_window
        self.menu_manager = None
        self.playback_controller = None
        self.waveform_display = None
        self.instrument_panel = None
        self.status_panel = None

    def initialize_synth(self):
        """Initialize the synthesizer."""
        try:
            self.synth = SynthWrapper()

            # Also initialize the synth_engine directly for parameter access
            self.synth_engine = synth_engine.SynthEngine()  # pylint: disable=c-extension-no-member
            self.synth_engine.initialize()

            return True
        except ImportError as e:
            self.logger.error("Failed to import synthesizer: %s", e)
            return False
        except RuntimeError as e:
            self.logger.error("Failed to initialize synthesizer: %s", e)
            return False

    def create_main_window(self):
        """Create the main application window with component architecture."""
        self.root = tk.Tk()
        self.root.title("4K Softsynth Editor")
        self.root.geometry("1200x900")
        
        # Initialize UI components
        self.menu_manager = MenuManager(self.root, self)
        self.playback_controller = PlaybackController(self)
        self.waveform_display = WaveformDisplay(self)
        self.instrument_panel = InstrumentPanel(self)
        self.status_panel = StatusPanel(self)
        
        # Create menu bar
        self.menu_manager.create_menu_bar()
        
        # Create main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self._configure_grid_weights(main_frame)
        
        # Create UI sections using components
        self.playback_controller.create_transport_section(main_frame)
        self.instrument_panel.create_instrument_section(main_frame)
        self.waveform_display.create_visualization_section(main_frame)
        self.status_panel.create_output_section(main_frame)
        self.status_panel.create_status_bar(main_frame)
        
        # Initialize audio
        self._initialize_audio()
        
        # Set up keyboard bindings
        self._setup_keyboard_bindings()
        
        # Set up window close handler
        self.root.protocol("WM_DELETE_WINDOW", self.menu_manager.on_window_close)
        
        # Initial output
        self.status_panel.log_output("4K Softsynth Editor - Tkinter Version")
        if self.synth.is_ready():
            self.status_panel.log_output("✓ ARM64 Synthesizer initialized and ready")
        else:
            self.status_panel.log_output("⚠ Running in simulation mode")
            
        # Add helpful instructions
        self.status_panel.log_output("💡 Press 'Q' key to play a synthesizer note!")
        if self.audio and self.audio.is_initialized:
            self.status_panel.log_output("🔊 Audio system ready for playback")
            
        # Initial waveform update - show current instrument waveform at startup
        self.waveform_display.auto_update_waveform_from_synth()

    def _configure_grid_weights(self, main_frame):
        """Configure grid weights for responsive layout."""
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(3, weight=1)

    def _initialize_audio(self):
        """Initialize the audio system."""
        try:
            self.audio = AudioDevice(sample_rate=44100)
            if self.audio.is_initialized:
                device_info = self.audio.get_device_info()
                self.status_panel.log_output(f"✓ Audio initialized: {device_info['device_name']}")
            else:
                self.status_panel.log_output("⚠ Audio initialization failed, running in silent mode")
        except (ImportError, OSError, RuntimeError) as e:
            self.logger.error("Audio initialization error: %s", e)
            self.status_panel.log_output(f"⚠ Audio error: {e}")
            self.audio = None

    def _setup_keyboard_bindings(self):
        """Set up keyboard event bindings."""
        # Make sure the window can receive focus and key events
        self.root.focus_set()

        # Bind key press events
        self.root.bind('<Key>', self.on_key_press)
        self.root.bind('<KeyPress-q>', self.on_q_key_press)

        # Make sure the window is focusable
        self.root.focus_force()

    def on_key_press(self, _event):
        """Handle general key press events."""
        # You can add other key handlers here if needed
        # Currently handled by specific key bindings like 'q'

    def on_q_key_press(self, _event):
        """Handle 'q' key press - play synthesizer note."""
        try:
            self.status_panel.log_output("🎵 Playing note (Q key pressed)...")

            # Get audio data from synthesizer
            audio_data = self.synth.render_instrument_note(self.current_instrument, 64)

            if audio_data is not None and len(audio_data) > 0:
                # Play the audio if audio system is available
                if self.audio and self.audio.is_initialized:
                    success = self.audio.play_samples(audio_data, blocking=False)
                    if success:
                        self.status_panel.log_output(f"✓ Playing {len(audio_data)} samples")
                    else:
                        self.status_panel.log_output("✗ Audio playback failed")
                else:
                    self.status_panel.log_output("✗ Audio system not available")
            else:
                self.status_panel.log_output("✗ No audio data generated")

        except (RuntimeError, ValueError, OSError) as e:
            self.logger.error("Error playing note: %s", e)
            self.status_panel.log_output(f"✗ Error playing note: {e}")

    def run(self):
        """Main application entry point."""
        if not self.initialize_synth():
            return 1

        try:
            self.create_main_window()
            self.root.mainloop()
            return 0
        except (tk.TclError, RuntimeError) as e:
            self.logger.error("Application error: %s", e)
            return 1
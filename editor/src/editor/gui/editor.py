"""
Main Editor Application for 4K Softsynth
Refactored with component architecture using CustomTkinter
"""

from typing import Optional, NamedTuple
import customtkinter as ctk

from editor.audio.synth_wrapper import SynthWrapper
from editor.audio.audio_device import AudioDevice
from editor.utils.logger import setup_logger
from .menu_manager import MenuManager
from .playback_controller import PlaybackController
from .waveform_display import WaveformDisplay
from .instrument_panel import InstrumentPanel
from .status_panel import StatusPanel


class UIComponents(NamedTuple):
    """Container for UI component instances."""
    menu_manager: MenuManager
    playback_controller: PlaybackController
    waveform_display: WaveformDisplay
    instrument_panel: InstrumentPanel
    status_panel: StatusPanel


class Editor:
    """Main editor application controller."""

    def __init__(self) -> None:
        """Initialize the editor with component architecture."""
        # Set CustomTkinter appearance mode and color theme
        ctk.set_appearance_mode("dark")  # Modes: "System" (standard), "Dark", "Light"
        ctk.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"
        self.root: Optional[ctk.CTk] = None
        self.synth: Optional[SynthWrapper] = None
        self.audio: Optional[AudioDevice] = None
        self.logger = setup_logger()
        self.current_instrument = 0
        self.components: Optional[UIComponents] = None

    def initialize_synth(self) -> bool:
        """Initialize the synthesizer."""
        try:
            self.synth = SynthWrapper()
            return True
        except ImportError as e:
            self.logger.error("Failed to import synthesizer: %s", e)
            return False
        except RuntimeError as e:
            self.logger.error("Failed to initialize synthesizer: %s", e)
            return False

    def create_main_window(self) -> None:
        """Create the main application window with component architecture."""
        self.root = ctk.CTk()
        self.root.title("4K Softsynth Editor")
        self.root.geometry("1200x900")

        # Initialize UI components
        self.components = UIComponents(
            menu_manager=MenuManager(self.root, self),
            playback_controller=PlaybackController(self),
            waveform_display=WaveformDisplay(self),
            instrument_panel=InstrumentPanel(self),
            status_panel=StatusPanel(self)
        )

        # Create menu bar
        self.components.menu_manager.create_menu_bar()

        # Create main frame
        main_frame = ctk.CTkFrame(self.root)
        main_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        # Configure grid weights
        self._configure_grid_weights(main_frame)

        # Create UI sections using components
        self.components.playback_controller.create_transport_section(main_frame)
        self.components.instrument_panel.create_instrument_section(main_frame)
        self.components.waveform_display.create_visualization_section(main_frame)
        self.components.status_panel.create_output_section(main_frame)
        self.components.status_panel.create_status_bar(main_frame)

        # Initialize audio
        self._initialize_audio()

        # Set up keyboard bindings
        self._setup_keyboard_bindings()

        # Set up window close handler
        self.root.protocol("WM_DELETE_WINDOW", self.components.menu_manager.on_window_close)

        # Initial output
        self.components.status_panel.log_output("4K Softsynth Editor - Tkinter Version")
        if self.synth.is_ready():
            self.components.status_panel.log_output("✓ ARM64 Synthesizer initialized and ready")
        else:
            self.components.status_panel.log_output("⚠ Running in simulation mode")

        # Add helpful instructions
        self.components.status_panel.log_output("💡 Press 'Q' key to play a synthesizer note!")
        if self.audio and self.audio.is_initialized:
            self.components.status_panel.log_output("🔊 Audio system ready for playback")

        # Initial waveform update - show current instrument waveform at startup
        self.components.waveform_display.auto_update_waveform_from_synth()

    def _configure_grid_weights(self, main_frame: ctk.CTkFrame) -> None:
        """Configure grid weights for responsive layout."""
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        # Give much more space to instrument panel (column 0) for sliders
        main_frame.columnconfigure(0, weight=4, minsize=700)  # Instrument panel gets 4/5 of space, min 600px
        main_frame.columnconfigure(1, weight=1, minsize=200)  # Waveform display gets 1/5 of space, min 200px
        # Configure all rows properly
        main_frame.rowconfigure(0, weight=0)  # Transport controls - fixed height
        main_frame.rowconfigure(1, weight=1)  # Main panels - expandable
        main_frame.rowconfigure(2, weight=0)  # Output section - fixed height  
        main_frame.rowconfigure(3, weight=0)  # Status bar - fixed height

    def _initialize_audio(self) -> None:
        """Initialize the audio system."""
        try:
            self.audio = AudioDevice(sample_rate=44100)
            if self.audio.is_initialized:
                device_info = self.audio.get_device_info()
                self.components.status_panel.log_output(
                    f"✓ Audio initialized: {device_info['device_name']}")
            else:
                self.components.status_panel.log_output(
                    "⚠ Audio initialization failed, running in silent mode")
        except (ImportError, OSError, RuntimeError) as e:
            self.logger.error("Audio initialization error: %s", e)
            self.components.status_panel.log_output(f"⚠ Audio error: {e}")
            self.audio = None

    def _setup_keyboard_bindings(self) -> None:
        """Set up keyboard event bindings."""
        # Make sure the window can receive focus and key events
        self.root.focus_set()

        # Bind key press events
        self.root.bind('<Key>', self.on_key_press)
        self.root.bind('<KeyPress-q>', self.on_q_key_press)

        # Make sure the window is focusable
        self.root.focus_force()

    def on_key_press(self, _event) -> None:
        """Handle general key press events."""
        # You can add other key handlers here if needed
        # Currently handled by specific key bindings like 'q'

    def on_q_key_press(self, _event) -> None:
        """Handle 'q' key press - play synthesizer note."""
        try:
            self.components.status_panel.log_output("🎵 Playing note (Q key pressed)...")

            # Get audio data from synthesizer
            audio_data = self.synth.render_instrument_note(self.current_instrument, 64)

            if audio_data is not None and len(audio_data) > 0:
                # Play the audio if audio system is available
                if self.audio and self.audio.is_initialized:
                    success = self.audio.play_samples(audio_data, blocking=False)
                    if success:
                        self.components.status_panel.log_output(
                            f"✓ Playing {len(audio_data)} samples")
                    else:
                        self.components.status_panel.log_output("✗ Audio playback failed")
                else:
                    self.components.status_panel.log_output("✗ Audio system not available")
            else:
                self.components.status_panel.log_output("✗ No audio data generated")

        except (RuntimeError, ValueError, OSError) as e:
            self.logger.error("Error playing note: %s", e)
            self.components.status_panel.log_output(f"✗ Error playing note: {e}")

    def run(self) -> int:
        """Main application entry point."""
        if not self.initialize_synth():
            return 1

        try:
            self.create_main_window()
            self.root.mainloop()
            return 0
        except RuntimeError as e:
            self.logger.error("Application error: %s", e)
            return 1

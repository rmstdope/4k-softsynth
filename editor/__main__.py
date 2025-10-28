#!/usr/bin/env python3
"""
Simple Tkinter-based GUI for 4K Softsynth Editor
Alternative to PySimpleGUI which has compatibility issues
"""

import os
import sys
import tkinter as tk
from tkinter import ttk, messagebox

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

matplotlib.use('TkAgg')

# Add the current directory to the Python path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# pylint: disable=import-error,wrong-import-position
from audio.synth_wrapper import SynthWrapper
from audio.audio_device import Audio
from utils.logger import setup_logger

# pylint: disable=too-many-instance-attributes,too-many-public-methods
class Editor:
    """Simple Tkinter-based editor for the synthesizer"""

    def __init__(self):
        """Initialize the Tkinter editor"""
        self.logger = setup_logger()
        self.synth = None
        self.root = None
        self.audio = None

        # UI state
        self.playing = False
        self.current_instrument = 0

        # Waveform visualization
        self.waveform_fig = None
        self.waveform_ax = None
        self.waveform_canvas = None

        # UI controls - initialized to None, will be set in create_main_window
        self.play_button = None
        self.tempo_var = None
        self.instrument_var = None
        self.attack_var = None
        self.decay_var = None
        self.sustain_var = None
        self.release_var = None
        self.gain_var = None
        self.output_text = None
        self.status_var = None

        # ADSR entry fields - initialized to None, will be set in _create_instrument_controllers
        self.attack_entry = None
        self.decay_entry = None
        self.sustain_entry = None
        self.release_entry = None
        self.gain_entry = None

    def initialize_synth(self):
        """Initialize the synthesizer"""
        try:
            self.synth = SynthWrapper()
            return True
        except ImportError as e:
            self.logger.error("Synthesizer import error: %s", e)
            messagebox.showerror("Error", f"Failed to import synthesizer: {e}")
            return False
        except RuntimeError as e:
            self.logger.error("Synthesizer runtime error: %s", e)
            messagebox.showerror("Error", f"Failed to initialize synthesizer: {e}")
            return False

    def _create_menu_bar(self):
        """Create the application menu bar"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New", command=self.new_project)
        file_menu.add_command(label="Open", command=self.open_project)
        file_menu.add_command(label="Save", command=self.save_project)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)

        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)

    def create_main_window(self):
        """Create the main application window"""
        self.root = tk.Tk()
        self.root.title("4K Softsynth Editor")
        self.root.geometry("1200x900")

        # Create menu bar
        self._create_menu_bar()

        # Create main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Configure grid weights
        self._configure_grid_weights(main_frame)

        # Create UI sections
        self._create_transport_controls(main_frame)
        self._create_instrument_controls(main_frame)
        self._create_visualization_section(main_frame)
        self._create_output_section(main_frame)
        self._create_status_bar(main_frame)

        # Initialize audio
        self._initialize_audio()

        # Set up keyboard bindings
        self._setup_keyboard_bindings()

        # Set up window close handler
        self.root.protocol("WM_DELETE_WINDOW", self.on_window_close)

        # Initial output
        self.log_output("4K Softsynth Editor - Tkinter Version")
        if self.synth.is_ready():
            self.log_output("✓ ARM64 Synthesizer initialized and ready")
        else:
            self.log_output("⚠ Running in simulation mode")

        # Add helpful instructions
        self.log_output("💡 Press 'Q' key to play a synthesizer note!")
        if self.audio and self.audio.is_initialized:
            self.log_output("🔊 Audio system ready for playback")

    def _configure_grid_weights(self, main_frame):
        """Configure grid weights for responsive layout"""
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(3, weight=1)

    def _initialize_audio(self):
        """Initialize the audio system"""
        try:
            self.audio = Audio(sample_rate=44100)
            if self.audio.is_initialized:
                device_info = self.audio.get_device_info()
                self.log_output(f"✓ Audio initialized: {device_info['device_name']}")
            else:
                self.log_output("⚠ Audio initialization failed, running in silent mode")
        except (ImportError, OSError, RuntimeError) as e:
            self.logger.error("Audio initialization error: %s", e)
            self.log_output(f"⚠ Audio error: {e}")
            self.audio = None

    def _setup_keyboard_bindings(self):
        """Set up keyboard event bindings"""
        # Make sure the window can receive focus and key events
        self.root.focus_set()

        # Bind key press events
        self.root.bind('<Key>', self.on_key_press)
        self.root.bind('<KeyPress-q>', self.on_q_key_press)

        # Make sure the window is focusable
        self.root.focus_force()

    def on_key_press(self, event):
        """Handle general key press events"""
        # You can add other key handlers here if needed
        # Currently handled by specific key bindings like 'q'

    def on_q_key_press(self, _event):
        """Handle 'q' key press - play synthesizer note"""
        try:
            self.log_output("🎵 Playing note (Q key pressed)...")

            # Get audio data from synthesizer
            audio_data = self.synth.render_instrument_note(self.current_instrument, 64)

            if audio_data is not None and len(audio_data) > 0:
                # Play the audio if audio system is available
                if self.audio and self.audio.is_initialized:
                    success = self.audio.play_samples(audio_data, blocking=False)
                    if success:
                        self.log_output(f"✓ Playing {len(audio_data)} samples")
                    else:
                        self.log_output("✗ Audio playback failed")
                else:
                    self.log_output("✗ Audio system not available")
            else:
                self.log_output("✗ No audio data generated")

        except (RuntimeError, ValueError, OSError) as e:
            self.logger.error("Error playing note: %s", e)
            self.log_output(f"✗ Error playing note: {e}")

    def on_window_close(self):
        """Handle window close event - cleanup resources"""
        try:
            # Cleanup audio
            if self.audio:
                self.audio.cleanup()
                self.log_output("✓ Audio cleanup completed")

            # Close the window
            self.root.destroy()
        except (RuntimeError, tk.TclError) as e:
            self.logger.error("Error during cleanup: %s", e)
            self.root.destroy()

    def _create_transport_controls(self, main_frame):
        """Create transport control section"""
        transport_frame = ttk.LabelFrame(main_frame, text="Song Controls",
                                       padding="5")
        transport_frame.grid(row=0, column=0, columnspan=2,
                           sticky=(tk.W, tk.E), pady=(0, 10))

        self.play_button = ttk.Button(transport_frame, text="Play",
                                    command=self.toggle_play)
        self.play_button.pack(side=tk.LEFT, padx=(0, 5))

        ttk.Button(transport_frame, text="Stop",
                  command=self.stop_playback).pack(side=tk.LEFT, padx=(0, 5))

        ttk.Label(transport_frame, text="Tempo:").pack(side=tk.LEFT,
                                                      padx=(10, 5))
        self.tempo_var = tk.IntVar(value=125)
        tempo_spinbox = ttk.Spinbox(transport_frame, from_=60, to=200,
                                   textvariable=self.tempo_var, width=5)
        tempo_spinbox.pack(side=tk.LEFT)
        ttk.Label(transport_frame, text="BPM").pack(side=tk.LEFT,
                                                   padx=(5, 0))
    def _create_instrument_controls(self, main_frame):
        """Create instrument control section"""
        instrument_frame = ttk.LabelFrame(main_frame, text="Instrument Controls",
                                        padding="5")
        instrument_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S),
                            pady=(0, 10))

        # Instrument selector
        ttk.Label(instrument_frame, text="Instrument:").grid(row=0, column=0,
                                                           sticky=tk.W)
        self.instrument_var = tk.StringVar(value="Instrument 0")
        instrument_values = ["Instrument 0", "Instrument 1",
                           "Instrument 2", "Instrument 3"]
        instrument_combo = ttk.Combobox(instrument_frame,
                                      textvariable=self.instrument_var,
                                      values=instrument_values)
        instrument_combo.grid(row=0, column=1, sticky=(tk.W, tk.E),
                            padx=(5, 0))
        instrument_combo.bind('<<ComboboxSelected>>', self.on_instrument_change)

        # Instrument controls
        ttk.Label(instrument_frame, text="Instrument controls:").grid(
            row=1, column=0, columnspan=2, sticky=tk.W, pady=(10, 5))

        self._create_instrument_controllers(instrument_frame)
        instrument_frame.columnconfigure(1, weight=1)

    def _create_instrument_controllers(self, parent_frame):
        """Create instrument control sliders with value fields"""
        # Configure grid columns
        parent_frame.columnconfigure(1, weight=2)  # Slider column
        parent_frame.columnconfigure(2, weight=0)  # Value field column

        # Attack
        ttk.Label(parent_frame, text="Attack:").grid(row=2, column=0, sticky=tk.W)
        self.attack_var = tk.DoubleVar(value=0.1)
        attack_scale = ttk.Scale(parent_frame, from_=0.0, to=1.0,
                               variable=self.attack_var, orient=tk.HORIZONTAL,
                               command=self.on_attack_slider_change)
        attack_scale.grid(row=2, column=1, sticky=(tk.W, tk.E), padx=(5, 5))

        self.attack_entry = ttk.Entry(parent_frame, width=8, justify=tk.CENTER)
        self.attack_entry.grid(row=2, column=2, sticky=tk.W, padx=(0, 5))
        self.attack_entry.insert(0, "0.10")
        self.attack_entry.bind('<Return>', self.on_attack_entry_change)
        self.attack_entry.bind('<FocusOut>', self.on_attack_entry_change)

        # Decay
        ttk.Label(parent_frame, text="Decay:").grid(row=3, column=0, sticky=tk.W)
        self.decay_var = tk.DoubleVar(value=0.2)
        decay_scale = ttk.Scale(parent_frame, from_=0.0, to=1.0,
                              variable=self.decay_var, orient=tk.HORIZONTAL,
                              command=self.on_decay_slider_change)
        decay_scale.grid(row=3, column=1, sticky=(tk.W, tk.E), padx=(5, 5))

        self.decay_entry = ttk.Entry(parent_frame, width=8, justify=tk.CENTER)
        self.decay_entry.grid(row=3, column=2, sticky=tk.W, padx=(0, 5))
        self.decay_entry.insert(0, "0.20")
        self.decay_entry.bind('<Return>', self.on_decay_entry_change)
        self.decay_entry.bind('<FocusOut>', self.on_decay_entry_change)

        # Sustain
        ttk.Label(parent_frame, text="Sustain:").grid(row=4, column=0, sticky=tk.W)
        self.sustain_var = tk.DoubleVar(value=0.7)
        sustain_scale = ttk.Scale(parent_frame, from_=0.0, to=1.0,
                                variable=self.sustain_var, orient=tk.HORIZONTAL,
                                command=self.on_sustain_slider_change)
        sustain_scale.grid(row=4, column=1, sticky=(tk.W, tk.E), padx=(5, 5))

        self.sustain_entry = ttk.Entry(parent_frame, width=8, justify=tk.CENTER)
        self.sustain_entry.grid(row=4, column=2, sticky=tk.W, padx=(0, 5))
        self.sustain_entry.insert(0, "0.70")
        self.sustain_entry.bind('<Return>', self.on_sustain_entry_change)
        self.sustain_entry.bind('<FocusOut>', self.on_sustain_entry_change)

        # Release
        ttk.Label(parent_frame, text="Release:").grid(row=5, column=0, sticky=tk.W)
        self.release_var = tk.DoubleVar(value=0.5)
        release_scale = ttk.Scale(parent_frame, from_=0.0, to=1.0,
                                variable=self.release_var, orient=tk.HORIZONTAL,
                                command=self.on_release_slider_change)
        release_scale.grid(row=5, column=1, sticky=(tk.W, tk.E), padx=(5, 5))

        self.release_entry = ttk.Entry(parent_frame, width=8, justify=tk.CENTER)
        self.release_entry.grid(row=5, column=2, sticky=tk.W, padx=(0, 5))
        self.release_entry.insert(0, "0.50")
        self.release_entry.bind('<Return>', self.on_release_entry_change)
        self.release_entry.bind('<FocusOut>', self.on_release_entry_change)

        # Gain
        ttk.Label(parent_frame, text="Gain:").grid(row=6, column=0, sticky=tk.W)
        self.gain_var = tk.DoubleVar(value=0.8)
        gain_scale = ttk.Scale(parent_frame, from_=0.0, to=1.0,
                             variable=self.gain_var, orient=tk.HORIZONTAL,
                             command=self.on_gain_slider_change)
        gain_scale.grid(row=6, column=1, sticky=(tk.W, tk.E), padx=(5, 5))

        self.gain_entry = ttk.Entry(parent_frame, width=8, justify=tk.CENTER)
        self.gain_entry.grid(row=6, column=2, sticky=tk.W, padx=(0, 5))
        self.gain_entry.insert(0, "0.80")
        self.gain_entry.bind('<Return>', self.on_gain_entry_change)
        self.gain_entry.bind('<FocusOut>', self.on_gain_entry_change)
    def _create_visualization_section(self, main_frame):
        """Create visualization section"""
        viz_frame = ttk.LabelFrame(main_frame, text="Instrument Visualization",
                                 padding="5")
        viz_frame.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S),
                     padx=(10, 0), pady=(0, 10))
        viz_frame.columnconfigure(0, weight=1)
        viz_frame.rowconfigure(0, weight=1)

        # Waveform display
        self.setup_waveform_display(viz_frame)

    def _create_output_section(self, main_frame):
        """Create output text section"""
        output_frame = ttk.LabelFrame(main_frame, text="Output", padding="5")
        output_frame.grid(row=2, column=0, columnspan=2,
                        sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        output_frame.columnconfigure(0, weight=1)
        output_frame.rowconfigure(0, weight=1)

        self.output_text = tk.Text(output_frame, height=8, wrap=tk.WORD)
        scrollbar = ttk.Scrollbar(output_frame, orient=tk.VERTICAL,
                                command=self.output_text.yview)
        self.output_text.configure(yscrollcommand=scrollbar.set)

        self.output_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))

    def _create_status_bar(self, main_frame):
        """Create status bar"""
        self.status_var = tk.StringVar(value="Ready")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var,
                             relief=tk.SUNKEN, anchor=tk.W)
        status_bar.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E))

    def log_output(self, message):
        """Add a message to the output text area"""
        self.output_text.insert(tk.END, message + "\n")
        self.output_text.see(tk.END)

    def on_instrument_change(self, _event):
        """Handle instrument selection change"""
        selection = self.instrument_var.get()
        if selection:
            self.current_instrument = int(selection.split()[-1])
            self.log_output(f"Selected {selection}")
            self.update_synth_parameters()

    def on_attack_slider_change(self, value):
        """Handle attack slider changes"""
        self.attack_entry.delete(0, tk.END)
        self.attack_entry.insert(0, f"{float(value):.2f}")
        self.update_synth_parameters()

    def on_attack_entry_change(self, _event):
        """Handle attack entry field changes"""
        try:
            value = float(self.attack_entry.get())
            value = max(0.0, min(1.0, value))  # Clamp to valid range
            self.attack_var.set(value)
            self.attack_entry.delete(0, tk.END)
            self.attack_entry.insert(0, f"{value:.2f}")
            self.update_synth_parameters()
        except ValueError:
            # Reset to current slider value if invalid input
            self.attack_entry.delete(0, tk.END)
            self.attack_entry.insert(0, f"{self.attack_var.get():.2f}")

    def on_decay_slider_change(self, value):
        """Handle decay slider changes"""
        self.decay_entry.delete(0, tk.END)
        self.decay_entry.insert(0, f"{float(value):.2f}")
        self.update_synth_parameters()

    def on_decay_entry_change(self, _event):
        """Handle decay entry field changes"""
        try:
            value = float(self.decay_entry.get())
            value = max(0.0, min(1.0, value))  # Clamp to valid range
            self.decay_var.set(value)
            self.decay_entry.delete(0, tk.END)
            self.decay_entry.insert(0, f"{value:.2f}")
            self.update_synth_parameters()
        except ValueError:
            # Reset to current slider value if invalid input
            self.decay_entry.delete(0, tk.END)
            self.decay_entry.insert(0, f"{self.decay_var.get():.2f}")

    def on_sustain_slider_change(self, value):
        """Handle sustain slider changes"""
        self.sustain_entry.delete(0, tk.END)
        self.sustain_entry.insert(0, f"{float(value):.2f}")
        self.update_synth_parameters()

    def on_sustain_entry_change(self, _event):
        """Handle sustain entry field changes"""
        try:
            value = float(self.sustain_entry.get())
            value = max(0.0, min(1.0, value))  # Clamp to valid range
            self.sustain_var.set(value)
            self.sustain_entry.delete(0, tk.END)
            self.sustain_entry.insert(0, f"{value:.2f}")
            self.update_synth_parameters()
        except ValueError:
            # Reset to current slider value if invalid input
            self.sustain_entry.delete(0, tk.END)
            self.sustain_entry.insert(0, f"{self.sustain_var.get():.2f}")

    def on_release_slider_change(self, value):
        """Handle release slider changes"""
        self.release_entry.delete(0, tk.END)
        self.release_entry.insert(0, f"{float(value):.2f}")
        self.update_synth_parameters()

    def on_release_entry_change(self, _event):
        """Handle release entry field changes"""
        try:
            value = float(self.release_entry.get())
            value = max(0.0, min(1.0, value))  # Clamp to valid range
            self.release_var.set(value)
            self.release_entry.delete(0, tk.END)
            self.release_entry.insert(0, f"{value:.2f}")
            self.update_synth_parameters()
        except ValueError:
            # Reset to current slider value if invalid input
            self.release_entry.delete(0, tk.END)
            self.release_entry.insert(0, f"{self.release_var.get():.2f}")

    def on_gain_slider_change(self, value):
        """Handle gain slider changes"""
        self.gain_entry.delete(0, tk.END)
        self.gain_entry.insert(0, f"{float(value):.2f}")
        self.update_synth_parameters()

    def on_gain_entry_change(self, _event):
        """Handle gain entry field changes"""
        try:
            value = float(self.gain_entry.get())
            value = max(0.0, min(1.0, value))  # Clamp to valid range
            self.gain_var.set(value)
            self.gain_entry.delete(0, tk.END)
            self.gain_entry.insert(0, f"{value:.2f}")
            self.update_synth_parameters()
        except ValueError:
            # Reset to current slider value if invalid input
            self.gain_entry.delete(0, tk.END)
            self.gain_entry.insert(0, f"{self.gain_var.get():.2f}")

    def update_synth_parameters(self):
        """Update synthesizer parameters based on UI controls"""
        if self.synth:
            try:
                # Note: ADSR parameters are not yet implemented in the ARM64 engine
                # For now, just update the waveform display
                status_msg = f"Updated parameters for instrument {self.current_instrument}"
                self.status_var.set(status_msg)

                # Auto-refresh the waveform display
                self.auto_update_waveform()

            except (RuntimeError, ValueError) as e:
                self.log_output(f"Error updating parameters: {e}")

    def toggle_play(self):
        """Toggle play/pause"""
        if not self.playing:
            self.start_playback()
        else:
            self.pause_playback()

    def start_playback(self):
        """Start playback"""
        self.playing = True
        self.play_button.config(text="Pause")
        self.status_var.set("Playing...")
        self.log_output("Playback started")
        # FIXME: Implement actual continuous playback  # pylint: disable=fixme

    def pause_playback(self):
        """Pause playback"""
        self.playing = False
        self.play_button.config(text="Play")
        self.status_var.set("Paused")
        self.log_output("Playback paused")

    def stop_playback(self):
        """Stop playback"""
        self.playing = False
        self.play_button.config(text="Play")
        self.status_var.set("Stopped")
        self.log_output("Playback stopped")

    def test_arm64_engine(self):
        """Test the ARM64 engine"""
        self.log_output("Testing ARM64 Synthesizer...")
        try:
            # Generate audio using render_note
            audio_data = self.synth.render_note()

            if audio_data is not None and len(audio_data) > 0:
                self.log_output(f"✓ Generated {len(audio_data)} samples")
                min_val = np.min(audio_data)
                max_val = np.max(audio_data)
                self.log_output(f"  Sample range: {min_val:.3f} to {max_val:.3f}")
                self.log_output(f"  RMS level: {np.sqrt(np.mean(audio_data**2)):.3f}")

                # Open modal window with graph
                self.show_audio_graph(audio_data)
            else:
                self.log_output("✗ Failed to generate audio")
        except (ImportError, OSError, RuntimeError) as e:
            self.log_output(f"✗ ARM64 test failed: {e}")

    def show_audio_graph(self, audio_data):
        """Show audio waveform in a modal window"""
        try:
            self._create_audio_graph_window(audio_data)
        except ImportError as e:
            messagebox.showerror("Error", f"Matplotlib not available: {e}")
            self.log_output("✗ Cannot show graph: matplotlib not available")
        except (RuntimeError, ValueError) as e:
            messagebox.showerror("Error", f"Failed to create graph: {e}")
            self.log_output(f"✗ Graph creation failed: {e}")

    def _create_audio_graph_window(self, audio_data):
        """Create the audio graph modal window"""
        # Create modal window
        graph_window = tk.Toplevel(self.root)
        graph_window.title("ARM64 Engine Audio Output")
        graph_window.geometry("1200x900")
        graph_window.transient(self.root)
        graph_window.grab_set()  # Make it modal

        # Center the window
        self._center_window(graph_window, 1200, 900)

        # Create matplotlib plots
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))
        self._plot_waveform_analysis(fig, ax1, ax2, audio_data)

        # Create canvas and add to window
        canvas = FigureCanvasTkAgg(fig, graph_window)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Add info frame with controls
        self._create_graph_info_frame(graph_window, audio_data)

        self.log_output("📊 Audio analysis window opened")

    def _center_window(self, window, width, height):
        """Center a window on the screen"""
        window.update_idletasks()
        x = (window.winfo_screenwidth() // 2) - (width // 2)
        y = (window.winfo_screenheight() // 2) - (height // 2)
        window.geometry(f"{width}x{height}+{x}+{y}")

    def _plot_waveform_analysis(self, fig, ax1, ax2, audio_data):
        """Create waveform and spectrum plots"""
        fig.suptitle('ARM64 Synthesizer Output Analysis', fontsize=14)

        # Plot waveform
        time_axis = np.arange(len(audio_data)) / 44100.0  # Assuming 44.1kHz
        ax1.plot(time_axis, audio_data, 'b-', linewidth=0.8)
        ax1.set_title('Waveform')
        ax1.set_xlabel('Time (seconds)')
        ax1.set_ylabel('Amplitude')
        ax1.grid(True, alpha=0.3)
        ax1.set_ylim([-1.1, 1.1])

        # Plot frequency spectrum (FFT)
        self._plot_frequency_spectrum(ax2, audio_data)
        plt.tight_layout()

    def _plot_frequency_spectrum(self, ax2, audio_data):
        """Plot frequency spectrum of audio data"""
        if len(audio_data) > 1:
            fft_data = np.fft.fft(audio_data[:min(len(audio_data), 4096)])
            freqs = np.fft.fftfreq(len(fft_data), 1/44100.0)
            magnitude = np.abs(fft_data)

            # Only plot positive frequencies
            positive_freqs = freqs[:len(freqs)//2]
            positive_magnitude = magnitude[:len(magnitude)//2]

            ax2.semilogy(positive_freqs, positive_magnitude, 'r-', linewidth=0.8)
            ax2.set_title('Frequency Spectrum (First 4096 samples)')
            ax2.set_xlabel('Frequency (Hz)')
            ax2.set_ylabel('Magnitude (log scale)')
            ax2.grid(True, alpha=0.3)
            ax2.set_xlim([0, 22050])  # Nyquist frequency
        else:
            ax2.text(0.5, 0.5, 'Insufficient data for FFT',
                    horizontalalignment='center', verticalalignment='center',
                    transform=ax2.transAxes)

    def _create_graph_info_frame(self, graph_window, audio_data):
        """Create info frame with statistics and controls"""
        info_frame = ttk.Frame(graph_window)
        info_frame.pack(fill=tk.X, padx=10, pady=(0, 10))

        # Audio statistics
        stats_text = (f"Samples: {len(audio_data)} | "
                     f"Duration: {len(audio_data)/44100.0:.3f}s | "
                     f"Min: {np.min(audio_data):.4f} | "
                     f"Max: {np.max(audio_data):.4f} | "
                     f"RMS: {np.sqrt(np.mean(audio_data**2)):.4f}")

        ttk.Label(info_frame, text=stats_text).pack(side=tk.LEFT)

        # Close button
        ttk.Button(info_frame, text="Close",
                  command=graph_window.destroy).pack(side=tk.RIGHT)

        # Save data button
        def save_data():
            try:
                filename = f"arm64_output_{len(audio_data)}_samples.txt"
                np.savetxt(filename, audio_data)
                self.log_output(f"✓ Audio data saved to {filename}")
            except (OSError, ValueError) as e:
                self.log_output(f"✗ Save failed: {e}")

        ttk.Button(info_frame, text="Save Data",
                  command=save_data).pack(side=tk.RIGHT, padx=(0, 5))

    # def play_test_note(self):
    #     """Play a test note (A4 = 440Hz)"""
    #     self.log_output("Playing A4 test note...")
    #     try:
    #         # Update parameters first
    #         self.update_synth_parameters()

    #         # Trigger A4 note (MIDI note 69)
    #         self.synth.trigger_note(self.current_instrument, 69, 0.8)

    #         # Generate 2 seconds of audio
    #         num_samples = self.synth.get_sample_rate() * 2
    #         audio_data = self.synth.render_audio(num_samples)

    #         if audio_data is not None:
    #             self.log_output(f"✓ Generated test note: {len(audio_data)} samples")
    #             # FIXME: Play the audio through system audio
    #         else:
    #             self.log_output("✗ Failed to generate test note")
    #     except (RuntimeError, ValueError) as e:
    #         self.log_output(f"✗ Test note failed: {e}")

    # def generate_sample(self):
    #     """Generate a sample audio file"""
    #     self.log_output("Generating sample audio file...")
    #     try:
    #         # Set up parameters for a chord
    #         self.update_synth_parameters()

    #         # Trigger a C major chord (C4, E4, G4)
    #         self.synth.trigger_note(0, 60, 0.7)  # C4
    #         self.synth.trigger_note(1, 64, 0.7)  # E4
    #         self.synth.trigger_note(2, 67, 0.7)  # G4

    #         # Generate 3 seconds of audio
    #         num_samples = self.synth.get_sample_rate() * 3
    #         audio_data = self.synth.render_audio(num_samples)

    #         if audio_data is not None:
    #             # Save first 1000 samples to text file
    #             output_file = "sample_chord.txt"
    #             np.savetxt(output_file, audio_data[:1000])
    #             self.log_output(f"✓ Sample chord saved to {output_file}")
    #             duration = len(audio_data) // 88200
    #             self.log_output(f"  Generated {len(audio_data)} samples "
    #                           f"({duration:.1f}s)")
    #         else:
    #             self.log_output("✗ Failed to generate sample")
    #     except (RuntimeError, ValueError, OSError) as e:
    #         self.log_output(f"✗ Sample generation failed: {e}")

    # def run_performance_test(self):
    #     """Run a performance test"""
    #     self.log_output("Running performance test...")
    #     try:
    #         test_samples = self.synth.get_sample_rate()  # 1 second
    #         iterations = 10

    #         start_time = time.time()

    #         for i in range(iterations):
    #             audio_data = self.synth.render_audio(test_samples)
    #             if audio_data is None:
    #                 self.log_output(f"✗ Failed at iteration {i+1}")
    #                 return

    #         end_time = time.time()
    #         total_time = end_time - start_time
    #         audio_time = (test_samples * iterations) / self.synth.get_sample_rate()

    #         self.log_output("✓ Performance test completed:")
    #         self.log_output(f"  Render time: {total_time:.3f}s, "
    #                       f"Audio time: {audio_time:.3f}s")
    #         self.log_output(f"  Real-time factor: {audio_time/total_time:.2f}x")

    #     except (RuntimeError, ValueError) as e:
    #         self.log_output(f"✗ Performance test failed: {e}")

    def new_project(self):
        """Create new project"""
        self.log_output("New project created")

    def open_project(self):
        """Open project"""
        self.log_output("Open project - not implemented")

    def save_project(self):
        """Save project"""
        self.log_output("Save project - not implemented")

    def show_about(self):
        """Show about dialog"""
        about_text = ("4K Softsynth Editor - Tkinter Version\n\n"
                     "ARM64 Assembly Synthesizer Interface\n"
                     "Built with Python and Tkinter")
        messagebox.showinfo("About", about_text)

    def setup_waveform_display(self, parent_frame):
        """Set up the embedded waveform display"""
        try:
            self._create_waveform_plot(parent_frame)
            # Auto-update waveform after a short delay to allow synth initialization
            self.root.after(100, self.auto_update_waveform)

            # Log only if output_text is available
            if hasattr(self, 'output_text') and self.output_text:
                self.log_output("✓ Waveform display initialized")

        except ImportError:
            self._create_fallback_display(parent_frame,
                                        "Matplotlib not available for waveform display")
            if hasattr(self, 'output_text') and self.output_text:
                self.log_output("⚠ Waveform display unavailable: matplotlib not found")
        except (RuntimeError, ValueError) as e:
            self._create_fallback_display(parent_frame, f"Waveform display error: {e}")
            if hasattr(self, 'output_text') and self.output_text:
                self.log_output(f"✗ Waveform display setup failed: {e}")

    def _create_waveform_plot(self, parent_frame):
        """Create the matplotlib waveform plot"""
        # Create matplotlib figure
        self.waveform_fig, self.waveform_ax = plt.subplots(figsize=(6, 3))
        self.waveform_fig.patch.set_facecolor('white')

        # Configure the plot
        self.waveform_ax.set_title('Waveform Visualization')
        self.waveform_ax.set_xlabel('Time (samples)')
        self.waveform_ax.set_ylabel('Amplitude')
        self.waveform_ax.grid(True, alpha=0.3)
        self.waveform_ax.set_ylim([-1.1, 1.1])

        # Initial empty plot
        self.waveform_ax.text(0.5, 0.5, 'Loading waveform...',
                             horizontalalignment='center',
                             verticalalignment='center',
                             transform=self.waveform_ax.transAxes,
                             fontsize=10, alpha=0.7)

        # Create canvas and add to parent frame
        self.waveform_canvas = FigureCanvasTkAgg(self.waveform_fig, parent_frame)
        self.waveform_canvas.draw()
        canvas_widget = self.waveform_canvas.get_tk_widget()
        canvas_widget.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

    def _create_fallback_display(self, parent_frame, message):
        """Create fallback display when matplotlib is not available"""
        fallback_label = ttk.Label(parent_frame, text=message)
        fallback_label.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

    def auto_update_waveform(self):
        """Automatically update the waveform display"""
        if not self.waveform_ax or not self.synth:
            return

        try:
            # Get audio data from synthesizer
            audio_data = self.synth.render_instrument_note(self.current_instrument, 64)

            if audio_data is not None and len(audio_data) > 0:
                self._update_waveform_plot(audio_data)
            else:
                self._show_empty_waveform_state()

        except (RuntimeError, ValueError) as e:
            if hasattr(self, 'output_text') and self.output_text:
                self.log_output(f"Auto-waveform update failed: {e}")

    def _update_waveform_plot(self, audio_data):
        """Update the waveform plot with new data"""
        # Clear previous plot
        self.waveform_ax.clear()

        # Configure the plot
        self.waveform_ax.set_xlabel('Time (samples)')
        self.waveform_ax.set_ylabel('Amplitude')
        self.waveform_ax.grid(True, alpha=0.3)

        # Plot the waveform
        display_samples = len(audio_data)
        time_axis = np.arange(display_samples)
        self.waveform_ax.plot(time_axis, audio_data[:display_samples],
                             'b-', linewidth=0.8)

        # Update canvas
        if self.waveform_canvas:
            self.waveform_canvas.draw()

    def _show_empty_waveform_state(self):
        """Show empty state when no audio data is available"""
        self.waveform_ax.clear()
        self.waveform_ax.set_title('Instrument Waveform')
        self.waveform_ax.set_xlabel('Time (samples)')
        self.waveform_ax.set_ylabel('Amplitude')
        self.waveform_ax.grid(True, alpha=0.3)
        self.waveform_ax.set_ylim([-1.1, 1.1])
        self.waveform_ax.text(0.5, 0.5, 'No audio data available',
                             horizontalalignment='center',
                             verticalalignment='center',
                             transform=self.waveform_ax.transAxes,
                             fontsize=10, alpha=0.7)

        if self.waveform_canvas:
            self.waveform_canvas.draw()

    def run(self):
        """Main application entry point"""
        if not self.initialize_synth():
            return 1

        try:
            self.create_main_window()
            self.root.mainloop()
            return 0
        except (tk.TclError, RuntimeError) as e:
            self.logger.error("Application error: %s", e)
            if self.root:
                messagebox.showerror("Error", f"Application error: {e}")
            return 1

def main():
    """Main entry point"""
    app = Editor()
    return app.run()

if __name__ == "__main__":
    sys.exit(main())

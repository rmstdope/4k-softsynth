"""Waveform display component for the audio editor using CustomTkinter."""

import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure


class WaveformDisplay:
    """Manages audio waveform visualization and display."""

    def __init__(self, main_editor):
        """Initialize the waveform display.

        Args:
            main_editor: Reference to the main editor controller
        """
        self.main_editor = main_editor
        self.waveform_fig = None
        self.waveform_ax = None
        self.waveform_canvas = None

    def create_visualization_section(self, parent_frame):
        """Create visualization section."""
        visualization_frame = ctk.CTkFrame(parent_frame, corner_radius=10)
        visualization_frame.grid(row=1, column=1, sticky="nsew", padx=5, pady=(0, 10))

        # Title label
        title_label = ctk.CTkLabel(visualization_frame, text="Waveform Display",
                                  font=ctk.CTkFont(size=16, weight="bold"))
        title_label.pack(pady=(15, 10))

        self.setup_waveform_display(visualization_frame)

    def setup_waveform_display(self, parent_frame):
        """Setup the waveform display area."""
        self._create_waveform_plot(parent_frame)

    def _create_waveform_plot(self, parent_frame):
        """Create the matplotlib waveform plot."""
        self.waveform_fig = Figure(figsize=(8, 4), dpi=80)
        self.waveform_ax = self.waveform_fig.add_subplot(111)

        # Configure the plot
        self.waveform_ax.set_title('Instrument Waveform')
        self.waveform_ax.set_xlabel('Time (samples)')
        self.waveform_ax.set_ylabel('Amplitude')
        self.waveform_ax.grid(True, alpha=0.3)
        self.waveform_ax.set_ylim([-1.1, 1.1])

        # Create canvas
        self.waveform_canvas = FigureCanvasTkAgg(self.waveform_fig, parent_frame)
        self.waveform_canvas.draw()
        self.waveform_canvas.get_tk_widget().pack(fill="both", expand=True, padx=15, pady=(0, 15))

        # Show empty state initially
        self._show_empty_waveform_state()



    def auto_update_waveform_from_synth(self):
        """Automatically update waveform display from current synth parameters."""
        try:
            if not self.main_editor.synth:
                return

            # Get audio data from synthesizer
            audio_data = self.main_editor.synth.render_instrument_note(
                self.main_editor.current_instrument, 64)

            if audio_data is not None and len(audio_data) > 0:
                self._update_waveform_plot(audio_data)
            else:
                self._show_empty_waveform_state()

        except (RuntimeError, ValueError) as e:
            if hasattr(self.main_editor, 'status_panel'):
                self.main_editor.status_panel.log_output(f"Auto-waveform update failed: {e}")

    def _update_waveform_plot(self, audio_data):
        """Update the waveform plot with new data."""
        if not self.waveform_ax or not self.waveform_canvas:
            return

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
        self.waveform_canvas.draw()

    def _show_empty_waveform_state(self):
        """Show empty state when no audio data is available."""
        if not self.waveform_ax or not self.waveform_canvas:
            return

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

        self.waveform_canvas.draw()

    def show_audio_graph(self, audio_data):
        """Show audio waveform in a modal window."""
        try:
            self._create_audio_graph_window(audio_data)
        except (RuntimeError, ValueError) as e:
            messagebox.showerror("Error", f"Failed to create graph: {e}")
            if hasattr(self.main_editor, 'status_panel'):
                self.main_editor.status_panel.log_output(f"✗ Graph creation failed: {e}")

    def _create_audio_graph_window(self, audio_data):
        """Create the audio graph modal window."""
        # Create modal window
        graph_window = tk.Toplevel(self.main_editor.root)
        graph_window.title("ARM64 Engine Audio Output")
        graph_window.geometry("1200x900")
        graph_window.transient(self.main_editor.root)
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

        if hasattr(self.main_editor, 'status_panel'):
            self.main_editor.status_panel.log_output("📊 Audio analysis window opened")

    def _center_window(self, window, width, height):
        """Center a window on the screen."""
        window.update_idletasks()
        x = (window.winfo_screenwidth() // 2) - (width // 2)
        y = (window.winfo_screenheight() // 2) - (height // 2)
        window.geometry(f"{width}x{height}+{x}+{y}")

    def _plot_waveform_analysis(self, fig, ax1, ax2, audio_data):
        """Create waveform and spectrum plots."""
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
        """Plot frequency spectrum of audio data."""
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
        """Create info frame with statistics and controls."""
        info_frame = ctk.CTkFrame(graph_window)
        info_frame.pack(fill="x", padx=10, pady=(0, 10))

        # Audio statistics
        stats_text = (f"Samples: {len(audio_data)} | "
                     f"Duration: {len(audio_data)/44100.0:.3f}s | "
                     f"Min: {np.min(audio_data):.4f} | "
                     f"Max: {np.max(audio_data):.4f} | "
                     f"RMS: {np.sqrt(np.mean(audio_data**2)):.4f}")

        stats_label = ctk.CTkLabel(info_frame, text=stats_text,
                                  font=ctk.CTkFont(size=10))
        stats_label.pack(pady=10)

        # Close button
        close_button = ctk.CTkButton(info_frame, text="Close",
                                    command=graph_window.destroy,
                                    width=100, height=32)
        close_button.pack(pady=(0, 10))

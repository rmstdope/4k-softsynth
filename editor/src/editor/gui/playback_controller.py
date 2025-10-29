"""Playback controller component for the audio editor."""

import tkinter as tk
from tkinter import ttk


class PlaybackController:
    """Manages transport controls and playback state."""

    def __init__(self, main_editor):
        """Initialize the playback controller.
        
        Args:
            main_editor: Reference to the main editor controller
        """
        self.main_editor = main_editor
        self.play_button = None
        self.tempo_var = None
        self.is_playing = False
        self.playing = False

    def create_transport_section(self, parent_frame):
        """Create transport control section."""
        transport_frame = ttk.LabelFrame(parent_frame, text="Song Controls",
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

    def toggle_play(self):
        """Toggle play/pause state."""
        if self.is_playing:
            self.pause_playback()
        else:
            self.start_playback()

    def start_playback(self):
        """Start playback."""
        self.is_playing = True
        self.playing = True
        if self.play_button:
            self.play_button.config(text="Pause")
        if hasattr(self.main_editor, 'status_panel'):
            self.main_editor.status_panel.log_output("▶ Playback started")

    def pause_playback(self):
        """Pause playback."""
        self.is_playing = False
        self.playing = False
        if self.play_button:
            self.play_button.config(text="Play")
        if hasattr(self.main_editor, 'status_panel'):
            self.main_editor.status_panel.log_output("⏸ Playback paused")

    def stop_playback(self):
        """Stop playback."""
        self.is_playing = False
        self.playing = False
        if self.play_button:
            self.play_button.config(text="Play")
        if hasattr(self.main_editor, 'status_panel'):
            self.main_editor.status_panel.log_output("⏹ Playback stopped")

    def test_arm64_engine(self):
        """Test the ARM64 synthesizer engine."""
        try:
            if hasattr(self.main_editor, 'status_panel'):
                self.main_editor.status_panel.log_output("🔧 Testing ARM64 engine...")

            # Get audio data from synthesizer
            if self.main_editor.synth:
                audio_data = self.main_editor.synth.render_instrument_note(
                    self.main_editor.current_instrument, 64)

                if audio_data is not None and len(audio_data) > 0:
                    if hasattr(self.main_editor, 'status_panel'):
                        self.main_editor.status_panel.log_output(
                            f"✓ ARM64 engine test successful: {len(audio_data)} samples")

                    # Update waveform display if available
                    if hasattr(self.main_editor, 'waveform_display'):
                        self.main_editor.waveform_display.show_audio_graph(audio_data)
                else:
                    if hasattr(self.main_editor, 'status_panel'):
                        self.main_editor.status_panel.log_output("✗ ARM64 engine test failed: no audio data")
            else:
                if hasattr(self.main_editor, 'status_panel'):
                    self.main_editor.status_panel.log_output("✗ ARM64 engine test failed: no synthesizer")

        except (RuntimeError, ValueError, OSError) as e:
            if hasattr(self.main_editor, 'logger'):
                self.main_editor.logger.error("ARM64 engine test error: %s", e)
            if hasattr(self.main_editor, 'status_panel'):
                self.main_editor.status_panel.log_output(f"✗ ARM64 engine test error: {e}")

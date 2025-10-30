"""Playback controller component for the audio editor using CustomTkinter."""

import tkinter as tk
import customtkinter as ctk


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
        transport_frame = ctk.CTkFrame(parent_frame, corner_radius=10)
        transport_frame.grid(row=0, column=0, columnspan=2,
                           sticky="ew", padx=5, pady=(0, 10))

        # Title label
        title_label = ctk.CTkLabel(transport_frame, text="Song Controls",
                                  font=ctk.CTkFont(size=16, weight="bold"))
        title_label.pack(pady=(15, 10))

        # Button frame
        button_frame = ctk.CTkFrame(transport_frame, fg_color="transparent")
        button_frame.pack(fill="x", padx=15, pady=(0, 15))

        self.play_button = ctk.CTkButton(button_frame, text="Play",
                                        command=self.toggle_play,
                                        width=80, height=32)
        self.play_button.pack(side="left", padx=(0, 10))

        stop_button = ctk.CTkButton(button_frame, text="Stop",
                                   command=self.stop_playback,
                                   width=80, height=32)
        stop_button.pack(side="left", padx=(0, 20))

        ctk.CTkLabel(button_frame, text="Tempo:").pack(side="left", padx=(0, 5))
        
        self.tempo_var = tk.IntVar(value=125)
        tempo_spinbox = ctk.CTkEntry(button_frame, width=60, justify="center")
        tempo_spinbox.insert(0, "125")
        tempo_spinbox.pack(side="left", padx=(0, 5))
        
        ctk.CTkLabel(button_frame, text="BPM").pack(side="left")

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
                        self.main_editor.status_panel.log_output(
                            "✗ ARM64 engine test failed: no audio data")
            else:
                if hasattr(self.main_editor, 'status_panel'):
                    self.main_editor.status_panel.log_output(
                        "✗ ARM64 engine test failed: no synthesizer")

        except (RuntimeError, ValueError, OSError) as e:
            if hasattr(self.main_editor, 'logger'):
                self.main_editor.logger.error("ARM64 engine test error: %s", e)
            if hasattr(self.main_editor, 'status_panel'):
                self.main_editor.status_panel.log_output(f"✗ ARM64 engine test error: {e}")

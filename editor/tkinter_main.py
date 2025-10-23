#!/usr/bin/env python3
"""
Simple Tkinter-based GUI for 4K Softsynth Editor
Alternative to PySimpleGUI which has compatibility issues
"""

import tkinter as tk
from tkinter import ttk, messagebox
import numpy as np
import sys
import os

# Add the current directory to the Python path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from audio.synth_wrapper import SynthWrapper
from utils.logger import setup_logger

class TkinterEditor:
    """Simple Tkinter-based editor for the synthesizer"""
    
    def __init__(self):
        """Initialize the Tkinter editor"""
        self.logger = setup_logger()
        self.synth = None
        self.root = None
        
        # UI state
        self.playing = False
        self.current_instrument = 0
        
    def initialize_synth(self):
        """Initialize the synthesizer"""
        try:
            self.synth = SynthWrapper()
            return True
        except Exception as e:
            self.logger.error("Synthesizer initialization error: %s", e)
            messagebox.showerror("Error", f"Failed to initialize synthesizer: {e}")
            return False
    
    def create_main_window(self):
        """Create the main application window"""
        self.root = tk.Tk()
        self.root.title("4K Softsynth Editor")
        self.root.geometry("800x600")
        
        # Create menu bar
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
        
        # Create main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(3, weight=1)
        
        # Transport controls
        transport_frame = ttk.LabelFrame(main_frame, text="Transport", padding="5")
        transport_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.play_button = ttk.Button(transport_frame, text="Play", command=self.toggle_play)
        self.play_button.pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(transport_frame, text="Stop", command=self.stop_playback).pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Label(transport_frame, text="Tempo:").pack(side=tk.LEFT, padx=(10, 5))
        self.tempo_var = tk.IntVar(value=125)
        tempo_spinbox = ttk.Spinbox(transport_frame, from_=60, to=200, textvariable=self.tempo_var, width=5)
        tempo_spinbox.pack(side=tk.LEFT)
        ttk.Label(transport_frame, text="BPM").pack(side=tk.LEFT, padx=(5, 0))
        
        # Instrument controls
        instrument_frame = ttk.LabelFrame(main_frame, text="Instrument Controls", padding="5")
        instrument_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        ttk.Label(instrument_frame, text="Instrument:").grid(row=0, column=0, sticky=tk.W)
        self.instrument_var = tk.StringVar(value="Instrument 0")
        instrument_combo = ttk.Combobox(instrument_frame, textvariable=self.instrument_var, 
                                      values=["Instrument 0", "Instrument 1", "Instrument 2", "Instrument 3"])
        instrument_combo.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(5, 0))
        instrument_combo.bind('<<ComboboxSelected>>', self.on_instrument_change)
        
        # ADSR controls
        ttk.Label(instrument_frame, text="ADSR Envelope:").grid(row=1, column=0, columnspan=2, sticky=tk.W, pady=(10, 5))
        
        # Attack
        ttk.Label(instrument_frame, text="Attack:").grid(row=2, column=0, sticky=tk.W)
        self.attack_var = tk.DoubleVar(value=0.1)
        attack_scale = ttk.Scale(instrument_frame, from_=0.0, to=1.0, variable=self.attack_var, orient=tk.HORIZONTAL)
        attack_scale.grid(row=2, column=1, sticky=(tk.W, tk.E), padx=(5, 0))
        attack_scale.bind('<Motion>', self.on_adsr_change)
        
        # Decay
        ttk.Label(instrument_frame, text="Decay:").grid(row=3, column=0, sticky=tk.W)
        self.decay_var = tk.DoubleVar(value=0.2)
        decay_scale = ttk.Scale(instrument_frame, from_=0.0, to=1.0, variable=self.decay_var, orient=tk.HORIZONTAL)
        decay_scale.grid(row=3, column=1, sticky=(tk.W, tk.E), padx=(5, 0))
        decay_scale.bind('<Motion>', self.on_adsr_change)
        
        # Sustain
        ttk.Label(instrument_frame, text="Sustain:").grid(row=4, column=0, sticky=tk.W)
        self.sustain_var = tk.DoubleVar(value=0.7)
        sustain_scale = ttk.Scale(instrument_frame, from_=0.0, to=1.0, variable=self.sustain_var, orient=tk.HORIZONTAL)
        sustain_scale.grid(row=4, column=1, sticky=(tk.W, tk.E), padx=(5, 0))
        sustain_scale.bind('<Motion>', self.on_adsr_change)
        
        # Release
        ttk.Label(instrument_frame, text="Release:").grid(row=5, column=0, sticky=tk.W)
        self.release_var = tk.DoubleVar(value=0.5)
        release_scale = ttk.Scale(instrument_frame, from_=0.0, to=1.0, variable=self.release_var, orient=tk.HORIZONTAL)
        release_scale.grid(row=5, column=1, sticky=(tk.W, tk.E), padx=(5, 0))
        release_scale.bind('<Motion>', self.on_adsr_change)
        
        # Gain
        ttk.Label(instrument_frame, text="Gain:").grid(row=6, column=0, sticky=tk.W)
        self.gain_var = tk.DoubleVar(value=0.8)
        gain_scale = ttk.Scale(instrument_frame, from_=0.0, to=1.0, variable=self.gain_var, orient=tk.HORIZONTAL)
        gain_scale.grid(row=6, column=1, sticky=(tk.W, tk.E), padx=(5, 0))
        gain_scale.bind('<Motion>', self.on_adsr_change)
        
        instrument_frame.columnconfigure(1, weight=1)
        
        # Test controls
        test_frame = ttk.LabelFrame(main_frame, text="Test & Demo", padding="5")
        test_frame.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(10, 0), pady=(0, 10))
        
        ttk.Button(test_frame, text="Test ARM64 Engine", command=self.test_arm64_engine).pack(fill=tk.X, pady=(0, 5))
        ttk.Button(test_frame, text="Play A4 Note", command=self.play_test_note).pack(fill=tk.X, pady=(0, 5))
        ttk.Button(test_frame, text="Generate Sample", command=self.generate_sample).pack(fill=tk.X, pady=(0, 5))
        ttk.Button(test_frame, text="Performance Test", command=self.run_performance_test).pack(fill=tk.X, pady=(0, 5))
        
        # Output text area
        output_frame = ttk.LabelFrame(main_frame, text="Output", padding="5")
        output_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        output_frame.columnconfigure(0, weight=1)
        output_frame.rowconfigure(0, weight=1)
        
        self.output_text = tk.Text(output_frame, height=8, wrap=tk.WORD)
        scrollbar = ttk.Scrollbar(output_frame, orient=tk.VERTICAL, command=self.output_text.yview)
        self.output_text.configure(yscrollcommand=scrollbar.set)
        
        self.output_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E))
        
        # Initial output
        self.log_output("4K Softsynth Editor - Tkinter Version")
        if self.synth.is_ready():
            self.log_output("✓ ARM64 Synthesizer initialized and ready")
        else:
            self.log_output("⚠ Running in simulation mode")
    
    def log_output(self, message):
        """Add a message to the output text area"""
        self.output_text.insert(tk.END, message + "\n")
        self.output_text.see(tk.END)
    
    def on_instrument_change(self, event):
        """Handle instrument selection change"""
        selection = self.instrument_var.get()
        if selection:
            self.current_instrument = int(selection.split()[-1])
            self.log_output(f"Selected {selection}")
            self.update_synth_parameters()
    
    def on_adsr_change(self, event):
        """Handle ADSR parameter changes"""
        self.update_synth_parameters()
    
    def update_synth_parameters(self):
        """Update synthesizer parameters based on UI controls"""
        if self.synth:
            try:
                # Set ADSR parameters
                self.synth.set_adsr(
                    self.current_instrument,
                    self.attack_var.get(),
                    self.decay_var.get(),
                    self.sustain_var.get(),
                    self.release_var.get(),
                    self.gain_var.get()
                )
                self.status_var.set(f"Updated ADSR for instrument {self.current_instrument}")
            except Exception as e:
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
        # TODO: Implement actual continuous playback
    
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
            # Generate 1 second of audio
            num_samples = self.synth.get_sample_rate()
            audio_data = self.synth.render_audio(num_samples)
            
            if audio_data is not None:
                self.log_output(f"✓ Generated {len(audio_data)} samples (stereo)")
                self.log_output(f"  Sample range: {np.min(audio_data):.3f} to {np.max(audio_data):.3f}")
                self.log_output(f"  RMS level: {np.sqrt(np.mean(audio_data**2)):.3f}")
            else:
                self.log_output("✗ Failed to generate audio")
        except Exception as e:
            self.log_output(f"✗ ARM64 test failed: {e}")
    
    def play_test_note(self):
        """Play a test note (A4 = 440Hz)"""
        self.log_output("Playing A4 test note...")
        try:
            # Update parameters first
            self.update_synth_parameters()
            
            # Trigger A4 note (MIDI note 69)
            self.synth.trigger_note(self.current_instrument, 69, 0.8)
            
            # Generate 2 seconds of audio
            num_samples = self.synth.get_sample_rate() * 2
            audio_data = self.synth.render_audio(num_samples)
            
            if audio_data is not None:
                self.log_output(f"✓ Generated test note: {len(audio_data)} samples")
                # TODO: Play the audio through system audio
            else:
                self.log_output("✗ Failed to generate test note")
        except Exception as e:
            self.log_output(f"✗ Test note failed: {e}")
    
    def generate_sample(self):
        """Generate a sample audio file"""
        self.log_output("Generating sample audio file...")
        try:
            # Set up parameters for a chord
            self.update_synth_parameters()
            
            # Trigger a C major chord (C4, E4, G4)
            self.synth.trigger_note(0, 60, 0.7)  # C4
            self.synth.trigger_note(1, 64, 0.7)  # E4  
            self.synth.trigger_note(2, 67, 0.7)  # G4
            
            # Generate 3 seconds of audio
            num_samples = self.synth.get_sample_rate() * 3
            audio_data = self.synth.render_audio(num_samples)
            
            if audio_data is not None:
                # Save first 1000 samples to text file
                output_file = "sample_chord.txt"
                np.savetxt(output_file, audio_data[:1000])
                self.log_output(f"✓ Sample chord saved to {output_file}")
                self.log_output(f"  Generated {len(audio_data)} samples ({len(audio_data)//88200:.1f}s)")
            else:
                self.log_output("✗ Failed to generate sample")
        except Exception as e:
            self.log_output(f"✗ Sample generation failed: {e}")
    
    def run_performance_test(self):
        """Run a performance test"""
        self.log_output("Running performance test...")
        try:
            import time
            
            test_samples = self.synth.get_sample_rate()  # 1 second
            iterations = 10
            
            start_time = time.time()
            
            for i in range(iterations):
                audio_data = self.synth.render_audio(test_samples)
                if audio_data is None:
                    self.log_output(f"✗ Failed at iteration {i+1}")
                    return
            
            end_time = time.time()
            total_time = end_time - start_time
            audio_time = (test_samples * iterations) / self.synth.get_sample_rate()
            
            self.log_output(f"✓ Performance test completed:")
            self.log_output(f"  Render time: {total_time:.3f}s, Audio time: {audio_time:.3f}s")
            self.log_output(f"  Real-time factor: {audio_time/total_time:.2f}x")
            
        except Exception as e:
            self.log_output(f"✗ Performance test failed: {e}")
    
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
        messagebox.showinfo("About", 
                           "4K Softsynth Editor - Tkinter Version\n\n"
                           "ARM64 Assembly Synthesizer Interface\n"
                           "Built with Python and Tkinter")
    
    def run(self):
        """Main application entry point"""
        if not self.initialize_synth():
            return 1
        
        try:
            self.create_main_window()
            self.root.mainloop()
            return 0
        except Exception as e:
            self.logger.error("Application error: %s", e)
            if self.root:
                messagebox.showerror("Error", f"Application error: {e}")
            return 1

def main():
    """Main entry point"""
    app = TkinterEditor()
    return app.run()

if __name__ == "__main__":
    sys.exit(main())
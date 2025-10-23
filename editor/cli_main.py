#!/usr/bin/env python3
"""
Command-line interface for 4K Softsynth Editor
Fallback when GUI is not available
"""

import sys
import os
import numpy as np

# Add the current directory to the Python path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from audio.synth_wrapper import SynthWrapper
from utils.logger import setup_logger

class CLIEditor:
    """Command-line interface for the synthesizer"""
    
    def __init__(self):
        """Initialize the CLI editor"""
        self.logger = setup_logger()
        self.synth = None
        
    def initialize_synth(self):
        """Initialize the synthesizer"""
        try:
            self.synth = SynthWrapper()
            print("✓ Synthesizer initialized successfully")
            return True
        except Exception as e:
            self.logger.error("Synthesizer initialization error: %s", e)
            print(f"✗ Failed to initialize synthesizer: {e}")
            return False
    
    def show_menu(self):
        """Display the main menu"""
        print("\n" + "="*50)
        print("    4K Softsynth Editor - Command Line Interface")
        print("="*50)
        print("1. Test ARM64 Synthesizer")
        print("2. Generate Sample Audio")
        print("3. Show Synthesizer Info")
        print("4. Run Performance Test")
        print("5. Exit")
        print("-"*50)
    
    def test_synthesizer(self):
        """Test the ARM64 synthesizer functions"""
        print("\nTesting ARM64 Synthesizer...")
        
        try:
            # Test basic rendering
            duration = 1.0  # 1 second
            num_samples = int(self.synth.get_sample_rate() * duration)
            
            print(f"Generating {num_samples} samples at {self.synth.get_sample_rate()}Hz...")
            
            # Generate audio using the synthesizer (returns stereo samples)
            audio_data = self.synth.render_audio(num_samples)
            
            if audio_data is not None:
                print(f"✓ Generated audio: {len(audio_data)} samples (stereo)")
                print(f"  Sample range: {np.min(audio_data):.3f} to {np.max(audio_data):.3f}")
                print(f"  RMS level: {np.sqrt(np.mean(audio_data**2)):.3f}")
                print(f"  Synthesizer ready: {self.synth.is_ready()}")
            else:
                print("✗ Failed to generate audio")
                
        except Exception as e:
            print(f"✗ Synthesizer test failed: {e}")
            self.logger.error("Synthesizer test error: %s", e)
    
    def generate_sample_audio(self):
        """Generate a sample audio file"""
        print("\nGenerating sample audio...")
        
        try:
            # Parameters for a simple tone
            duration = 2.0  # 2 seconds
            
            num_samples = int(self.synth.get_sample_rate() * duration)
            
            # Set some synthesizer parameters using ARM64 functions
            print("Setting synthesizer parameters...")
            
            # Set ADSR envelope: attack=0.1, decay=0.2, sustain=0.7, release=0.5, gain=0.8
            self.synth.set_adsr(0, 0.1, 0.2, 0.7, 0.5, 0.8)
            
            # Set oscillator: sine wave, no transpose, no detune, moderate color, gain=0.5
            self.synth.set_oscillator(0, 0, 0.0, 0.0, 0.5, 0.5)
            
            # Trigger a note (A4 = MIDI note 69)
            self.synth.trigger_note(0, 69, 0.8)
            
            # Generate audio
            audio_data = self.synth.render_audio(num_samples)
            
            if audio_data is not None:
                # Save to a simple text file for inspection
                output_file = "sample_output.txt"
                np.savetxt(output_file, audio_data[:100])  # Save first 100 samples
                print(f"✓ Sample saved to {output_file} (first 100 samples)")
                print(f"  Audio length: {len(audio_data)} samples ({duration}s)")
                print(f"  Stereo samples, {len(audio_data)//2} mono samples per channel")
            else:
                print("✗ Failed to generate sample audio")
                
        except Exception as e:
            print(f"✗ Sample generation failed: {e}")
            self.logger.error("Sample generation error: %s", e)
    
    def show_synth_info(self):
        """Show synthesizer information"""
        print("\nSynthesizer Information:")
        print(f"  Status: {'Available' if self.synth else 'Not initialized'}")
        
        if self.synth:
            try:
                print(f"  Sample Rate: {self.synth.get_sample_rate()}Hz")
                print(f"  Buffer Size: {self.synth.get_buffer_size()} samples")
                print(f"  Ready: {self.synth.is_ready()}")
                
                # Show ARM64 constants if available
                constants = self.synth.get_constants()
                if constants:
                    print("  ARM64 Constants:")
                    for key, value in constants.items():
                        print(f"    {key}: {value}")
                else:
                    print("  ARM64 Constants: Not available (simulation mode)")
                    
            except Exception as e:
                print(f"  Error getting info: {e}")
    
    def run_performance_test(self):
        """Run a performance test"""
        print("\nRunning performance test...")
        
        try:
            import time
            
            sample_rate = self.synth.get_sample_rate()
            test_samples = sample_rate  # 1 second of audio
            num_iterations = 10
            
            print(f"Rendering {test_samples} samples x {num_iterations} iterations...")
            
            start_time = time.time()
            
            for i in range(num_iterations):
                audio_data = self.synth.render_audio(test_samples)
                if audio_data is None:
                    print(f"✗ Failed at iteration {i+1}")
                    return
                
                if (i + 1) % 5 == 0:
                    print(f"  Completed {i+1}/{num_iterations} iterations")
            
            end_time = time.time()
            total_time = end_time - start_time
            total_audio_time = (test_samples * num_iterations) / sample_rate
            
            print("✓ Performance test completed:")
            print(f"  Total render time: {total_time:.3f} seconds")
            print(f"  Total audio time: {total_audio_time:.3f} seconds")
            print(f"  Real-time factor: {total_audio_time/total_time:.2f}x")
            
        except Exception as e:
            print(f"✗ Performance test failed: {e}")
            self.logger.error("Performance test error: %s", e)
    
    def run(self):
        """Main CLI loop"""
        print("Starting 4K Softsynth Editor CLI...")
        
        if not self.initialize_synth():
            print("Cannot continue without synthesizer. Exiting.")
            return 1
        
        while True:
            self.show_menu()
            
            try:
                choice = input("Enter your choice (1-5): ").strip()
                
                if choice == '1':
                    self.test_synthesizer()
                elif choice == '2':
                    self.generate_sample_audio()
                elif choice == '3':
                    self.show_synth_info()
                elif choice == '4':
                    self.run_performance_test()
                elif choice == '5':
                    print("Goodbye!")
                    break
                else:
                    print("Invalid choice. Please enter 1-5.")
                    
            except KeyboardInterrupt:
                print("\nInterrupted by user. Goodbye!")
                break
            except EOFError:
                print("\nEOF received. Goodbye!")
                break
            except Exception as e:
                print(f"Unexpected error: {e}")
                self.logger.error("CLI error: %s", e)
        
        return 0

def main():
    """Main entry point for CLI"""
    cli = CLIEditor()
    return cli.run()

if __name__ == "__main__":
    sys.exit(main())
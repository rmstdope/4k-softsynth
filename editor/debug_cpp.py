#!/usr/bin/env python3
"""
Debugging helper for C++ extension in Python
This script helps set up proper C++ debugging by:
1. Starting the Python process
2. Loading the C++ extension  
3. Providing the PID for debugger attachment
4. Waiting for debugger attachment before proceeding
"""

import os
import sys
import time
import signal

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def debug_main():
    """Main debugging function"""
    print("🔧 C++ Extension Debug Helper")
    print("="*50)
    
    # Show process ID for debugger attachment
    pid = os.getpid()
    print(f"🔍 Python Process ID: {pid}")
    print(f"   Use this PID to attach C++ debugger in VS Code")
    print(f"   Or run: lldb -p {pid}")
    
    # Import required modules
    print("\n📦 Loading modules...")
    try:
        from audio.synth_wrapper import SynthWrapper
        print("✅ SynthWrapper loaded")
        
        # This is where the C++ extension gets loaded
        print("\n🔧 Initializing synthesizer (loads C++ extension)...")
        synth = SynthWrapper()
        print("✅ C++ extension loaded and initialized")
        
    except Exception as e:
        print(f"❌ Error loading extension: {e}")
        return 1
    
    # Wait for debugger attachment
    print(f"\n🔗 Ready for debugger attachment!")
    print(f"   1. In VS Code, run 'Attach C++ by PID' debug configuration")
    print(f"   2. Enter PID: {pid}")
    print(f"   3. Set breakpoints in C++ code (cpp/synth_bindings.cpp)")
    print(f"   4. Press ENTER here to continue...")
    
    try:
        input("Press ENTER to continue (or Ctrl+C to exit)...")
    except KeyboardInterrupt:
        print("\n👋 Exiting...")
        return 0
    
    print("\n🎵 Testing C++ functions (should hit breakpoints)...")
    
    # Test functions that should trigger C++ breakpoints
    try:
        print("   - Testing render_note()...")
        audio_data = synth.render_note()
        print(f"     Got {len(audio_data)} samples")
        
        print("   - Testing render_instrument_note()...")  
        audio_data = synth.render_instrument_note(0, 64)
        print(f"     Got {len(audio_data)} samples")
        
        print("   - Testing constants...")
        constants = synth.get_constants()
        print(f"     Got {len(constants)} constants")
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        return 1
    
    print("\n✅ Debug session completed!")
    print("   If breakpoints didn't hit, check:")
    print("   - Extension was built with debug symbols (DEBUG_BUILD=1)")
    print("   - Breakpoints are set in the correct source files")
    print("   - Debugger attached to the correct process")
    
    return 0

if __name__ == "__main__":
    sys.exit(debug_main())
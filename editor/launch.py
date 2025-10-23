#!/usr/bin/env python3
"""
Smart launcher for 4K Softsynth Editor
Automatically chooses the best available GUI interface
"""

import sys
import subprocess

def test_gui_availability():
    """Test which GUI frameworks are available"""
    available_guis = []
    
    # Test tkinter (most reliable)
    try:
        import tkinter
        available_guis.append(('tkinter', 'Tkinter GUI (Native)', 'tkinter_main.py'))
    except ImportError:
        pass
    
    # CLI is always available
    available_guis.append(('cli', 'Command Line Interface', 'cli_main.py'))
    
    return available_guis

def main():
    """Main launcher entry point"""
    print("4K Softsynth Editor Launcher")
    print("=" * 40)
    
    available_guis = test_gui_availability()
    
    if len(available_guis) == 0:
        print("ERROR: No GUI interfaces available!")
        return 1
    
    # If we have arguments, try to honor them
    if len(sys.argv) > 1:
        interface = sys.argv[1].lower()
        
        if interface in ['cli', 'command', 'terminal']:
            script = 'cli_main.py'
        elif interface in ['tk', 'tkinter', 'gui']:
            script = 'tkinter_main.py'
        else:
            print(f"Unknown interface: {interface}")
            print("Available: cli, tkinter")
            return 1
        
        print(f"Launching {interface} interface...")
        return subprocess.call([sys.executable, script])
    
    # Auto-select best available GUI
    print("Available interfaces:")
    for i, (gui_id, gui_name, gui_script) in enumerate(available_guis):
        print(f"  {i+1}. {gui_name}")
    
    # Default preference: tkinter > cli
    preferred_order = ['tkinter', 'cli']
    
    selected_gui = None
    for preferred in preferred_order:
        for gui_id, gui_name, gui_script in available_guis:
            if gui_id == preferred:
                selected_gui = (gui_id, gui_name, gui_script)
                break
        if selected_gui:
            break
    
    if not selected_gui:
        selected_gui = available_guis[0]  # Fallback to first available
    
    gui_id, gui_name, gui_script = selected_gui
    print(f"\nAuto-selecting: {gui_name}")
    print(f"Launching {gui_script}...")
    print()
    
    try:
        return subprocess.call([sys.executable, gui_script])
    except KeyboardInterrupt:
        print("\nLauncher interrupted by user")
        return 0
    except Exception as e:
        print(f"Launch failed: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
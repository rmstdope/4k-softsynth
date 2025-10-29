#!/usr/bin/env python3
"""
Test the updated GUI with instrument parameter controls
"""

import sys
import os

# Add the current directory to the Python path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_gui_components():
    """Test the GUI components without starting the main loop"""
    print("🧪 Testing GUI components...")
    
    try:
        # Import all required modules
        import tkinter as tk
        from tkinter import ttk
        print("✅ Tkinter imports successful")
        
        # Import synth_engine
        import synth_engine
        print("✅ synth_engine import successful")
        
        # Test ParameterControl class import by importing the module
        import importlib.util
        spec = importlib.util.spec_from_file_location("main_module", "__main__.py")
        main_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(main_module)
        ParameterControl = main_module.ParameterControl
        print("✅ ParameterControl class import successful")
        
        # Create a test window
        root = tk.Tk()
        root.title("GUI Component Test")
        root.geometry("800x600")
        
        # Test synth engine initialization
        engine = synth_engine.SynthEngine()
        engine.initialize()
        print("✅ SynthEngine initialized")
        
        # Create a test frame
        main_frame = ttk.Frame(root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create a scrollable frame (simplified version)
        canvas = tk.Canvas(main_frame, height=300)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        scrollable_frame.columnconfigure(1, weight=1)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        print("✅ Scrollable frame created")
        
        # Test creating parameter controls for instrument 0
        instrument = engine.get_instrument(0)
        if instrument:
            instructions = instrument.get_instructions()
            row = 0
            controls = {}
            
            for instr_idx, instr_id in enumerate(instructions):
                instr_name = instrument.get_instruction_name(instr_idx)
                param_names = instrument.get_instruction_parameter_names(instr_idx)
                param_values = instrument.get_instruction_parameters(instr_idx)
                
                if param_names:
                    # Add section header
                    header_label = ttk.Label(scrollable_frame, 
                                           text=f"🎛️ {instr_name}", 
                                           font=('TkDefaultFont', 9, 'bold'))
                    header_label.grid(row=row, column=0, columnspan=3, sticky=tk.W, pady=(10, 5))
                    row += 1
                    
                    # Create parameter controls
                    for param_idx, (param_name, param_value) in enumerate(zip(param_names, param_values)):
                        normalized_value = param_value / 255.0
                        
                        control = ParameterControl(
                            parent=scrollable_frame,
                            name=param_name,
                            initial_value=normalized_value,
                            row=row,
                            update_callback=lambda: print(f"Parameter changed: {param_name}")
                        )
                        
                        control_id = f"instr_{instr_idx}_param_{param_idx}"
                        controls[control_id] = control
                        row += 1
            
            print(f"✅ Created {len(controls)} parameter controls")
            
            # Add a close button
            ttk.Button(main_frame, text="Close Test", 
                      command=root.destroy).pack(pady=10)
            
            # Update the canvas scroll region
            scrollable_frame.update_idletasks()
            canvas.configure(scrollregion=canvas.bbox("all"))
            
            print("🎉 GUI test successful!")
            print(f"📊 Total controls created: {len(controls)}")
            print("💡 You can run the full GUI now with: python __main__.py")
            
            # Don't start the mainloop in test mode
            root.destroy()
            
        else:
            print("❌ Could not get instrument 0")
            root.destroy()
            
    except Exception as e:
        print(f"❌ Error during GUI test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_gui_components()
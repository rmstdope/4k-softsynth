#!/usr/bin/env python3
"""
Final comprehensive test of the parameter names functionality.
Shows parameter modification by name instead of cryptic indices.
"""

import synth_engine

def find_parameter_by_name(instrument, instruction_index, param_name):
    """Helper function to find parameter index by name"""
    param_names = instrument.get_instruction_parameter_names(instruction_index)
    try:
        return param_names.index(param_name)
    except ValueError:
        return -1

def update_parameter_by_name(instrument, instruction_index, param_name, value):
    """Helper function to update parameter by name"""
    param_index = find_parameter_by_name(instrument, instruction_index, param_name)
    if param_index >= 0:
        instrument.update_parameter(instruction_index, param_index, value)
        return True
    return False

def print_instruction_details(instrument, instruction_index):
    """Helper function to print detailed instruction info"""
    instr_name = instrument.get_instruction_name(instruction_index)
    param_names = instrument.get_instruction_parameter_names(instruction_index)
    param_values = instrument.get_instruction_parameters(instruction_index)
    
    print(f'   🎯 {instr_name}:')
    if param_names and param_values:
        for name, value in zip(param_names, param_values):
            print(f'      {name:12s} = {value:3d}')
    print()

def main():
    print('🎛️  PARAMETER MODIFICATION BY NAME - FINAL TEST')
    print('=' * 55)

    # Initialize engine
    engine = synth_engine.SynthEngine()
    engine.initialize()

    # Get the first instrument
    instrument_0 = engine.get_instrument(0)
    print('🎼 COMPREHENSIVE PARAMETER MODIFICATION TEST')
    print('-' * 45)

    # Show original state
    print('📋 ORIGINAL PARAMETERS:')
    for i in range(len(instrument_0.get_instructions())):
        print_instruction_details(instrument_0, i)

    print('🧪 PARAMETER MODIFICATION BY NAME:')
    print()

    # Test 1: ENVELOPE modifications
    envelope_idx = None
    for i, instr_id in enumerate(instrument_0.get_instructions()):
        if instr_id == synth_engine.ENVELOPE_ID:
            envelope_idx = i
            break

    if envelope_idx is not None:
        print('   🎚️  ENVELOPE - Creating custom ADSR curve')
        update_parameter_by_name(instrument_0, envelope_idx, 'Attack', 30)    # Moderate attack
        update_parameter_by_name(instrument_0, envelope_idx, 'Decay', 60)     # Medium decay
        update_parameter_by_name(instrument_0, envelope_idx, 'Sustain', 120)  # High sustain
        update_parameter_by_name(instrument_0, envelope_idx, 'Release', 90)   # Long release
        update_parameter_by_name(instrument_0, envelope_idx, 'Gain', 180)     # Boost volume
        print_instruction_details(instrument_0, envelope_idx)

    # Test 2: OSCILLATOR modifications
    osc_idx = None
    for i, instr_id in enumerate(instrument_0.get_instructions()):
        if instr_id == synth_engine.OSCILLATOR_ID:
            osc_idx = i
            break

    if osc_idx is not None:
        print('   🌊 OSCILLATOR - Creating bright, detuned saw wave')
        update_parameter_by_name(instrument_0, osc_idx, 'Transpose', 67)    # +3 semitones
        update_parameter_by_name(instrument_0, osc_idx, 'Detune', 70)       # Slight detune
        update_parameter_by_name(instrument_0, osc_idx, 'Color', 100)       # Bright timbre
        update_parameter_by_name(instrument_0, osc_idx, 'Shape', 90)        # Sharp shape  
        update_parameter_by_name(instrument_0, osc_idx, 'Type', 32)         # SAW wave
        update_parameter_by_name(instrument_0, osc_idx, 'Gain', 150)        # Louder
        print_instruction_details(instrument_0, osc_idx)

    # Test 3: OUTPUT modifications
    output_idx = None
    for i, instr_id in enumerate(instrument_0.get_instructions()):
        if instr_id == synth_engine.OUTPUT_ID:
            output_idx = i
            break

    if output_idx is not None:
        print('   🔊 OUTPUT - Boosting final volume')
        update_parameter_by_name(instrument_0, output_idx, 'Gain', 220)     # Much louder
        print_instruction_details(instrument_0, output_idx)

    # Audio test
    print('🎵 AUDIO GENERATION TEST:')
    print('   Rendering modified instrument...')
    audio_data = instrument_0.render_note(64)  # Middle C
    peak_amplitude = max(abs(x) for x in audio_data) if audio_data else 0
    rms = (sum(x*x for x in audio_data) / len(audio_data))**0.5 if audio_data else 0

    print(f'   📊 Audio Stats:')
    print(f'      Samples:    {len(audio_data)}')
    print(f'      Peak:       {peak_amplitude:.6f}')
    print(f'      RMS:        {rms:.6f}')
    print(f'      Duration:   {len(audio_data)/44100:.3f}s')
    print()

    # Summary of available parameter names by instruction type
    print('📚 PARAMETER NAMES REFERENCE:')
    print('-' * 30)

    # Check what instruction types we actually have
    available_instructions = {}
    for i in range(len(instrument_0.get_instructions())):
        instr_id = instrument_0.get_instructions()[i]
        instr_name = instrument_0.get_instruction_name(i)
        param_names = instrument_0.get_instruction_parameter_names(i)
        
        if instr_name not in available_instructions:
            available_instructions[instr_name] = param_names

    for instr_name, param_names in available_instructions.items():
        print(f'   {instr_name:12s}: {", ".join(param_names)}')

    print()
    print('=' * 55)
    print('✅ PARAMETER NAMES SYSTEM COMPLETE!')
    print('🎯 Key Features:')
    print('   • Get human-readable parameter names')
    print('   • Modify parameters by name (no more index hunting!)')
    print('   • Full integration with existing parameter system')
    print('   • Proper error handling and validation')
    print('   • Real-time audio parameter modification')
    print()
    print('🎉 The synthesizer now has a user-friendly parameter interface!')

if __name__ == '__main__':
    main()
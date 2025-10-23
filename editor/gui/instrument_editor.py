"""
Instrument Editor Window for editing synthesizer parameters
"""

import PySimpleGUI as sg

class InstrumentEditor:
    """Window for editing instrument parameters like ADSR, oscillator settings, etc."""
    
    def __init__(self):
        """Initialize the instrument editor"""
        self.window = None
        self.current_instrument = None
        
    def create_layout(self):
        """Create the instrument editor layout"""
        
        # ADSR Envelope section
        adsr_frame = [
            [sg.Text('Attack:'), sg.Slider(range=(0, 127), default_value=10, orientation='h', 
                                         key='-ATTACK-', size=(20, 20))],
            [sg.Text('Decay:'), sg.Slider(range=(0, 127), default_value=20, orientation='h', 
                                        key='-DECAY-', size=(20, 20))],
            [sg.Text('Sustain:'), sg.Slider(range=(0, 127), default_value=80, orientation='h', 
                                           key='-SUSTAIN-', size=(20, 20))],
            [sg.Text('Release:'), sg.Slider(range=(0, 127), default_value=30, orientation='h', 
                                          key='-RELEASE-', size=(20, 20))]
        ]
        
        # Oscillator section
        osc_frame = [
            [sg.Text('Waveform:'), sg.Combo(['Sine', 'Sawtooth', 'Square', 'Triangle', 'Noise'], 
                                           default_value='Sine', key='-WAVEFORM-', readonly=True)],
            [sg.Text('Transpose:'), sg.Slider(range=(-24, 24), default_value=0, orientation='h', 
                                            key='-TRANSPOSE-', size=(20, 20))],
            [sg.Text('Detune:'), sg.Slider(range=(-100, 100), default_value=0, orientation='h', 
                                          key='-DETUNE-', size=(20, 20))],
            [sg.Text('Gain:'), sg.Slider(range=(0, 127), default_value=100, orientation='h', 
                                        key='-GAIN-', size=(20, 20))]
        ]
        
        # Filter section
        filter_frame = [
            [sg.Text('Type:'), sg.Combo(['Lowpass', 'Highpass', 'Bandpass', 'Notch'], 
                                       default_value='Lowpass', key='-FILTER_TYPE-', readonly=True)],
            [sg.Text('Frequency:'), sg.Slider(range=(20, 20000), default_value=1000, orientation='h', 
                                             key='-FILTER_FREQ-', size=(20, 20))],
            [sg.Text('Resonance:'), sg.Slider(range=(0, 100), default_value=10, orientation='h', 
                                             key='-FILTER_RES-', size=(20, 20))]
        ]
        
        # Effects section
        effects_frame = [
            [sg.Checkbox('Reverb', key='-REVERB-'), 
             sg.Slider(range=(0, 100), default_value=20, orientation='h', key='-REVERB_AMOUNT-', size=(15, 20))],
            [sg.Checkbox('Delay', key='-DELAY-'), 
             sg.Slider(range=(0, 100), default_value=15, orientation='h', key='-DELAY_AMOUNT-', size=(15, 20))],
            [sg.Checkbox('Distortion', key='-DISTORTION-'), 
             sg.Slider(range=(0, 100), default_value=0, orientation='h', key='-DISTORTION_AMOUNT-', size=(15, 20))]
        ]
        
        # Main layout
        layout = [
            [sg.Text('Instrument Editor', font=('Arial', 16, 'bold'))],
            [sg.Text('Instrument:'), sg.Combo(['Instrument 1', 'Instrument 2', 'Instrument 3', 'Instrument 4'], 
                                             default_value='Instrument 1', key='-INSTRUMENT_SELECT-', 
                                             readonly=True, enable_events=True)],
            [sg.HSeparator()],
            [sg.Frame('ADSR Envelope', adsr_frame, title_color='cyan')],
            [sg.Frame('Oscillator', osc_frame, title_color='cyan')],
            [sg.Frame('Filter', filter_frame, title_color='cyan')],
            [sg.Frame('Effects', effects_frame, title_color='cyan')],
            [sg.HSeparator()],
            [sg.Button('Load Preset'), sg.Button('Save Preset'), sg.Button('Reset'), 
             sg.Button('Apply'), sg.Button('Close')]
        ]
        
        return layout
    
    def load_instrument_parameters(self, instrument_name):
        """Load parameters for the specified instrument
        
        Args:
            instrument_name: Name of the instrument to load
        """
        # TODO: Load actual instrument parameters from the synthesizer
        # For now, just update the UI with default values
        self.current_instrument = instrument_name
        
        if self.window:
            # Update sliders with instrument-specific values
            # This would normally load from the actual synth data
            self.window['-ATTACK-'].update(value=10)
            self.window['-DECAY-'].update(value=20)
            self.window['-SUSTAIN-'].update(value=80)
            self.window['-RELEASE-'].update(value=30)
    
    def save_instrument_parameters(self):
        """Save current parameters to the synthesizer"""
        if not self.window:
            return
            
        # Get current values
        values = {
            'attack': self.window['-ATTACK-'].get(),
            'decay': self.window['-DECAY-'].get(),
            'sustain': self.window['-SUSTAIN-'].get(),
            'release': self.window['-RELEASE-'].get(),
            'waveform': self.window['-WAVEFORM-'].get(),
            'transpose': self.window['-TRANSPOSE-'].get(),
            'detune': self.window['-DETUNE-'].get(),
            'gain': self.window['-GAIN-'].get(),
            'filter_type': self.window['-FILTER_TYPE-'].get(),
            'filter_freq': self.window['-FILTER_FREQ-'].get(),
            'filter_res': self.window['-FILTER_RES-'].get(),
        }
        
        # TODO: Send these values to the actual synthesizer
        sg.popup(f'Saved parameters for {self.current_instrument}', title='Saved')
    
    def reset_parameters(self):
        """Reset all parameters to defaults"""
        if not self.window:
            return
            
        # Reset all sliders to default values
        self.window['-ATTACK-'].update(value=10)
        self.window['-DECAY-'].update(value=20)
        self.window['-SUSTAIN-'].update(value=80)
        self.window['-RELEASE-'].update(value=30)
        self.window['-TRANSPOSE-'].update(value=0)
        self.window['-DETUNE-'].update(value=0)
        self.window['-GAIN-'].update(value=100)
        self.window['-FILTER_FREQ-'].update(value=1000)
        self.window['-FILTER_RES-'].update(value=10)
        
        # Reset checkboxes
        self.window['-REVERB-'].update(value=False)
        self.window['-DELAY-'].update(value=False)
        self.window['-DISTORTION-'].update(value=False)
    
    def show(self):
        """Show the instrument editor window"""
        if self.window and not self.window.was_closed():
            self.window.bring_to_front()
            return
            
        layout = self.create_layout()
        self.window = sg.Window('Instrument Editor', layout, resizable=True, finalize=True)
        
        while True:
            event, values = self.window.read()
            
            if event == sg.WIN_CLOSED or event == 'Close':
                break
            elif event == '-INSTRUMENT_SELECT-':
                self.load_instrument_parameters(values['-INSTRUMENT_SELECT-'])
            elif event == 'Load Preset':
                # TODO: Implement preset loading
                sg.popup('Preset loading not yet implemented')
            elif event == 'Save Preset':
                # TODO: Implement preset saving
                sg.popup('Preset saving not yet implemented')
            elif event == 'Reset':
                self.reset_parameters()
            elif event == 'Apply':
                self.save_instrument_parameters()
        
        self.window.close()
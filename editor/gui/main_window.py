"""
Main Window for 4K Softsynth Editor
Handles the primary GUI interface with PySimpleGUI
"""

import PySimpleGUI as sg
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import io

from .plot_window import PlotWindow
from .instrument_editor import InstrumentEditor

class MainWindow:
    """Main application window using PySimpleGUI"""
    
    def __init__(self, synth_wrapper):
        """Initialize the main window
        
        Args:
            synth_wrapper: Instance of SynthWrapper for audio processing
        """
        self.synth = synth_wrapper
        self.window = None
        self.plot_window = None
        self.instrument_editor = None
        
        # Set PySimpleGUI theme
        try:
            sg.theme('DarkBlue3')
        except AttributeError:
            # Fallback for older PySimpleGUI versions
            try:
                sg.SetOptions(background_color='#64778d')
            except:
                pass  # Use default theme
        
    def create_layout(self):
        """Create the main window layout"""
        # Menu bar
        menu_def = [
            ['&File', ['&New', '&Open', '&Save', '&Save As', 'E&xit']],
            ['&Edit', ['&Preferences']],
            ['&View', ['&Waveform', '&Spectrum', '&Instrument Editor']],
            ['&Help', ['&About']]
        ]
        
        # Toolbar
        toolbar = [
            [sg.Button('Play', key='-PLAY-', size=(8, 1)),
             sg.Button('Stop', key='-STOP-', size=(8, 1)),
             sg.Button('Record', key='-RECORD-', size=(8, 1)),
             sg.VSeparator(),
             sg.Text('Tempo:'), sg.Spin([i for i in range(60, 200)], initial_value=120, key='-TEMPO-', size=(5, 1)),
             sg.Text('BPM')]
        ]
        
        # Main content area
        left_column = [
            [sg.Text('Instruments', font=('Arial', 12, 'bold'))],
            [sg.Listbox(['Instrument 1', 'Instrument 2', 'Instrument 3', 'Instrument 4'], 
                       size=(20, 8), key='-INSTRUMENT_LIST-', enable_events=True)],
            [sg.Button('Add', size=(8, 1)), sg.Button('Delete', size=(8, 1))],
            [sg.HSeparator()],
            [sg.Text('Pattern Editor', font=('Arial', 12, 'bold'))],
            [sg.Multiline('', size=(25, 10), key='-PATTERN-')]
        ]
        
        right_column = [
            [sg.Text('Waveform Display', font=('Arial', 12, 'bold'))],
            [sg.Canvas(size=(600, 200), key='-CANVAS-', background_color='black')],
            [sg.HSeparator()],
            [sg.Text('Controls', font=('Arial', 12, 'bold'))],
            [sg.Text('Volume:'), sg.Slider(range=(0, 100), default_value=50, orientation='h', key='-VOLUME-')],
            [sg.Text('Filter Freq:'), sg.Slider(range=(20, 20000), default_value=1000, orientation='h', key='-FILTER-')],
            [sg.Text('Resonance:'), sg.Slider(range=(0, 100), default_value=10, orientation='h', key='-RESONANCE-')]
        ]
        
        # Status bar
        status_bar = [
            [sg.StatusBar('Ready', size=(80, 1), key='-STATUS-')]
        ]
        
        # Combine all elements
        layout = [
            [sg.Menu(menu_def)],
            toolbar,
            [sg.HSeparator()],
            [sg.Column(left_column), sg.VSeparator(), sg.Column(right_column)],
            [sg.HSeparator()],
            status_bar
        ]
        
        return layout
    
    def create_sample_plot(self):
        """Create a sample waveform plot"""
        fig, ax = plt.subplots(figsize=(8, 3))
        
        # Generate sample waveform data
        t = np.linspace(0, 1, 1000)
        y = np.sin(2 * np.pi * 440 * t) * np.exp(-t * 2)  # Decaying sine wave
        
        ax.plot(t, y, 'cyan', linewidth=1.5)
        ax.set_xlabel('Time (s)')
        ax.set_ylabel('Amplitude')
        ax.set_title('Sample Waveform')
        ax.grid(True, alpha=0.3)
        ax.set_facecolor('black')
        fig.patch.set_facecolor('black')
        
        return fig
    
    def draw_figure(self, canvas, figure):
        """Draw matplotlib figure on PySimpleGUI canvas"""
        figure_canvas_agg = FigureCanvasTkAgg(figure, canvas)
        figure_canvas_agg.draw()
        figure_canvas_agg.get_tk_widget().pack(side='top', fill='both', expand=1)
        return figure_canvas_agg
    
    def run(self):
        """Main event loop"""
        layout = self.create_layout()
        self.window = sg.Window('4K Softsynth Editor', layout, 
                               resizable=True, finalize=True, size=(1000, 600))
        
        # Draw initial plot
        fig = self.create_sample_plot()
        canvas_elem = self.window['-CANVAS-']
        canvas = canvas_elem.TKCanvas
        fig_agg = self.draw_figure(canvas, fig)
        
        while True:
            event, values = self.window.read()
            
            if event == sg.WIN_CLOSED or event == 'Exit':
                break
                
            elif event == '-PLAY-':
                self.handle_play()
                
            elif event == '-STOP-':
                self.handle_stop()
                
            elif event == '-RECORD-':
                self.handle_record()
                
            elif event == '-INSTRUMENT_LIST-':
                self.handle_instrument_select(values['-INSTRUMENT_LIST-'])
                
            elif event == 'Waveform':
                self.show_waveform_window()
                
            elif event == 'Spectrum':
                self.show_spectrum_window()
                
            elif event == 'Instrument Editor':
                self.show_instrument_editor()
                
            elif event == 'About':
                self.show_about_dialog()
        
        self.window.close()
    
    def handle_play(self):
        """Handle play button click"""
        self.window['-STATUS-'].update('Playing...')
        # TODO: Implement audio playback
        
    def handle_stop(self):
        """Handle stop button click"""
        self.window['-STATUS-'].update('Stopped')
        # TODO: Implement audio stop
        
    def handle_record(self):
        """Handle record button click"""
        self.window['-STATUS-'].update('Recording...')
        # TODO: Implement audio recording
        
    def handle_instrument_select(self, selection):
        """Handle instrument selection"""
        if selection:
            instrument = selection[0]
            self.window['-STATUS-'].update(f'Selected: {instrument}')
            # TODO: Load instrument parameters
    
    def show_waveform_window(self):
        """Show waveform analysis window"""
        if not self.plot_window:
            self.plot_window = PlotWindow('Waveform Analysis')
        self.plot_window.show()
    
    def show_spectrum_window(self):
        """Show spectrum analysis window"""
        if not self.plot_window:
            self.plot_window = PlotWindow('Spectrum Analysis')
        self.plot_window.show()
    
    def show_instrument_editor(self):
        """Show instrument editor window"""
        if not self.instrument_editor:
            self.instrument_editor = InstrumentEditor()
        self.instrument_editor.show()
    
    def show_about_dialog(self):
        """Show about dialog"""
        sg.popup('4K Softsynth Editor\n\nVersion 1.0\nBuilt with PySimpleGUI',
                title='About', keep_on_top=True)
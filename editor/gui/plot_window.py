"""
Plot Window for displaying waveforms and spectrum analysis
"""

import PySimpleGUI as sg
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np

class PlotWindow:
    """Separate window for plotting waveforms and spectrum data"""
    
    def __init__(self, title="Plot Window"):
        """Initialize the plot window
        
        Args:
            title: Window title
        """
        self.title = title
        self.window = None
        self.figure = None
        
    def create_layout(self):
        """Create the plot window layout"""
        layout = [
            [sg.Text(self.title, font=('Arial', 14, 'bold'))],
            [sg.Canvas(size=(800, 400), key='-PLOT_CANVAS-')],
            [sg.HSeparator()],
            [sg.Button('Generate Sine', key='-SINE-'),
             sg.Button('Generate Sawtooth', key='-SAW-'),
             sg.Button('Generate Square', key='-SQUARE-'),
             sg.Button('Generate Noise', key='-NOISE-')],
            [sg.Text('Frequency:'), sg.Slider(range=(20, 2000), default_value=440, 
                                            orientation='h', key='-FREQ-', size=(30, 20))],
            [sg.Button('Close', key='-CLOSE-')]
        ]
        return layout
    
    def generate_waveform(self, waveform_type, frequency=440):
        """Generate different types of waveforms
        
        Args:
            waveform_type: Type of waveform ('sine', 'sawtooth', 'square', 'noise')
            frequency: Frequency in Hz
        """
        t = np.linspace(0, 0.01, 1000)  # 10ms of audio
        
        if waveform_type == 'sine':
            y = np.sin(2 * np.pi * frequency * t)
            title = f'Sine Wave - {frequency} Hz'
        elif waveform_type == 'sawtooth':
            y = 2 * (t * frequency - np.floor(t * frequency + 0.5))
            title = f'Sawtooth Wave - {frequency} Hz'
        elif waveform_type == 'square':
            y = np.sign(np.sin(2 * np.pi * frequency * t))
            title = f'Square Wave - {frequency} Hz'
        elif waveform_type == 'noise':
            y = np.random.normal(0, 0.3, len(t))
            title = 'White Noise'
        else:
            y = np.zeros_like(t)
            title = 'Silence'
        
        return t, y, title
    
    def create_plot(self, waveform_type='sine', frequency=440):
        """Create matplotlib plot"""
        if self.figure:
            plt.close(self.figure)
            
        self.figure, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 6))
        
        # Generate waveform
        t, y, title = self.generate_waveform(waveform_type, frequency)
        
        # Time domain plot
        ax1.plot(t * 1000, y, 'cyan', linewidth=1.5)
        ax1.set_xlabel('Time (ms)')
        ax1.set_ylabel('Amplitude')
        ax1.set_title(title)
        ax1.grid(True, alpha=0.3)
        ax1.set_facecolor('black')
        
        # Frequency domain plot (FFT)
        fft = np.fft.fft(y)
        freqs = np.fft.fftfreq(len(y), t[1] - t[0])
        magnitude = np.abs(fft)
        
        # Plot only positive frequencies
        positive_freqs = freqs[:len(freqs)//2]
        positive_magnitude = magnitude[:len(magnitude)//2]
        
        ax2.semilogy(positive_freqs, positive_magnitude, 'orange', linewidth=1.5)
        ax2.set_xlabel('Frequency (Hz)')
        ax2.set_ylabel('Magnitude')
        ax2.set_title('Frequency Spectrum')
        ax2.grid(True, alpha=0.3)
        ax2.set_facecolor('black')
        ax2.set_xlim(0, 5000)  # Show up to 5kHz
        
        self.figure.patch.set_facecolor('black')
        plt.tight_layout()
        
        return self.figure
    
    def draw_figure(self, canvas, figure):
        """Draw matplotlib figure on canvas"""
        figure_canvas_agg = FigureCanvasTkAgg(figure, canvas)
        figure_canvas_agg.draw()
        figure_canvas_agg.get_tk_widget().pack(side='top', fill='both', expand=1)
        return figure_canvas_agg
    
    def show(self):
        """Show the plot window"""
        if self.window and not self.window.was_closed():
            self.window.bring_to_front()
            return
            
        layout = self.create_layout()
        self.window = sg.Window(self.title, layout, resizable=True, finalize=True)
        
        # Create initial plot
        fig = self.create_plot()
        canvas_elem = self.window['-PLOT_CANVAS-']
        canvas = canvas_elem.TKCanvas
        fig_agg = self.draw_figure(canvas, fig)
        
        while True:
            event, values = self.window.read()
            
            if event == sg.WIN_CLOSED or event == '-CLOSE-':
                break
            elif event in ['-SINE-', '-SAW-', '-SQUARE-', '-NOISE-']:
                # Clear previous plot
                if fig_agg:
                    fig_agg.get_tk_widget().destroy()
                
                # Generate new plot
                waveform_type = event.strip('-').lower()
                frequency = values['-FREQ-']
                fig = self.create_plot(waveform_type, frequency)
                fig_agg = self.draw_figure(canvas, fig)
        
        self.window.close()
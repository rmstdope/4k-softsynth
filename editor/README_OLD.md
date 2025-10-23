# 4K Softsynth Editor

A Python-based editor for the 4K ARM64 softsynth with multiple GUI interfaces and direct ARM64 assembly integration.

## Features

- **Graphical User Interface**: Built with PySimpleGUI for cross-platform compatibility
- **Real-time Waveform Display**: Visualize audio waveforms using matplotlib
- **Spectrum Analysis**: View frequency domain representations of audio
- **Instrument Editor**: Edit synthesizer parameters (ADSR, oscillators, filters, effects)
- **Pattern Editor**: Create and edit musical patterns
- **C++ Integration**: Native C++ synthesizer engine with Python bindings
- **Audio Playback**: Real-time audio rendering and playback

## Project Structure

```
editor/
├── main.py                 # Main application entry point
├── requirements.txt        # Python dependencies
├── setup.py               # C++ extension build configuration
├── build.sh               # Build script
├── README.md              # This file
├── gui/                   # GUI modules
│   ├── __init__.py
│   ├── main_window.py     # Main application window
│   ├── plot_window.py     # Waveform/spectrum display
│   └── instrument_editor.py # Instrument parameter editor
├── audio/                 # Audio processing modules
│   ├── __init__.py
│   └── synth_wrapper.py   # Python wrapper for C++ synth
├── cpp/                   # C++ extension source
│   ├── __init__.py
│   └── synth_bindings.cpp # pybind11 bindings
└── utils/                 # Utility modules
    ├── __init__.py
    └── logger.py          # Logging configuration
```

## Dependencies

### Python Packages
- **PySimpleGUI**: GUI framework
- **matplotlib**: Plotting and visualization
- **numpy**: Numerical computations
- **pybind11**: C++ Python bindings

### System Requirements
- Python 3.6 or higher
- C++ compiler with C++17 support
- CMake (for building C++ extensions)

## Installation

### Quick Setup
```bash
cd editor
./build.sh
```

### Manual Setup
1. Create a Python virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Build the C++ extension:
   ```bash
   python setup.py build_ext --inplace
   ```

## Usage

### Running the Editor
```bash
# Activate virtual environment
source venv/bin/activate

# Run the editor
python main.py
```

### Main Features

#### Main Window
- **Instrument List**: Select and manage synthesizer instruments
- **Pattern Editor**: Edit musical patterns and sequences
- **Waveform Display**: Real-time visualization of audio output
- **Control Sliders**: Adjust volume, filter frequency, and resonance

#### Instrument Editor
- **ADSR Envelope**: Configure attack, decay, sustain, and release
- **Oscillator Settings**: Choose waveform, transpose, detune, and gain
- **Filter Parameters**: Set filter type, frequency, and resonance
- **Effects**: Enable and configure reverb, delay, and distortion

#### Plot Window
- **Waveform Generation**: Create sine, sawtooth, square, and noise waveforms
- **Time Domain Display**: View waveform in time domain
- **Frequency Analysis**: FFT-based spectrum analysis
- **Interactive Controls**: Adjust frequency and regenerate waveforms

## Development

### Building the C++ Extension
The project includes C++ code for the synthesizer engine. To modify and rebuild:

1. Edit `cpp/synth_bindings.cpp`
2. Rebuild: `python setup.py build_ext --inplace`

### Integrating with Actual Softsynth
To integrate with the real softsynth C++ code:

1. Update `cpp/synth_bindings.cpp` to include actual softsynth headers
2. Modify `audio/synth_wrapper.py` to match the real API
3. Update `setup.py` to link with the softsynth library
4. Rebuild the extension

### Adding New Features
- **GUI Components**: Add new windows in the `gui/` directory
- **Audio Processing**: Extend `audio/synth_wrapper.py`
- **Utilities**: Add helper functions in `utils/`

## Troubleshooting

### Common Issues

1. **Import Errors**: Make sure the virtual environment is activated and dependencies are installed
2. **C++ Build Errors**: Check that you have a C++17 compatible compiler
3. **PySimpleGUI Issues**: Try updating tkinter: `pip install --upgrade tkinter`
4. **Audio Issues**: The editor currently runs in simulation mode if the C++ library isn't found

### Logging
The application creates log files with timestamp names (`synth_editor_YYYYMMDD_HHMMSS.log`) for debugging.

## License

This project is part of the 4K Softsynth suite. See the main project license for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## Future Enhancements

- MIDI input/output support
- VST plugin compatibility
- Advanced visualization modes
- Preset management system
- Multi-track sequencing
- Export to various audio formats
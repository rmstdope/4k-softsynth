# 4K Softsynth Editor

A Python-based editor for the 4K ARM64 softsynth with multiple GUI interfaces and direct ARM64 assembly integration.

## Features

- **Real-time ARM64 synthesizer integration** - Direct interface to ARM64 assembly code
- **Multiple interfaces** - Tkinter GUI (stable) and CLI
- **Instrument parameter editing** - ADSR envelopes, oscillator settings
- **ARM64 assembly integration** - C++ bindings for maximum performance
- **Cross-platform compatibility** - macOS (Apple Silicon), ARM64 Linux

## Quick Start

```bash
# Build the project (includes ARM64 synthesis and Python bindings)
./build.sh

# Launch with smart interface selection
python launch.py

# Or choose specific interface
python launch.py tkinter    # Stable Tkinter GUI
python launch.py cli        # Command-line interface
```

## Available Interfaces

### 1. Tkinter GUI (Recommended)

```bash
python tkinter_main.py
```

- **Native tkinter interface** - Most stable on all platforms
- **Real-time ARM64 integration** - Direct synthesizer control
- **ADSR parameter editing** - Visual sliders for envelope shaping
- **Test functions** - Built-in ARM64 engine testing and audio generation

### 2. Command-Line Interface

```bash
python cli_main.py
```

- **Full ARM64 functionality** - Complete synthesizer access without GUI
- **Performance testing** - Benchmark ARM64 assembly performance
- **Audio generation** - Create and export audio samples
- **Debug output** - Detailed synthesizer information and constants

### 3. Smart Launcher

```bash
python launch.py [interface]
```

- **Auto-detects** best available interface
- **Interface options**: `tkinter`, `cli`
- **Default preference**: tkinter → cli

## Requirements

- **Python 3.8+** (Python 3.14+ recommended)
- **ARM64 architecture** (Apple Silicon Mac or ARM64 Linux)
- **Build tools**: clang++, make
- **Python packages**: Listed in requirements.txt

### macOS Setup

```bash
# Install tkinter support (if missing)
brew install python-tk

# Build everything
./build.sh
```

## ARM64 Integration Details

The editor provides direct access to ARM64 assembly functions through C++ bindings:

### Synthesizer Functions

- `dope4ks_render()` - Main audio rendering loop
- `transform_values()` - Parameter transformation
- `envelope_function()` - ADSR envelope processing
- `process_stack()` - Audio processing pipeline

### Parameter Access

- **transformed_parameters** array manipulation
- **Real-time parameter updates** - ADSR, oscillator settings
- **Direct memory access** - Maximum performance

### Constants Access

```python
# Available ARM64 constants
SAMPLE_RATE: 44100
BEATS_PER_MINUTE: 125
MAX_NUM_INSTRUMENTS: 4
MAX_COMMANDS: 32
ENVELOPE_ID: 1
OSCILLATOR_ID: 2
```

## Usage Examples

### Basic Audio Generation

```python
# Initialize synthesizer
synth = SynthWrapper()

# Set ADSR envelope
synth.set_adsr(0, attack=0.1, decay=0.2, sustain=0.7, release=0.5, gain=0.8)

# Trigger note and render audio
synth.trigger_note(0, 69, 0.8)  # A4 note
audio_data = synth.render_audio(44100)  # 1 second of stereo audio
```

### Performance Testing

```bash
python cli_main.py
# Choose option 4: Run Performance Test
# Measures real-time factor (should be >1.0 for real-time capability)
```

### Parameter Experimentation

```bash
python tkinter_main.py
# Use GUI sliders to adjust ADSR parameters in real-time
# Click "Test ARM64 Engine" to verify synthesis
# Click "Play A4 Note" to hear parameter changes
```

## Build System

```bash
# Complete build (ARM64 synthesis + Python bindings)
./build.sh

# Manual build steps
cd softsynth && make              # Build ARM64 synthesizer
cd editor && python setup.py build_ext --inplace  # Build Python extension
```

## Project Structure

```
editor/
├── launch.py           # Smart launcher (recommended entry point)
├── tkinter_main.py     # Tkinter GUI (stable)
├── cli_main.py         # Command-line interface
├── main.py             # Legacy PySimpleGUI interface (deprecated)
├── audio/
│   └── synth_wrapper.py    # Python synthesizer interface
├── cpp/
│   └── synth_bindings.cpp  # C++ bindings to ARM64 assembly
├── gui/                    # PySimpleGUI modules
├── utils/                  # Logging and utilities
├── DEBUGGING.md            # Debugging guide for VS Code
└── build.sh               # Automated build script
```

## Debugging

The project includes comprehensive VS Code debugging support:

```bash
# Open in VS Code and use F5 to debug
code /Users/henrikku/repos/4k-softsynth

# Available debug configurations:
# - Debug Tkinter Editor    (GUI debugging)
# - Debug CLI Editor        (Command-line debugging)
# - Debug Editor Launcher   (Smart launcher debugging)
# - Debug softsynth         (C++ ARM64 debugging)
# - Debug test_softsynth    (ARM64 unit tests)
```

See [DEBUGGING.md](DEBUGGING.md) for detailed debugging instructions.

## Troubleshooting

### GUI Issues on macOS

```bash
# If tkinter is missing:
brew install python-tk

# Use the stable interface:
python launch.py tkinter
```

### Build Issues

```bash
# Clean and rebuild
make clean
./build.sh

# Check ARM64 synthesizer build
cd softsynth && make && ./bin/test_softsynth
```

### Performance Issues

```bash
# Verify ARM64 engine status
python cli_main.py  # Option 3: Show Synthesizer Info
# Should show "Ready: True" and ARM64 constants
```

## Development

### Adding New Parameters

1. Update `transformed_parameters` access in `synth_bindings.cpp`
2. Add getter/setter methods in `SynthWrapper`
3. Update GUI controls in `tkinter_main.py`

### Testing ARM64 Functions

```bash
# Direct ARM64 testing
cd softsynth && ./bin/test_softsynth

# Python integration testing
python example_arm64.py
```

This editor provides a complete interface to the 4K ARM64 softsynth, enabling real-time synthesis parameter control and audio generation through multiple user interface options.

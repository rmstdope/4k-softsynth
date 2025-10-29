# Debugging Guide for 4K Softsynth Editor

This guide explains how to debug the 4K Softsynth Editor using VS Code.

## Available Debug Configurations

The following debug configurations are available in VS Code (accessible via F5 or Run & Debug panel):

### 1. Debug Tkinter Editor

- **Target**: `__main__.py`
- **Purpose**: Debug the main Tkinter GUI application
- **Use case**: GUI development, ARM64 integration testing, parameter control debugging

### 2. Debug CLI Editor

- **Purpose**: Debug the command-line interface
- **Use case**: ARM64 synthesizer testing, performance analysis, headless operation

### 3. Debug Editor Launcher

- **Target**: `launch.py`
- **Purpose**: Debug the smart launcher with tkinter argument
- **Use case**: Interface selection logic, startup debugging

### 4. Debug softsynth (C++)

- **Target**: `softsynth/bin/softsynth`
- **Purpose**: Debug the native ARM64 synthesizer
- **Use case**: ARM64 assembly debugging, low-level performance analysis

### 5. Debug test_softsynth (C++)

- **Target**: `softsynth/bin/test_softsynth`
- **Purpose**: Debug ARM64 synthesizer unit tests
- **Use case**: ARM64 function validation, algorithm debugging

## Python Debugging Setup

### Environment Configuration

- **Python Interpreter**: `${workspaceFolder}/.venv/bin/python`
- **Working Directory**: `${workspaceFolder}/editor`
- **PYTHONPATH**: Automatically set to include editor directory
- **Console**: Integrated terminal for better VS Code integration

### Key Debugging Features

- **justMyCode**: Set to `false` to enable stepping into library code
- **stopOnEntry**: Set to `false` for normal startup (can be changed to `true`)
- **Console**: `integratedTerminal` for GUI compatibility

## Debugging Workflow

### For GUI Issues (Tkinter)

1. Set breakpoints in `__main__.py`
2. Select "Debug Tkinter Editor" configuration
3. Press F5 to start debugging
4. GUI will launch in debug mode
5. Use VS Code debug controls to step through code

### For ARM64 Synthesizer Issues

1. Set breakpoints in `audio/synth_wrapper.py` or `src/editor/cpp/synth_bindings.cpp`
2. Use "Debug Tkinter Editor" or "Debug CLI Editor"
3. Trigger ARM64 functions via GUI controls or CLI commands
4. Step through Python → C++ → ARM64 call chain

### For Performance Analysis

1. Use "Debug CLI Editor" configuration
2. Set breakpoints in performance testing functions
3. Use VS Code's performance profiling features
4. Monitor ARM64 function call timing

## Useful Breakpoint Locations

### Main GUI (`__main__.py`)

```python
# GUI initialization
def __init__(self):

# Parameter updates
def update_synth_parameters(self):

# ARM64 testing
def test_arm64_engine(self):

# Audio generation
def play_test_note(self):
```

### Synthesizer Wrapper (`audio/synth_wrapper.py`)

```python
# ARM64 initialization
def __init__(self, sample_rate: int = 44100, buffer_size: int = 1024):

# Audio rendering
def render_audio(self, num_samples: int) -> np.ndarray:

# Parameter setting
def set_adsr(self, instrument: int, attack: float, decay: float, ...):

# Note triggering
def trigger_note(self, instrument: int, note: int, velocity: float = 1.0):
```

```python
# Synthesizer testing
def test_synthesizer(self):

# Performance testing
def run_performance_test(self):
```

## ARM64 Integration Debugging

### C++ Bindings (`src/editor/cpp/synth_bindings.cpp`)

Set breakpoints in:

- `SynthEngine::initialize()`
- `SynthEngine::render_audio()`
- `SynthEngine::set_transformed_parameter()`

### Python-C++ Interface

1. Start with Python debug configuration
2. Step into C++ extension calls
3. Use mixed-mode debugging if needed
4. Monitor ARM64 function performance

## Common Debugging Scenarios

### 1. GUI Not Starting

- Debug: "Debug Tkinter Editor"
- Check: Tkinter import, virtual environment activation
- Breakpoint: `TkinterEditor.__init__()`

### 2. ARM64 Functions Not Working

- Debug: Any Python configuration
- Check: C++ extension loading, ARM64 library linking
- Breakpoint: `SynthWrapper.__init__()`, `render_audio()`

### 3. Audio Generation Issues

- Debug: "Debug Tkinter Editor" → click "Test ARM64 Engine"
- Breakpoint: `test_arm64_engine()`, `render_audio()`
- Monitor: Audio data arrays, sample values

### 4. Parameter Control Problems

- Debug: "Debug Tkinter Editor" → adjust ADSR sliders
- Breakpoint: `on_adsr_change()`, `set_adsr()`
- Monitor: Parameter values, ARM64 parameter array

## Debug Console Commands

While debugging, you can use the VS Code debug console:

```python
# Check synthesizer status
synth.is_ready()

# Get ARM64 constants
synth.get_constants()

# Generate test audio
audio = synth.render_audio(1000)

# Check parameter values
synth.get_transformed_parameter(0)
```

## Troubleshooting Debug Issues

### Python Debugger Not Working

1. Ensure Python extension is installed in VS Code
2. Check Python interpreter path in settings
3. Verify virtual environment is activated
4. Check PYTHONPATH configuration

### C++ Debugging Issues

1. Ensure C++ extension is installed
2. Check LLDB configuration on macOS
3. Verify debug symbols in compiled binaries
4. Check compiler flags include `-g`

### Mixed Python/C++ Debugging

1. Start with Python debugger
2. Use `justMyCode: false` to step into C++
3. Consider using external tools like `lldb` for deep C++ analysis
4. Use logging for ARM64 assembly debugging

## Performance Debugging

### ARM64 Performance Analysis

1. Use "Debug CLI Editor" → Performance Test
2. Set breakpoints in timing sections
3. Use VS Code performance profiler
4. Monitor real-time factor calculations

### Memory Analysis

1. Debug long-running audio generation
2. Monitor numpy array allocations
3. Check ARM64 memory access patterns
4. Use memory profiling tools if needed

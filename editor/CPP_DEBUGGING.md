# Debugging C++ SynthEngine Class

This guide explains multiple methods to debug the C++ SynthEngine class in the synth_bindings.cpp file.

## The Problem

When debugging Python code that calls C++ extensions (pybind11), Python debuggers cannot step into the compiled C++ code. You need special techniques to debug the C++ portion.

## Method 1: Debug Logging (Easiest)

I've added debug logging macros to the C++ code. To enable debug output:

### Enable Debug Build

```bash
cd editor
# Build with debug symbols and DEBUG flag
CPPFLAGS="-g -O0 -DDEBUG" python setup.py build_ext --inplace --debug
```

### Run Python Code with Debug Output

```bash
cd editor
python __main__.py
```

You'll see debug output like:

```
[DEBUG] SynthEngine: Constructor called: sample_rate=44100, buffer_size=1024
[DEBUG] SynthEngine: Initialize called
[DEBUG] SynthEngine: Initialize completed successfully
[DEBUG] SynthEngine: render_audio called: num_samples=44100
[DEBUG] SynthEngine: Calling dope4ks_render with 352800 bytes
[DEBUG] SynthEngine: dope4ks_render completed successfully
```

## Method 2: Mixed-Mode Debugging (Advanced)

### Step 1: Build Debug Extension

```bash
cd editor
# Use the VS Code task or run manually:
CPPFLAGS="-g -O0 -DDEBUG" python setup.py build_ext --inplace --debug
```

### Step 2: Start Python Debugger

1. Open `__main__.py` in VS Code
2. Set breakpoints in Python code before C++ calls
3. Use "Debug Python + C++ (Tkinter)" configuration
4. Start debugging (F5)

### Step 3: Attach C++ Debugger

1. When Python hits a breakpoint, note the Process ID
2. In VS Code, start "Debug C++ Extension (Attach to Python)"
3. Select the Python process when prompted
4. Set breakpoints in `synth_bindings.cpp`
5. Continue Python execution

## Method 3: Terminal-Based Debugging

### Using LLDB directly:

```bash
cd editor

# Start Python with debugger attached
lldb -- python __main__.py

# In LLDB:
(lldb) process launch
# Wait for Python to load the C++ extension
(lldb) process interrupt
(lldb) breakpoint set --file synth_bindings.cpp --line 25  # Constructor
(lldb) breakpoint set --file synth_bindings.cpp --line 45  # render_audio
(lldb) continue
```

## Method 4: GDB Alternative (Linux/macOS)

```bash
cd editor

# Start with GDB
gdb --args python __main__.py

# In GDB:
(gdb) set environment PYTHONPATH=.
(gdb) run
# When extension loads:
(gdb) break synth_bindings.cpp:SynthEngine::render_audio
(gdb) continue
```

## Key Debugging Points in C++

### Constructor Debugging

**File**: `synth_bindings.cpp`, line ~25
**Breakpoint**: `SynthEngine::SynthEngine()`
**Purpose**: Verify object creation

### Initialization Debugging

**File**: `synth_bindings.cpp`, line ~35
**Breakpoint**: `SynthEngine::initialize()`
**Purpose**: Check initialization logic

### Audio Rendering Debugging

**File**: `synth_bindings.cpp`, line ~45
**Breakpoint**: `SynthEngine::render_audio()`
**Purpose**: Monitor audio generation

### Parameter Setting Debugging

**File**: `synth_bindings.cpp`, line ~90
**Breakpoint**: `SynthEngine::set_transformed_parameter()`
**Purpose**: Track parameter changes

## Debugging Workflow

### For Parameter Issues:

1. Set breakpoint in Python: `synth.set_adsr()`
2. Step into C++: `SynthEngine::set_envelope_parameters()`
3. Verify ARM64 call: `set_transformed_parameter()`
4. Check values: `transformed_parameters[]` array

### For Audio Issues:

1. Set breakpoint in Python: `synth.render_audio()`
2. Step into C++: `SynthEngine::render_audio()`
3. Verify ARM64 call: `dope4ks_render()`
4. Check output: `output.data()` buffer

### For Initialization Issues:

1. Set breakpoint in Python: `SynthWrapper.__init__()`
2. Step into C++: `SynthEngine::SynthEngine()`
3. Check: `SynthEngine::initialize()`
4. Verify state: `initialized_` flag

## Debug Build Configuration

### Manual Debug Build:

```bash
cd editor
export CPPFLAGS="-g -O0 -DDEBUG -fno-omit-frame-pointer"
export CFLAGS="-g -O0 -DDEBUG -fno-omit-frame-pointer"
python setup.py build_ext --inplace --debug
```

### VS Code Task:

Use the "build-debug-extension" task from Command Palette:

- `Ctrl+Shift+P` → "Tasks: Run Task" → "build-debug-extension"

## Verification

### Check Debug Symbols:

```bash
cd editor
file synth_engine*.so
# Should show "not stripped" and debug info

nm synth_engine*.so | grep SynthEngine
# Should show symbol table
```

### Test Debug Logging:

```bash
cd editor
python -c "
from audio.synth_wrapper import SynthWrapper
synth = SynthWrapper()
synth.render_audio(1000)
"
```

Should output debug messages if DEBUG flag is enabled.

## Troubleshooting

### No Debug Symbols

- Ensure `-g` flag in CPPFLAGS
- Use `--debug` flag with setup.py
- Check compiler output for warnings

### Can't Attach Debugger

- Use `sudo` if necessary (macOS)
- Check process permissions
- Verify debugger (lldb/gdb) installation

### Mixed-Mode Issues

- Ensure both Python and C++ extensions have debug symbols
- Check VS Code C++ extension is installed
- Verify launch.json configurations

### Debug Output Missing

- Verify `-DDEBUG` flag is set
- Check that stdout is not redirected
- Ensure debug build completed successfully

## Alternative: Printf Debugging

If sophisticated debugging fails, add simple printf statements:

```cpp
// In synth_bindings.cpp
#include <cstdio>

std::vector<float> render_audio(int num_samples) {
    printf("C++ DEBUG: render_audio called with %d samples\n", num_samples);
    // ... rest of function
    printf("C++ DEBUG: render_audio completed\n");
    return output;
}
```

This will always show output regardless of debug configuration.

## Summary

**Easiest**: Method 1 (Debug Logging) - just rebuild with DEBUG flag
**Most Powerful**: Method 2 (Mixed-Mode) - full debugger support  
**Most Reliable**: Method 4 (Printf) - always works

Choose based on your debugging needs and comfort level with different tools.

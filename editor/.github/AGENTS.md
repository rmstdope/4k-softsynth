# 4K Softsynth Editor - Python Project Instructions

## Project Overview

This is the Python-based GUI editor component of the 4K Softsynth project. It provides:

- **GUI Interface**: Tkinter-based parameter editing interface
- **C++ Integration**: Python bindings to ARM64 synthesizer via pybind11
- **Real-time Audio**: Audio device management and synthesis control
- **Modern Python Packaging**: Follows PEP 518 standards with src/ layout

## Project Structure

```
editor/
├── src/editor/           # Main Python package (src layout)
│   ├── __main__.py      # Module entry point
│   ├── gui/             # GUI components subpackage
│   ├── audio/           # Audio processing subpackage
│   ├── cpp/             # C++ binding source code
│   └── utils/           # Utility modules
├── tests/               # Test suite
├── pyproject.toml       # Modern Python project configuration
├── setup.py            # C++ extension build logic
└── main.py             # Alternative entry point
```

## Python-Specific Guidelines

### Package Structure Rules

- **ALWAYS** use absolute imports (no relative imports like `from .module`)
- **Maintain** src/ layout structure for proper packaging
- **Follow** PEP 8 naming conventions and style guidelines
- **Keep** `__init__.py` files clean with proper exports
- **Avoid** exporting GUI classes from the main package - use subpackage imports instead

### Package Organization Principles

- **Main package** (`editor`): Contains only metadata and documentation, no class exports
- **Subpackages** (`gui`, `audio`, `utils`, `cpp`): Export their specific functionality
- **Import from subpackages**: `from editor.gui import Editor` (preferred)
- **Avoid coupling**: Main package should not import from subpackages in `__init__.py`

### Import Standards

```python
# ✅ Correct - subpackage imports (preferred)
from editor.gui import Editor, ParameterControl
from editor.audio import SynthWrapper, Audio
from editor.utils import setup_logger

# ✅ Also correct - direct imports when needed
from editor.audio.synth_wrapper import SynthWrapper
from editor.gui.parameter_control import ParameterControl

# ❌ Wrong - relative imports
from .audio.synth_wrapper import SynthWrapper
from .gui.parameter_control import ParameterControl
```

### Entry Point Management

The project supports multiple entry points:

1. **Module execution**: `python -m editor` (from src/ directory)
2. **Direct execution**: `python src/editor/__main__.py`
3. **Alternative entry**: `python main.py`

When modifying entry points:

- Test ALL entry methods after changes
- Maintain backwards compatibility
- Ensure VS Code debugging configurations work

### Build System Architecture

#### Modern Python Packaging (`pyproject.toml`)

- **Dependencies**: Runtime and development dependencies
- **Build configuration**: Uses setuptools with pybind11
- **Development tools**: pytest, black, flake8, mypy, pylint
- **Entry points**: Console scripts configuration

#### C++ Extension Building (`setup.py`)

- **Custom build logic**: `CustomBuildExt` class handles ARM64 objects
- **pybind11 integration**: Python-C++ bindings
- **ARM64 dependencies**: Links with softsynth ARM64 objects
- **Debug support**: Conditional debug flags

### Development Workflows

#### Code Modifications

1. **Test imports first**: Verify absolute imports work correctly
2. **Run pylint**: Check code quality with `pylint src/editor/` and fix issues
3. **Run tests**: Use `pytest tests/` to verify functionality
4. **Check entry points**: Test all execution methods
5. **Verify debugging**: Ensure VS Code configurations work

#### Build and Installation

```bash
# Development installation (editable)
pip install -e .

# Build C++ extensions
python setup.py build_ext --inplace

# Run tests
pytest tests/ -v
```

#### VS Code Integration

The project includes VS Code configurations for:

- **Python debugging**: Module and direct execution methods
- **C++ debugging**: Combined Python+C++ debugging support
- **Build tasks**: Integrated build system

When modifying VS Code configurations:

- Test from correct working directories (`editor/src/`)
- Verify Python path settings
- Ensure C++ extension debugging works

### Code Quality Standards

#### Style and Formatting

- **Follow PEP 8**: Use consistent naming and formatting
- **Type hints**: Add type annotations where beneficial
- **Docstrings**: Document classes and complex functions
- **Line length**: 88 characters (Black formatter standard)

#### Error Handling

- **Graceful degradation**: Handle missing PyAudio gracefully
- **Informative errors**: Provide clear error messages
- **Logging**: Use proper logging instead of print statements
- **Exception handling**: Catch specific exceptions, not bare except

#### Pylint Integration

- **Always run pylint**: Check code quality before committing changes
- **Use project configuration**: Project includes `.pylintrc` with custom settings
- **Fix issues incrementally**: Address pylint warnings as you encounter them
- **Common fixes needed**:
  - Missing docstrings for public methods
  - Unused imports or variables
  - Line length violations (max 88 characters)
  - Variable naming conventions

```bash
# Run pylint on specific files
pylint src/editor/editor.py src/editor/parameter_control.py

# Run pylint on entire package
pylint src/editor/

# Generate pylint report
pylint src/editor/ --output-format=text > pylint_report.txt
```

#### Testing Standards

- **Comprehensive tests**: Cover main functionality paths
- **Integration tests**: Test GUI components and C++ bindings
- **Mocking**: Use mocks for external dependencies (audio devices)
- **Test isolation**: Each test should be independent

### C++ Integration Guidelines

**C++ Module Structure**:

- All C++ binding code is in `src/editor/cpp/`
- Main binding file: `src/editor/cpp/synth_bindings.cpp`
- Build system references this path in `setup.py`
- Compiled extensions are placed in the project root

#### pybind11 Bindings

- **Memory management**: Proper RAII and smart pointers
- **Error propagation**: Convert C++ exceptions to Python exceptions
- **Type conversion**: Handle Python/C++ type conversions correctly
- **Performance**: Minimize copying between Python and C++

#### ARM64 Integration

- **Object dependencies**: Ensure ARM64 objects are built before Python extension
- **Debug support**: Maintain debug symbol support for C++ debugging
- **Platform compatibility**: Handle macOS ARM64 specifics correctly

### Common Modification Patterns

#### Adding New GUI Components

1. Create component in the `editor/gui/` subpackage
2. Add absolute imports to `editor/gui/__init__.py`
3. Update main editor integration in `editor/gui/editor.py`
4. Add tests for new functionality
5. Update documentation

**GUI Module Structure**:

- All GUI components are organized in `src/editor/gui/`
- Main application window: `editor/gui/editor.py`
- Reusable UI controls: `editor/gui/parameter_control.py`
- Use absolute imports: `from editor.gui.component import Component`

#### Modifying Build System

1. **Understand dependencies**: Changes affect both Python and C++ components
2. **Test incrementally**: Verify each build step works
3. **Maintain VS Code support**: Update debugging configurations if needed
4. **Document changes**: Update relevant documentation

#### Package Structure Changes

1. **Plan carefully**: Package moves affect imports throughout
2. **Update ALL imports**: Convert to new absolute import paths
3. **Test thoroughly**: Verify all entry points and VS Code debugging
4. **Update build configuration**: Modify pyproject.toml if needed

### Debugging and Development

#### Common Issues

- **Import errors**: Usually caused by incorrect working directory or Python path
- **VS Code debugging fails**: Check working directory in launch.json
- **C++ extension not found**: Rebuild with `python setup.py build_ext --inplace`
- **GUI issues**: Check tkinter availability and display environment

#### Development Environment Setup

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows

# Install in development mode
pip install -e .

# Install development dependencies
pip install -e ".[dev]"
```

### Testing Checklist

Before submitting changes:

- [ ] All imports are absolute (no relative imports)
- [ ] `python -m editor` works from src/ directory
- [ ] `python src/editor/__main__.py` works
- [ ] `python main.py` works (if it exists)
- [ ] VS Code "Debug Main Editor" configuration works
- [ ] pytest tests/ passes
- [ ] C++ extension builds successfully
- [ ] No circular import issues
- [ ] `pylint src/editor/` passes without critical errors
- [ ] Code follows PEP 8 style guidelines (checked by pylint)

### Emergency Recovery

If the project becomes unbuildable:

1. **Check working directory**: Most issues are path-related
2. **Verify virtual environment**: Ensure correct Python environment
3. **Rebuild C++ extension**: `python setup.py clean --all && python setup.py build_ext --inplace`
4. **Reset imports**: Convert any relative imports back to absolute
5. **Test entry points**: Verify each execution method individually

Remember: This project bridges Python and high-performance C++/ARM64 code. Changes must respect both ecosystems and maintain the integration points carefully.

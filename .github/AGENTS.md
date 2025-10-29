# 4K Softsynth Project - AI Agent Instructions

## Core Project Rules

**CRITICAL**: Never commit anything without explicit user approval.

## Project Overview

This is a high-performance ARM64 software synthesizer project with the following architecture:

```
4k-softsynth/
├── softsynth/          # Core ARM64 synthesizer engine
├── editor/             # Python-based GUI editor and bindings
├── scripts/            # Build and utility scripts
└── .github/            # CI/CD and agent instructions
```

## Project Structure Guidelines

### Directory Organization

- **Root level**: Build configuration, project-wide documentation
- **softsynth/**: ARM64 assembly core, C++ headers, low-level audio processing
- **editor/**: Python package with modern src/ layout, GUI interfaces, Python-C++ bindings
- **Cross-component**: Shared headers, build dependencies, integration points

### Build System Hierarchy

1. **Root Makefile**: Orchestrates builds across components
2. **Component Makefiles**: Handle component-specific builds
3. **Python build**: Uses pyproject.toml + setup.py for C++ extensions
4. **Integration**: C++/Python bindings via pybind11

## Development Workflow

### Code Changes

1. **Analyze first**: Understand current structure before making changes
2. **Test thoroughly**: Verify all entry points and build systems work
3. **Maintain compatibility**: Preserve existing interfaces and workflows
4. **Follow patterns**: Use established project conventions

### Build and Testing

- Always test builds after structural changes
- Verify both Python and C++ components build correctly
- Test multiple entry points (CLI, GUI, module execution)
- Ensure VS Code debugging configurations remain functional

### File Management

- Preserve package structure and import paths
- Maintain backwards compatibility for entry points
- Keep build artifacts separate from source code
- Follow Python packaging best practices (src/ layout)

## Architecture Principles

### Component Separation

- **Low-level**: ARM64 assembly for performance-critical synthesis
- **Mid-level**: C++ bindings and data structures
- **High-level**: Python GUI and user interfaces
- **Integration**: Clean boundaries with proper abstraction layers

### Performance Considerations

- ARM64 assembly for real-time audio processing
- Efficient C++/Python bindings
- Minimal overhead in critical paths
- Hardware-optimized algorithms

### Cross-Platform Support

- Primary target: macOS Apple Silicon
- Secondary: ARM64 Linux
- Build system accommodates platform differences

## Code Quality Standards

### Structure

- Follow established project organization
- Maintain clean separation of concerns
- Use appropriate abstraction levels
- Keep interfaces well-defined

### Documentation

- Update relevant documentation when making changes
- Maintain README files for significant changes
- Comment complex algorithms and integrations
- Document build and setup procedures

### Testing

- Verify functionality across all interfaces
- Test build system changes thoroughly
- Ensure debugging and development tools work
- Validate performance critical paths

## Integration Points

### Python-C++ Bindings

- Use pybind11 for clean interfaces
- Maintain proper error handling
- Respect Python packaging conventions
- Handle ARM64 assembly integration carefully

### Build Dependencies

- Understand component interdependencies
- Maintain proper build order
- Handle shared resources correctly
- Preserve development tool integration

### Development Environment

- Maintain VS Code configuration functionality
- Preserve debugging capabilities
- Keep development workflows operational
- Support multiple development styles

## Modification Guidelines

When modifying this project:

1. **Read relevant instructions** in `.github/AGENTS.md` for specific domains
2. **Understand dependencies** between components before changes
3. **Preserve working functionality** - don't break existing workflows
4. **Test comprehensively** - verify all entry points and build methods
5. **Follow established patterns** - maintain consistency with existing code
6. **Document significant changes** - update relevant documentation

## Emergency Procedures

If builds break or functionality is lost:

1. **Stop immediately** and assess the situation
2. **Identify what changed** and potential impact
3. **Test incrementally** to isolate issues
4. **Revert if necessary** to maintain project stability
5. **Ask for guidance** rather than making assumptions

Remember: This is a complex, performance-critical project with multiple integration points. Careful analysis and testing are essential for any modifications.

# Makefile for 4K Softsynth Editor

.PHONY: all install build clean run test help venv

# Default target
all: install build

# Setup virtual environment and install dependencies
install: venv
	@echo "Installing Python dependencies..."
	./venv/bin/pip install --upgrade pip
	./venv/bin/pip install -r requirements.txt
	./venv/bin/pip install setuptools wheel build pytest

# Create virtual environment
venv:
	@echo "Creating Python virtual environment..."
	python3 -m venv venv
	@echo "Virtual environment created in ./venv"

# Build C++ extension
build: build-softsynth
	@echo "Building C++ extension..."
	./venv/bin/python setup.py build_ext --inplace

# Build the ARM64 softsynth dependency
build-softsynth:
	@echo "Building ARM64 softsynth..."
	cd ../softsynth && make clean && make all

# Run the editor
run:
	@echo "Starting 4K Softsynth Editor..."
	./venv/bin/python main.py

# Run tests
test:
	@echo "Running tests..."
	./venv/bin/python -m pytest tests/ -v

# Clean build artifacts
clean:
	@echo "Cleaning build artifacts..."
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf __pycache__/
	find . -name "*.pyc" -delete
	find . -name "*.pyo" -delete
	find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
	rm -f *.so
	rm -f synth_editor_*.log

# Deep clean (includes virtual environment)
distclean: clean
	@echo "Removing virtual environment..."
	rm -rf venv/

# Install development dependencies
dev-install: install
	./venv/bin/pip install black flake8 mypy

# Format code
format:
	./venv/bin/python -m black .

# Lint code
lint:
	./venv/bin/python -m flake8 .
	./venv/bin/python -m mypy .

# Package for distribution
package: clean build
	./venv/bin/python -m build

# Install in development mode
dev: venv
	./venv/bin/pip install -e .

# Help target
help:
	@echo "Available targets:"
	@echo "  all        - Install dependencies and build (default)"
	@echo "  install    - Create venv and install Python dependencies"
	@echo "  venv       - Create virtual environment only"
	@echo "  build      - Build C++ extension"
	@echo "  run        - Run the editor application"
	@echo "  test       - Run tests"
	@echo "  clean      - Remove build artifacts"
	@echo "  distclean  - Remove build artifacts and virtual environment"
	@echo "  dev-install- Install development dependencies"
	@echo "  format     - Format code with black"
	@echo "  lint       - Lint code with flake8 and mypy"
	@echo "  package    - Package for distribution"
	@echo "  dev        - Install in development mode"
	@echo "  help       - Show this help message"
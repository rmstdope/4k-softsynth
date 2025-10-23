#!/bin/bash
# Build script for the 4K Softsynth Editor
# This script sets up the Python environment and builds the C++ extension

echo "Setting up 4K Softsynth Editor build environment..."

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install Python dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Install build dependencies
echo "Installing build dependencies..."
pip install setuptools wheel build

# Build the ARM64 softsynth first
echo "Building ARM64 softsynth..."
cd ../softsynth
make clean
make all
cd ../editor

# Build the C++ extension
echo "Building C++ extension..."
python setup.py build_ext --inplace

# Make the script executable
echo "Build complete!"
echo ""
echo "To run the editor:"
echo "1. Activate the virtual environment: source venv/bin/activate"
echo "2. Run the editor: python main.py"
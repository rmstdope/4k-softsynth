#!/bin/bash
#
# Force rebuild of ARM64 objects and Python extension
# Use this when you want to ensure everything is rebuilt from scratch
#

set -e

echo "🔧 Force rebuilding ARM64 assembly objects..."
cd ../softsynth
make clean
make bin/softsynth.o bin/song.o

echo "🔧 Rebuilding Python extension..."
cd ../editor
rm -f synth_engine*.so
rm -rf build/
/Users/henrikku/repos/4k-softsynth/.venv/bin/python setup.py build_ext --inplace --debug

echo "✅ Full rebuild complete!"
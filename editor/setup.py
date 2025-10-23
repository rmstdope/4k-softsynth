"""
Setup script for building the C++ extension module
"""

from pybind11.setup_helpers import Pybind11Extension, build_ext
from pybind11 import get_cmake_dir
import pybind11
from setuptools import setup, Extension
import os

# Define the extension module
ext_modules = [
    Pybind11Extension(
        "synth_engine",
        [
            "cpp/synth_bindings.cpp",
        ],
        include_dirs=[
            # Path to pybind11 headers
            pybind11.get_include(),
            # Path to softsynth headers  
            "../softsynth/include",
            "../softsynth/src/arm64",
            # System paths
            "/usr/local/include",
        ],
        libraries=["m"],  # Math library
        library_dirs=[
            "../softsynth/bin",
            "/usr/local/lib",
        ],
        # Link with the compiled ARM64 softsynth objects
        extra_objects=[
            "../softsynth/bin/softsynth.o",
            "../softsynth/bin/song.o",
        ],
        language='c++',
        cxx_std=17,
        define_macros=[
            ("VERSION_INFO", '"dev"'),
        ],
    ),
]

setup(
    name="synth_engine",
    ext_modules=ext_modules,
    cmdclass={"build_ext": build_ext},
    zip_safe=False,
    python_requires=">=3.6",
)
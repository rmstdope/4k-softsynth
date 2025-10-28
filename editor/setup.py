"""
Setup script for building the C++ extension module
"""

from pybind11.setup_helpers import Pybind11Extension, build_ext
from pybind11 import get_cmake_dir
import pybind11
from setuptools import setup, Extension
import os
import subprocess
import sys
from pathlib import Path

class CustomBuildExt(build_ext):
    """Custom build extension that rebuilds ARM64 objects when assembly files change"""
    
    def run(self):
        # Check if we need to rebuild ARM64 objects
        self.build_arm64_objects()
        super().run()
    
    def build_arm64_objects(self):
        """Build ARM64 assembly objects if source files are newer"""
        softsynth_dir = Path("../softsynth")
        
        # Assembly source files
        asm_sources = [
            softsynth_dir / "src/arm64/softsynth.asm",
            softsynth_dir / "src/arm64/song.asm", 
            softsynth_dir / "src/arm64/common.asm",
        ]
        
        # Object files
        obj_files = [
            softsynth_dir / "bin/softsynth.o",
            softsynth_dir / "bin/song.o",
        ]
        
        # Check if any assembly file is newer than object files
        need_rebuild = False
        
        for obj_file in obj_files:
            if not obj_file.exists():
                need_rebuild = True
                break
                
        if not need_rebuild:
            obj_time = min(os.path.getmtime(obj) for obj in obj_files if obj.exists())
            for asm_file in asm_sources:
                if asm_file.exists() and os.path.getmtime(asm_file) > obj_time:
                    need_rebuild = True
                    break
        
        if need_rebuild:
            print("🔧 Assembly files changed, rebuilding ARM64 objects...")
            try:
                # Run make in the softsynth directory to rebuild objects
                result = subprocess.run(
                    ["make", "bin/softsynth.o", "bin/song.o"],
                    cwd=softsynth_dir,
                    check=True,
                    capture_output=True,
                    text=True
                )
                print("✅ ARM64 objects rebuilt successfully")
                if result.stdout:
                    print(result.stdout)
            except subprocess.CalledProcessError as e:
                print(f"❌ Failed to rebuild ARM64 objects: {e}")
                if e.stdout:
                    print("STDOUT:", e.stdout)
                if e.stderr:
                    print("STDERR:", e.stderr)
                sys.exit(1)
        else:
            print("✅ ARM64 objects are up to date")

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
            ("DEBUG", None),
        ],
    ),
]

setup(
    name="synth_engine",
    ext_modules=ext_modules,
    cmdclass={"build_ext": CustomBuildExt},
    zip_safe=False,
    python_requires=">=3.6",
)
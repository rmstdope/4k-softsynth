#!/usr/bin/env python3
"""
Module entry point for running the 4K Softsynth Editor as a package
Usage: python -m editor
"""

import sys
from editor.gui.editor import Editor


def main():
    """Main entry point"""
    app = Editor()
    return app.run()


if __name__ == "__main__":
    sys.exit(main())

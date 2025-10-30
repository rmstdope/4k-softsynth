"""Menu management component for the audio editor using CustomTkinter."""

import tkinter as tk
from tkinter import messagebox


class MenuManager:
    """Manages the menu bar and window operations."""

    def __init__(self, root, main_editor):
        """Initialize the menu manager.
        
        Args:
            root: The tkinter root window
            main_editor: Reference to the main editor controller
        """
        self.root = root
        self.main_editor = main_editor
        self.menubar = None

    def create_menu_bar(self):
        """Create and configure the menu bar."""
        self.menubar = tk.Menu(self.root)
        self.root.config(menu=self.menubar)

        # File menu
        file_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New Project", command=self.new_project)
        file_menu.add_command(label="Open Project", command=self.open_project)
        file_menu.add_separator()
        file_menu.add_command(label="Save Project", command=self.save_project)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.on_window_close)

        # Help menu
        help_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)

    def new_project(self):
        """Create a new project."""
        if hasattr(self.main_editor, 'status_panel'):
            self.main_editor.status_panel.log_output("New project created")

    def open_project(self):
        """Open an existing project."""
        if hasattr(self.main_editor, 'status_panel'):
            self.main_editor.status_panel.log_output("Open project dialog")

    def save_project(self):
        """Save the current project."""
        if hasattr(self.main_editor, 'status_panel'):
            self.main_editor.status_panel.log_output("Project saved")

    def show_about(self):
        """Show about dialog."""
        messagebox.showinfo(
            "About Audio Editor",
            "Audio Editor v1.0\n\n"
            "A synthesizer editor for 4k productions.\n"
            "Built with Python and tkinter."
        )

    def on_window_close(self):
        """Handle window close event - cleanup resources."""
        try:
            # Cleanup audio through main editor
            if hasattr(self.main_editor, 'audio') and self.main_editor.audio:
                self.main_editor.audio.cleanup()
                if hasattr(self.main_editor, 'status_panel'):
                    self.main_editor.status_panel.log_output("✓ Audio cleanup completed")

            # Close the window
            self.root.destroy()
        except (RuntimeError, tk.TclError) as e:
            if hasattr(self.main_editor, 'logger'):
                self.main_editor.logger.error("Error during cleanup: %s", e)
            self.root.destroy()

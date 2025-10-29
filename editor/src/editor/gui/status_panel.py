"""Status panel component for the audio editor."""

import tkinter as tk
from tkinter import ttk, scrolledtext


class StatusPanel:
    """Manages status display, output logging, and user feedback."""
    
    def __init__(self, main_editor):
        """Initialize the status panel.
        
        Args:
            main_editor: Reference to the main editor controller
        """
        self.main_editor = main_editor
        self.output_text = None
        self.status_var = None
        
    def create_output_section(self, parent_frame):
        """Create output section."""
        output_frame = ttk.LabelFrame(parent_frame, text="Output",
                                    padding="5")
        output_frame.grid(row=2, column=0, columnspan=2,
                        sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
                        
        # Create scrolled text widget for output
        self.output_text = scrolledtext.ScrolledText(
            output_frame,
            height=8,
            width=80,
            wrap=tk.WORD,
            font=("Consolas", 9),
            state=tk.DISABLED
        )
        self.output_text.pack(fill=tk.BOTH, expand=True)
        
        # Configure text tags for different message types
        self.output_text.tag_configure("success", foreground="green")
        self.output_text.tag_configure("error", foreground="red")
        self.output_text.tag_configure("warning", foreground="orange")
        self.output_text.tag_configure("info", foreground="blue")
        
    def create_status_bar(self, parent_frame):
        """Create status bar."""
        status_frame = ttk.Frame(parent_frame)
        status_frame.grid(row=3, column=0, columnspan=2,
                        sticky=(tk.W, tk.E), pady=(0, 5))
                        
        # Status label
        self.status_var = tk.StringVar(value="Ready")
        status_label = ttk.Label(status_frame, textvariable=self.status_var,
                               relief=tk.SUNKEN, anchor=tk.W,
                               font=("Arial", 8))
        status_label.pack(fill=tk.X, padx=(0, 5))
        
    def log_output(self, message):
        """Log a message to the output text widget.
        
        Args:
            message: The message to log
        """
        if not self.output_text:
            return
            
        # Enable text widget temporarily
        self.output_text.config(state=tk.NORMAL)
        
        # Determine message type and tag
        tag = None
        if "✓" in message or "▶" in message or "📊" in message or "🎵" in message:
            tag = "success"
        elif "✗" in message or "❌" in message:
            tag = "error"
        elif "⚠" in message or "warning" in message.lower():
            tag = "warning"
        elif "ℹ️" in message or "🔧" in message:
            tag = "info"
            
        # Insert message with timestamp
        import datetime
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        full_message = f"[{timestamp}] {message}\n"
        
        if tag:
            self.output_text.insert(tk.END, full_message, tag)
        else:
            self.output_text.insert(tk.END, full_message)
            
        # Scroll to end
        self.output_text.see(tk.END)
        
        # Disable text widget again
        self.output_text.config(state=tk.DISABLED)
        
        # Update status bar
        if self.status_var:
            # Extract clean message for status bar (remove emojis and timestamp)
            clean_message = message.replace("✓", "").replace("✗", "")
            clean_message = clean_message.replace("🎵", "").replace("📊", "")
            clean_message = clean_message.replace("⏸", "").replace("⏹", "")
            clean_message = clean_message.replace("▶", "").strip()
            self.status_var.set(clean_message[:50] + "..." if len(clean_message) > 50 else clean_message)
            
    def clear_output(self):
        """Clear the output text widget."""
        if self.output_text:
            self.output_text.config(state=tk.NORMAL)
            self.output_text.delete(1.0, tk.END)
            self.output_text.config(state=tk.DISABLED)
            
    def set_status(self, message):
        """Set the status bar message.
        
        Args:
            message: The status message to display
        """
        if self.status_var:
            self.status_var.set(message[:80] + "..." if len(message) > 80 else message)
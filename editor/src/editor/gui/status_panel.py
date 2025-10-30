"""Status panel component for the audio editor using CustomTkinter."""

import datetime
import customtkinter as ctk


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
        output_frame = ctk.CTkFrame(parent_frame, corner_radius=10)
        output_frame.grid(row=2, column=0, columnspan=2,
                        sticky="nsew", padx=5, pady=(0, 10))

        # Title label
        title_label = ctk.CTkLabel(output_frame, text="Output",
                                  font=ctk.CTkFont(size=16, weight="bold"))
        title_label.pack(pady=(15, 10))

        # Create text widget for output using CTkTextbox
        self.output_text = ctk.CTkTextbox(
            output_frame,
            height=200,
            width=600,
            wrap="word",
            font=ctk.CTkFont(family="Consolas", size=10),
            state="disabled"
        )
        self.output_text.pack(fill="both", expand=True, padx=15, pady=(0, 15))

    def create_status_bar(self, parent_frame):
        """Create status bar."""
        status_frame = ctk.CTkFrame(parent_frame, corner_radius=10, height=40)
        status_frame.grid(row=3, column=0, columnspan=2,
                        sticky="ew", padx=5, pady=(0, 5))
        status_frame.grid_propagate(False)

        # Status label
        self.status_text = "Ready"
        self.status_label = ctk.CTkLabel(status_frame, text=self.status_text,
                                        font=ctk.CTkFont(size=10),
                                        anchor="w")
        self.status_label.pack(fill="x", padx=15, pady=10)

    def log_output(self, message):
        """Log a message to the output text widget.

        Args:
            message: The message to log
        """
        if not self.output_text:
            return

        # Enable text widget temporarily
        self.output_text.configure(state="normal")

        # Determine text color based on message type
        text_color = None
        if "✓" in message or "▶" in message or "📊" in message or "🎵" in message:
            text_color = "green"
        elif "✗" in message or "❌" in message:
            text_color = "red"
        elif "⚠" in message or "warning" in message.lower():
            text_color = "orange"
        elif "ℹ️" in message or "🔧" in message:
            text_color = "lightblue"

        # Insert message with timestamp
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        full_message = f"[{timestamp}] {message}\n"

        # Insert the message - CTkTextbox doesn't support text tags, so we just add the text
        self.output_text.insert("end", full_message)

        # Scroll to end
        self.output_text.see("end")

        # Disable text widget again
        self.output_text.configure(state="disabled")

        # Update status bar
        if hasattr(self, 'status_label'):
            # Extract clean message for status bar (remove emojis)
            clean_message = message.replace("✓", "").replace("✗", "")
            clean_message = clean_message.replace("🎵", "").replace("📊", "")
            clean_message = clean_message.replace("⏸", "").replace("⏹", "")
            clean_message = clean_message.replace("▶", "").strip()
            display_message = clean_message[:50] + "..." if len(clean_message) > 50 else clean_message
            self.status_label.configure(text=display_message)

    def clear_output(self):
        """Clear the output text widget."""
        if self.output_text:
            self.output_text.configure(state="normal")
            self.output_text.delete("1.0", "end")
            self.output_text.configure(state="disabled")

    def set_status(self, message):
        """Set the status bar message.

        Args:
            message: The status message to display
        """
        if hasattr(self, 'status_label'):
            display_message = message[:80] + "..." if len(message) > 80 else message
            self.status_label.configure(text=display_message)

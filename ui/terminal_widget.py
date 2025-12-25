"""
Embedded Terminal Widget - Real shell execution within Command Center
Activated only when Terminal gem is selected (security)
"""
import os
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QLineEdit, QLabel
from PyQt6.QtCore import QProcess, Qt, pyqtSignal
from PyQt6.QtGui import QFont, QTextCursor, QColor, QPalette

class TerminalWidget(QWidget):
    """Embedded terminal with real shell execution"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.command_history = []
        self.history_index = 0
        self.current_process = None
        
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Header
        header = QLabel("🖥️  Terminal Mode (Security: Commands execute directly)")
        header.setStyleSheet("""
            background-color: #1a1a1a;
            color: #ececf1;
            padding: 12px 20px;
            font-weight: bold;
            border-bottom: 1px solid #2a2a2a;
        """)
        layout.addWidget(header)
        
        # Output display
        self.output = QTextEdit()
        self.output.setReadOnly(True)
        self.output.setFont(QFont("Menlo, Monaco, Courier New", 13))
        self.output.setStyleSheet("""
            QTextEdit {
                background-color: #0d0d0d;
                color: #00ff00;
                border: none;
                padding: 15px;
                selection-background-color: #2a2a2a;
            }
        """)
        layout.addWidget(self.output)
        
        # Command input
        self.input = QLineEdit()
        self.input.setFont(QFont("Menlo, Monaco, Courier New", 13))
        self.input.setStyleSheet("""
            QLineEdit {
                background-color: #1a1a1a;
                color: #ececf1;
                border: none;
                border-top: 1px solid #2a2a2a;
                padding: 15px 20px;
            }
            QLineEdit:focus {
                background-color: #1e1e1e;
                border-top: 1px solid #5865f2;
            }
        """)
        self.input.setPlaceholderText("Enter command... (pwd, ls, python, etc.)")
        self.input.returnPressed.connect(self.execute_command)
        
        # Handle history navigation
        self.input.installEventFilter(self)
        
        layout.addWidget(self.input)
        
        # Show welcome message
        cwd = os.getcwd()
        self.append_output(f"Terminal Ready\nWorking Directory: {cwd}\n$ ", is_prompt=True)
    
    def eventFilter(self, obj, event):
        """Handle up/down arrows for command history"""
        if obj == self.input and event.type() == event.Type.KeyPress:
            if event.key() == Qt.Key.Key_Up:
                if self.command_history and self.history_index > 0:
                    self.history_index -= 1
                    self.input.setText(self.command_history[self.history_index])
                return True
            elif event.key() == Qt.Key.Key_Down:
                if self.command_history and self.history_index < len(self.command_history) - 1:
                    self.history_index += 1
                    self.input.setText(self.command_history[self.history_index])
                elif self.history_index == len(self.command_history) - 1:
                    self.history_index = len(self.command_history)
                    self.input.clear()
                return True
        return super().eventFilter(obj, event)
    
    def execute_command(self):
        """Execute shell command using QProcess"""
        command = self.input.text().strip()
        if not command:
            return
        
        # Clear input first
        self.input.clear()
        
        # Execute via the programmatic method
        self.execute_command_programmatic(command)
    
    def execute_command_programmatic(self, command):
        """Execute command programmatically (can be called by AI agents)"""
        # Add to history
        self.command_history.append(command)
        self.history_index = len(self.command_history)
        
        # Display command
        self.append_output(command + "\n", is_command=True)
        
        # Security check for dangerous commands
        if self.is_dangerous_command(command):
            self.append_output(f"⚠️  Blocked: '{command}' requires confirmation\n", is_error=True)
            self.append_output("$ ", is_prompt=True)
            return
        
        # Execute command
        self.current_process = QProcess(self)
        self.current_process.setProcessChannelMode(QProcess.ProcessChannelMode.MergedChannels)
        self.current_process.readyReadStandardOutput.connect(self.handle_output)
        self.current_process.finished.connect(self.handle_finished)
        
        # Set working directory
        self.current_process.setWorkingDirectory(os.getcwd())
        
        # Execute in shell
        if os.name == 'nt':  # Windows
            self.current_process.start("cmd", ["/c", command])
        else:  # Mac/Linux
            self.current_process.start("zsh", ["-c", command])
    
    def handle_output(self):
        """Stream output from process"""
        if self.current_process:
            data = self.current_process.readAllStandardOutput()
            text = bytes(data).decode('utf-8', errors='replace')
            self.append_output(text)
    
    def handle_finished(self):
        """Process completed"""
        self.append_output("\n$ ", is_prompt=True)
        self.current_process = None
    
    def append_output(self, text, is_command=False, is_error=False, is_prompt=False):
        """Append text to output with styling"""
        cursor = self.output.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        
        # Set color based on type
        fmt = cursor.charFormat()
        if is_command:
            fmt.setForeground(QColor("#00ff00"))
        elif is_error:
            fmt.setForeground(QColor("#ff4444"))
        elif is_prompt:
            fmt.setForeground(QColor("#5865f2"))
        else:
            fmt.setForeground(QColor("#cccccc"))
        
        cursor.setCharFormat(fmt)
        cursor.insertText(text)
        self.output.setTextCursor(cursor)
        self.output.ensureCursorVisible()
    
    def is_dangerous_command(self, cmd):
        """Check if command is potentially dangerous"""
        dangerous = ['rm -rf', 'sudo', 'mkfs', 'dd ', ':(){', 'chmod -R 777']
        return any(danger in cmd for danger in dangerous)
    
    def clear_terminal(self):
        """Clear the output"""
        self.output.clear()
        cwd = os.getcwd()
        self.append_output(f"Terminal Cleared\nWorking Directory: {cwd}\n$ ", is_prompt=True)
    
    def stop_process(self):
        """Stop current running process"""
        if self.current_process and self.current_process.state() == QProcess.ProcessState.Running:
            self.current_process.kill()
            self.append_output("\n⚠️  Process terminated\n$ ", is_error=True)

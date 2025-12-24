"""
Terminal Widget - In-app command execution
"""
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QTextEdit, QLineEdit, QMessageBox)
from PyQt6.QtCore import Qt, pyqtSignal, QThread
from PyQt6.QtGui import QFont, QTextCursor
import os

class CommandWorker(QThread):
    """Background worker for command execution"""
    output = pyqtSignal(str)
    error = pyqtSignal(str)
    finished = pyqtSignal()
    
    def __init__(self, executor_agent, command):
        super().__init__()
        self.executor_agent = executor_agent
        self.command = command
    
    def run(self):
        try:
            # Execute command
            result = self.executor_agent.execute(self.command)
            self.output.emit(result)
        except Exception as e:
            self.error.emit(str(e))
        finally:
            self.finished.emit()

class TerminalWidget(QDialog):
    """Terminal widget for in-app command execution"""
    
    def __init__(self, executor_agent, parent=None):
        super().__init__(parent)
        self.executor_agent = executor_agent
        self.setWindowTitle("Python/Terminal")
        self.setFixedSize(900, 700)
        self.command_history = []
        self.history_index = -1
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Header
        header = QLabel("Terminal Execution")
        header.setFont(QFont(".AppleSystemUIFont", 18, QFont.Weight.Bold))
        header.setStyleSheet("color: #ffffff;")
        layout.addWidget(header)
        
        # Info label
        info = QLabel("Execute shell commands or Python scripts")
        info.setStyleSheet("color: #888888; font-size: 11px;")
        layout.addWidget(info)
        
        # Output display
        output_label = QLabel("Output:")
        output_label.setStyleSheet("color: #e0e0e0; font-size: 13px;")
        layout.addWidget(output_label)
        
        self.output_display = QTextEdit()
        self.output_display.setReadOnly(True)
        self.output_display.setFont(QFont("Menlo", 12))
        self.output_display.setPlaceholderText("Command output will appear here...")
        layout.addWidget(self.output_display)
        
        # Command input
        cmd_layout = QHBoxLayout()
        
        prompt_label = QLabel("$")
        prompt_label.setFont(QFont("Menlo", 13, QFont.Weight.Bold))
        prompt_label.setStyleSheet("color: #ffffff;")
        cmd_layout.addWidget(prompt_label)
        
        self.command_input = QLineEdit()
        self.command_input.setPlaceholderText("Enter command... (e.g., ls -la or python --version)")
        self.command_input.setFont(QFont("Menlo", 12))
        self.command_input.returnPressed.connect(self.execute_command)
        cmd_layout.addWidget(self.command_input)
        
        exec_btn = QPushButton("Run")
        exec_btn.setObjectName("Primary")
        exec_btn.clicked.connect(self.execute_command)
        cmd_layout.addWidget(exec_btn)
        
        layout.addLayout(cmd_layout)
        
        # Action buttons
        btn_layout = QHBoxLayout()
        
        clear_btn = QPushButton("Clear Output")
        clear_btn.clicked.connect(lambda: self.output_display.clear())
        
        copy_btn = QPushButton("Copy Output")
        copy_btn.clicked.connect(self.copy_output)
        
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        
        btn_layout.addWidget(clear_btn)
        btn_layout.addWidget(copy_btn)
        btn_layout.addStretch()
        btn_layout.addWidget(close_btn)
        
        layout.addLayout(btn_layout)
        
        # Styling
        self.setStyleSheet("""
            QDialog {
                background-color: #1e1e1e;
                color: #ffffff;
            }
            QLabel {
                color: #e0e0e0;
            }
            QTextEdit, QLineEdit {
                background-color: #0d0d0d;
                border: 1px solid #3d3d3d;
                border-radius: 5px;
                padding: 8px;
                color: #00ff00;
                font-family: "Menlo", monospace;
                font-size: 12px;
            }
            QTextEdit:focus, QLineEdit:focus {
                border-color: #5d5d5d;
            }
            QPushButton {
                background-color: #2d2d2d;
                color: #ffffff;
                border: 1px solid #3d3d3d;
                border-radius: 6px;
                padding: 10px 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #3d3d3d;
            }
            QPushButton#Primary {
                background-color: #ffffff;
                color: #000000;
                border: none;
            }
            QPushButton#Primary:hover {
                background-color: #e0e0e0;
            }
        """)
        
        # Set focus to input
        self.command_input.setFocus()
    
    def execute_command(self):
        command = self.command_input.text().strip()
        if not command:
            return
        
        # Add to history
        self.command_history.append(command)
        self.history_index = len(self.command_history)
        
        # Clear input
        self.command_input.clear()
        
        # Show command in output
        self.append_output(f"$ {command}\n", color="#00ff00")
        
        # Check if executor available
        if not self.executor_agent:
            self.append_output("Error: Executor agent not available\n", color="#ff0000")
            return
        
        # Start worker thread
        self.worker = CommandWorker(self.executor_agent, command)
        self.worker.output.connect(lambda out: self.append_output(out + "\n"))
        self.worker.error.connect(lambda err: self.append_output(f"Error: {err}\n", color="#ff0000"))
        self.worker.finished.connect(lambda: self.append_output("\n"))
        self.worker.start()
    
    def append_output(self, text, color=None):
        """Append text to output display with optional color"""
        cursor = self.output_display.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        
        if color:
            self.output_display.setTextColor(QColor(color))
        else:
            self.output_display.setTextColor(QColor("#00ff00"))
        
        self.output_display.insertPlainText(text)
        self.output_display.setTextCursor(cursor)
        self.output_display.ensureCursorVisible()
    
    def copy_output(self):
        text = self.output_display.toPlainText()
        if text:
            from PyQt6.QtWidgets import QApplication
            QApplication.clipboard().setText(text)
            QMessageBox.information(self, "Copied", "Output copied to clipboard!")
    
    def keyPressEvent(self, event):
        """Handle up/down arrows for command history"""
        if event.key() == Qt.Key.Key_Up and self.command_history:
            if self.history_index > 0:
                self.history_index -= 1
                self.command_input.setText(self.command_history[self.history_index])
        elif event.key() == Qt.Key.Key_Down and self.command_history:
            if self.history_index < len(self.command_history) - 1:
                self.history_index += 1
                self.command_input.setText(self.command_history[self.history_index])
            else:
                self.history_index = len(self.command_history)
                self.command_input.clear()
        else:
            super().keyPressEvent(event)

# Missing import fix
from PyQt6.QtGui import QColor

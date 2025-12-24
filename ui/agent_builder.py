"""
Agent Builder UI - Conversational Wizard for creating new agents
"""
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QTextEdit, QPushButton, QProgressBar,
                             QMessageBox, QCheckBox, QGroupBox)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont

class AgentBuilderDialog(QDialog):
    """
    Wizard-style dialog to create a new agent
    """
    agent_created = pyqtSignal(dict)  # Signal emitting the new agent data
    
    def __init__(self, architect_agent, local_llm, parent=None):
        super().__init__(parent)
        self.architect = architect_agent
        self.local_llm = local_llm
        self.setWindowTitle("Agent Builder 🏗️")
        self.setFixedSize(600, 700)
        self.setStyleSheet("""
            QDialog {
                background-color: #1e1e1e;
                color: #ffffff;
            }
            QLabel {
                color: #e0e0e0;
                font-size: 14px;
            }
            QLineEdit, QTextEdit {
                background-color: #2d2d2d;
                border: 1px solid #3d3d3d;
                border-radius: 5px;
                padding: 8px;
                color: #ffffff;
                font-size: 13px;
            }
            QLineEdit:focus, QTextEdit:focus {
                border-color: #5d5d5d;
            }
            QPushButton {
                background-color: #2d2d2d;
                color: #ffffff;
                border: 1px solid #3d3d3d;
                border-radius: 6px;
                padding: 10px;
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
            QGroupBox {
                border: 1px solid #3d3d3d;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
                font-weight: bold;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)
        
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Header
        header = QLabel("Create New Agent")
        header.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))
        layout.addWidget(header)
        
        desc = QLabel("Describe your agent and the Architect will build it for you.")
        desc.setStyleSheet("color: #aaaaaa; margin-bottom: 10px;")
        layout.addWidget(desc)
        
        # Form
        input_layout = QVBoxLayout()
        input_layout.setSpacing(10)
        
        # Name
        input_layout.addWidget(QLabel("Agent Name"))
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("e.g. Marketing Guru, Reddit Summarizer...")
        input_layout.addWidget(self.name_input)
        
        # Role/Description
        input_layout.addWidget(QLabel("Role & Goal"))
        self.role_input = QTextEdit()
        self.role_input.setPlaceholderText("Describe what this agent does. Be specific!\nExample: 'You are a marketing expert. Your goal is to fetch the latest trends from r/marketing and summarize them into a LinkedIn post format.'")
        self.role_input.setFixedHeight(120)
        input_layout.addWidget(self.role_input)
        
        # Capabilities
        caps_group = QGroupBox("Capabilities")
        caps_layout = QVBoxLayout()
        self.cap_search = QCheckBox("Web Search (DuckDuckGo)")
        self.cap_search.setChecked(True)
        self.cap_code = QCheckBox("Write Code")
        self.cap_files = QCheckBox("Read/Write Files")
        
        caps_layout.addWidget(self.cap_search)
        caps_layout.addWidget(self.cap_code)
        caps_layout.addWidget(self.cap_files)
        caps_group.setLayout(caps_layout)
        input_layout.addWidget(caps_group)
        
        layout.addLayout(input_layout)
        
        # Preview Area (Hidden initially)
        self.preview_area = QTextEdit()
        self.preview_area.setReadOnly(True)
        self.preview_area.setPlaceholderText("Generated code will appear here...")
        self.preview_area.hide()
        layout.addWidget(self.preview_area)
        
        # Progress Bar
        self.progress = QProgressBar()
        self.progress.setTextVisible(False)
        self.progress.hide()
        layout.addWidget(self.progress)
        
        # Buttons
        btn_layout = QHBoxLayout()
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.reject)
        
        self.build_btn = QPushButton("Build Agent ✨")
        self.build_btn.setObjectName("Primary")
        self.build_btn.clicked.connect(self.start_build)
        
        self.save_btn = QPushButton("Save & Register")
        self.save_btn.setObjectName("Primary")
        self.save_btn.clicked.connect(self.save_agent)
        self.save_btn.hide()
        
        btn_layout.addWidget(self.cancel_btn)
        btn_layout.addStretch()
        btn_layout.addWidget(self.build_btn)
        btn_layout.addWidget(self.save_btn)
        
        layout.addLayout(btn_layout)
        
        # Logic State
        self.generated_data = None
        
    def start_build(self):
        name = self.name_input.text().strip()
        role = self.role_input.toPlainText().strip()
        
        if not name or not role:
            QMessageBox.warning(self, "Missing Info", "Please provide a name and description.")
            return
            
        # UI Updates
        self.build_btn.setEnabled(False)
        self.progress.show()
        self.progress.setRange(0, 0) # Indeterminate
        
        # Gather caps
        caps = []
        if self.cap_search.isChecked(): caps.append("web_search")
        if self.cap_code.isChecked(): caps.append("coding")
        if self.cap_files.isChecked(): caps.append("file_ops")
        
        # Start Worker
        self.worker = BuilderWorker(self.architect, self.local_llm, name, role, caps)
        self.worker.finished.connect(self.on_build_complete)
        self.worker.error.connect(self.on_build_error)
        self.worker.start()
        
    def on_build_complete(self, agent_data):
        self.progress.hide()
        self.generated_data = agent_data
        
        # Show Code
        self.preview_area.show()
        self.preview_area.setText(agent_data["code"])
        
        # Update Buttons
        self.build_btn.hide()
        self.save_btn.show()
        
    def on_build_error(self, error):
        self.progress.hide()
        self.build_btn.setEnabled(True)
        QMessageBox.critical(self, "Build Error", f"Architect failed: {error}")

    def save_agent(self):
        if not self.generated_data:
            return
            
        try:
            # 1. Save file to disk
            from agents.agent_generator import AgentGenerator
            generator = AgentGenerator(self.architect, self.local_llm)
            success = generator.save_agent(self.generated_data)
            
            if success:
                QMessageBox.information(self, "Success", f"Agent '{self.generated_data['name']}' created successfully!")
                self.agent_created.emit(self.generated_data)
                self.accept()
            else:
                QMessageBox.critical(self, "Error", "Failed to write agent file.")
                
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))


class BuilderWorker(QThread):
    finished = pyqtSignal(dict)
    error = pyqtSignal(str)
    
    def __init__(self, architect, local_llm, name, role, caps):
        super().__init__()
        self.architect = architect
        self.local_llm = local_llm
        self.name = name
        self.role = role
        self.caps = caps
        
    def run(self):
        try:
            from agents.agent_generator import AgentGenerator
            generator = AgentGenerator(self.architect, self.local_llm)
            
            data = generator.generate_agent(self.name, self.role, self.caps)
            self.finished.emit(data)
            
        except Exception as e:
            self.error.emit(str(e))

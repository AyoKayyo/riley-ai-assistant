"""
Settings Dialog - Configuration UI for AI Command Center
"""
import os
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QTabWidget, QWidget, QLineEdit,
                             QComboBox, QGroupBox, QFormLayout, QCheckBox,
                             QMessageBox, QScrollArea)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from dotenv import load_dotenv, set_key

class SettingsDialog(QDialog):
    """
    Main settings dialog with tabbed interface
    """
    settings_changed = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
        self.setWindowTitle("Settings ⚙️")
        self.setFixedSize(700, 600)
        self.setup_ui()
        self.load_settings()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Tabs
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget::pane {
                border: none;
                background-color: #1e1e1e;
            }
            QTabBar::tab {
                background-color: #2d2d2d;
                color: #ffffff;
                padding: 12px 24px;
                border: none;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background-color: #1e1e1e;
                border-bottom: 2px solid #ffffff;
            }
            QTabBar::tab:hover {
                background-color: #3d3d3d;
            }
        """)
        
        # Add tabs
        self.tabs.addTab(self.create_models_tab(), "🤖 Models")
        self.tabs.addTab(self.create_api_keys_tab(), "🔑 API Keys")
        self.tabs.addTab(self.create_appearance_tab(), "🎨 Appearance")
        self.tabs.addTab(self.create_memory_tab(), "🧠 Memory")
        
        layout.addWidget(self.tabs)
        
        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.setContentsMargins(20, 10, 20, 20)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        
        save_btn = QPushButton("Save Settings")
        save_btn.setObjectName("Primary")
        save_btn.clicked.connect(self.save_settings)
        
        btn_layout.addStretch()
        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(save_btn)
        
        layout.addLayout(btn_layout)
        
        # Styling
        self.setStyleSheet("""
            QDialog {
                background-color: #1e1e1e;
                color: #ffffff;
            }
            QLabel {
                color: #e0e0e0;
                font-size: 13px;
            }
            QLineEdit, QComboBox {
                background-color: #2d2d2d;
                border: 1px solid #3d3d3d;
                border-radius: 5px;
                padding: 8px;
                color: #ffffff;
                font-size: 13px;
            }
            QLineEdit:focus, QComboBox:focus {
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
            QGroupBox {
                border: 1px solid #3d3d3d;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 15px;
                font-weight: bold;
                color: #ffffff;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
            QCheckBox {
                color: #ffffff;
                spacing: 8px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border: 2px solid #3d3d3d;
                border-radius: 3px;
                background-color: #2d2d2d;
            }
            QCheckBox::indicator:checked {
                background-color: #ffffff;
            }
        """)
        
    def create_models_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Companion Model
        companion_group = QGroupBox("Companion (Riley)")
        companion_layout = QFormLayout()
        self.companion_model = QComboBox()
        self.companion_model.addItems([
            "qwen2.5-coder:7b (Fast, Local)",
            "qwen2.5-coder:14b (Smart, Local)",
            "llama3.1:8b (Local)",
        ])
        companion_layout.addRow("Model:", self.companion_model)
        companion_group.setLayout(companion_layout)
        layout.addWidget(companion_group)
        
        # Other Agents
        agents_group = QGroupBox("Specialized Agents")
        agents_layout = QFormLayout()
        
        self.coder_model = QComboBox()
        self.coder_model.addItems([
            "qwen2.5-coder:7b",
            "qwen2.5-coder:14b",
        ])
        agents_layout.addRow("Coder:", self.coder_model)
        
        self.vision_model = QComboBox()
        self.vision_model.addItems([
            "llava:7b",
            "llava:13b",
        ])
        agents_layout.addRow("Vision:", self.vision_model)
        
        agents_group.setLayout(agents_layout)
        layout.addWidget(agents_group)
        
        # Architect
        architect_group = QGroupBox("Architect (Cloud)")
        architect_layout = QFormLayout()
        self.architect_model = QComboBox()
        self.architect_model.addItems([
            "gemini-2.0-flash-exp",
            "gemini-1.5-pro",
        ])
        architect_layout.addRow("Model:", self.architect_model)
        architect_group.setLayout(architect_layout)
        layout.addWidget(architect_group)
        
        layout.addStretch()
        return widget
        
    def create_api_keys_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Gemini API
        gemini_group = QGroupBox("Google Gemini")
        gemini_layout = QFormLayout()
        self.gemini_key = QLineEdit()
        self.gemini_key.setPlaceholderText("AIzaSy...")
        self.gemini_key.setEchoMode(QLineEdit.EchoMode.Password)
        gemini_layout.addRow("API Key:", self.gemini_key)
        
        show_gemini = QCheckBox("Show key")
        show_gemini.toggled.connect(lambda checked: self.gemini_key.setEchoMode(
            QLineEdit.EchoMode.Normal if checked else QLineEdit.EchoMode.Password
        ))
        gemini_layout.addRow("", show_gemini)
        gemini_group.setLayout(gemini_layout)
        layout.addWidget(gemini_group)
        
        # Note
        note = QLabel("🔒 Keys are stored in .env file (not encrypted)")
        note.setStyleSheet("color: #888888; font-size: 11px;")
        layout.addWidget(note)
        
        layout.addStretch()
        return widget
        
    def create_appearance_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Theme
        theme_group = QGroupBox("Theme")
        theme_layout = QFormLayout()
        self.theme_selector = QComboBox()
        self.theme_selector.addItems([
            "OLED Black (Current)",
            "Dark Gray",
            "Light (Coming Soon)",
        ])
        theme_layout.addRow("Color Scheme:", self.theme_selector)
        theme_group.setLayout(theme_layout)
        layout.addWidget(theme_group)
        
        # Font Size
        font_group = QGroupBox("Typography")
        font_layout = QFormLayout()
        self.font_size = QComboBox()
        self.font_size.addItems(["Small", "Medium (Current)", "Large"])
        font_layout.addRow("Font Size:", self.font_size)
        font_group.setLayout(font_layout)
        layout.addWidget(font_group)
        
        layout.addStretch()
        return widget
        
    def create_memory_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Retention
        retention_group = QGroupBox("Retention")
        retention_layout = QVBoxLayout()
        self.save_history = QCheckBox("Save conversation history")
        self.save_history.setChecked(True)
        retention_layout.addWidget(self.save_history)
        retention_group.setLayout(retention_layout)
        layout.addWidget(retention_group)
        
        # Cleanup
        cleanup_group = QGroupBox("Maintenance")
        cleanup_layout = QVBoxLayout()
        
        clear_btn = QPushButton("Clear All Memory")
        clear_btn.clicked.connect(self.clear_memory)
        cleanup_layout.addWidget(clear_btn)
        
        cleanup_group.setLayout(cleanup_layout)
        layout.addWidget(cleanup_group)
        
        layout.addStretch()
        return widget
        
    def load_settings(self):
        """Load current settings from .env"""
        load_dotenv(self.env_path)
        
        # Models
        companion = os.getenv("COMPANION_MODEL", "qwen2.5-coder:7b")
        if "14b" in companion:
            self.companion_model.setCurrentIndex(1)
        elif "llama" in companion:
            self.companion_model.setCurrentIndex(2)
        else:
            self.companion_model.setCurrentIndex(0)
            
        # API Keys
        gemini_key = os.getenv("GEMINI_API_KEY", "")
        if gemini_key and gemini_key != "your_gemini_pro_key_here":
            self.gemini_key.setText(gemini_key)
            
    def save_settings(self):
        """Save settings to .env and signal parent"""
        try:
            # Model mappings
            companion_models = [
                "qwen2.5-coder:7b",
                "qwen2.5-coder:14b",
                "llama3.1:8b",
            ]
            
            set_key(self.env_path, "COMPANION_MODEL", companion_models[self.companion_model.currentIndex()])
            
            # API Keys
            gemini = self.gemini_key.text().strip()
            if gemini:
                set_key(self.env_path, "GEMINI_API_KEY", gemini)
                
            QMessageBox.information(self, "Success", "Settings saved!\n\nRestart the app to apply changes.")
            self.settings_changed.emit()
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save settings:\n{e}")
            
    def clear_memory(self):
        """Clear memory database"""
        reply = QMessageBox.question(
            self, 
            "Clear Memory",
            "This will delete all conversation history and learned facts.\n\nAre you sure?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                # Clear memory files
                memory_dir = os.path.join(os.path.dirname(self.env_path), "memory")
                if os.path.exists(memory_dir):
                    for file in os.listdir(memory_dir):
                        if file.endswith('.json') or file.endswith('.db'):
                            os.remove(os.path.join(memory_dir, file))
                            
                QMessageBox.information(self, "Success", "Memory cleared!")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to clear memory:\n{e}")

"""
Agent Marketplace Dialog
Visual interface for adding external AI agents
"""
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QLineEdit, QScrollArea, QWidget,
                             QFrame, QMessageBox)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from agents.external_agents import AVAILABLE_AGENTS
from agents.memory import MemorySystem


class AgentCard(QFrame):
    """Card widget for each agent template"""
    selected = pyqtSignal(str)  # Emits agent_id when clicked
    
    def __init__(self, agent_id, agent_info):
        super().__init__()
        self.agent_id = agent_id
        self.agent_info = agent_info
        self.setup_ui()
    
    def setup_ui(self):
        """Create the agent card UI"""
        self.setFrameStyle(QFrame.Shape.StyledPanel)
        self.setStyleSheet("""
            AgentCard {
                background-color: #1f2937;
                border: 2px solid #374151;
                border-radius: 12px;
                padding: 16px;
            }
            AgentCard:hover {
                border-color: #60a5fa;
                background-color: #374151;
            }
        """)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(8)
        
        # Icon + Name
        header_layout = QHBoxLayout()
        icon_label = QLabel(self.agent_info['icon'])
        icon_label.setFont(QFont("SF Pro Text", 32))
        header_layout.addWidget(icon_label)
        
        name_label = QLabel(self.agent_info['name'])
        name_label.setFont(QFont("SF Pro Display", 16, QFont.Weight.Bold))
        name_label.setStyleSheet("color: #f3f4f6;")
        header_layout.addWidget(name_label)
        header_layout.addStretch()
        
        layout.addLayout(header_layout)
        
        # Description
        desc_label = QLabel(self.agent_info['description'])
        desc_label.setWordWrap(True)
        desc_label.setFont(QFont("SF Pro Text", 12))
        desc_label.setStyleSheet("color: #9ca3af;")
        layout.addWidget(desc_label)
        
        # Add button
        add_btn = QPushButton("+ Add Agent")
        add_btn.setFont(QFont("SF Pro Text", 11, QFont.Weight.Bold))
        add_btn.setStyleSheet("""
            QPushButton {
                background-color: #2563eb;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: #1d4ed8;
            }
        """)
        add_btn.clicked.connect(lambda: self.selected.emit(self.agent_id))
        layout.addWidget(add_btn)


class AddAgentDialog(QDialog):
    """Dialog for adding new AI agents"""
    agent_added = pyqtSignal(str, dict)  # Emits (agent_id, config)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("🤖 Add AI Agent")
        self.setModal(True)
        self.resize(700, 600)
        self.memory = MemorySystem()
        self.setup_ui()
    
    def setup_ui(self):
        """Create the marketplace UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(24, 24, 24, 24)
        
        # Header
        header = QLabel("🚀 Agent Marketplace")
        header.setFont(QFont("SF Pro Display", 24, QFont.Weight.Bold))
        header.setStyleSheet("color: #60a5fa;")
        layout.addWidget(header)
        
        subtitle = QLabel("Connect your AI subscriptions and custom agents")
        subtitle.setFont(QFont("SF Pro Text", 13))
        subtitle.setStyleSheet("color: #9ca3af; margin-bottom: 10px;")
        layout.addWidget(subtitle)
        
        # Scroll area for agent cards
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
        """)
        
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        scroll_layout.setSpacing(16)
        
        # Create cards for each agent
        for agent_id, agent_info in AVAILABLE_AGENTS.items():
            card = AgentCard(agent_id, agent_info)
            card.selected.connect(self.on_agent_selected)
            scroll_layout.addWidget(card)
        
        scroll_layout.addStretch()
        scroll.setWidget(scroll_widget)
        layout.addWidget(scroll)
        
        # Close button
        close_btn = QPushButton("Close")
        close_btn.setFont(QFont("SF Pro Text", 12))
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #374151;
                color: #e5e7eb;
                border: none;
                border-radius: 8px;
                padding: 10px 24px;
            }
            QPushButton:hover {
                background-color: #4b5563;
            }
        """)
        close_btn.clicked.connect(self.close)
        layout.addWidget(close_btn, alignment=Qt.AlignmentFlag.AlignRight)
        
        # Dark mode style
        self.setStyleSheet("""
            QDialog {
                background-color: #111827;
            }
        """)
    
    def on_agent_selected(self, agent_id):
        """Handle agent selection"""
        agent_info = AVAILABLE_AGENTS[agent_id]
        
        # Show configuration dialog
        config_dialog = AgentConfigDialog(agent_id, agent_info, self)
        if config_dialog.exec() == QDialog.DialogCode.Accepted:
            config = config_dialog.get_config()
            
            # Save to memory
            self.memory.register_external_service(f'agent_{agent_id}', config)
            
            # Emit signal
            self.agent_added.emit(agent_id, config)
            
            # Show success message
            QMessageBox.information(
                self,
                "Success",
                f"✅ {agent_info['name']} added successfully!\n\nYou can now use it in your conversations."
            )


class AgentConfigDialog(QDialog):
    """Dialog for configuring agent settings"""
    
    def __init__(self, agent_id, agent_info, parent=None):
        super().__init__(parent)
        self.agent_id = agent_id
        self.agent_info = agent_info
        self.fields = {}
        self.setup_ui()
    
    def setup_ui(self):
        """Create configuration UI"""
        self.setWindowTitle(f"Configure {self.agent_info['name']}")
        self.setModal(True)
        self.resize(500, 400)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(24, 24, 24, 24)
        
        # Header
        header_layout = QHBoxLayout()
        icon = QLabel(self.agent_info['icon'])
        icon.setFont(QFont("SF Pro Text", 40))
        header_layout.addWidget(icon)
        
        title = QLabel(self.agent_info['name'])
        title.setFont(QFont("SF Pro Display", 20, QFont.Weight.Bold))
        title.setStyleSheet("color: #f3f4f6;")
        header_layout.addWidget(title)
        header_layout.addStretch()
        
        layout.addLayout(header_layout)
        
        desc = QLabel(self.agent_info['description'])
        desc.setWordWrap(True)
        desc.setFont(QFont("SF Pro Text", 12))
        desc.setStyleSheet("color: #9ca3af; margin-bottom: 10px;")
        layout.addWidget(desc)
        
        # Configuration fields
        for field_name in self.agent_info['requires']:
            field_layout = QVBoxLayout()
            
            label = QLabel(field_name.replace('_', ' ').title())
            label.setFont(QFont("SF Pro Text", 12, QFont.Weight.Bold))
            label.setStyleSheet("color: #e5e7eb;")
            field_layout.addWidget(label)
            
            field = QLineEdit()
            field.setPlaceholderText(f"Enter your {field_name}")
            field.setFont(QFont("SF Mono", 11))
            
            # Special handling for API keys
            if 'key' in field_name.lower():
                field.setEchoMode(QLineEdit.EchoMode.Password)
                
                # Check if key exists in env
                env_key = self.agent_info.get('env_key')
                if env_key:
                    import os
                    existing_key = os.getenv(env_key)
                    if existing_key:
                        field.setText(existing_key)
                        field.setPlaceholderText("✓ Found in .env")
            
            field.setStyleSheet("""
                QLineEdit {
                    background-color: #1f2937;
                    border: 2px solid #374151;
                    border-radius: 8px;
                    padding: 10px;
                    color: #f3f4f6;
                }
                QLineEdit:focus {
                    border-color: #60a5fa;
                }
            """)
            
            field_layout.addWidget(field)
            layout.addLayout(field_layout)
            
            self.fields[field_name] = field
        
        layout.addStretch()
        
        # Buttons
        button_layout = QHBoxLayout()
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setFont(QFont("SF Pro Text", 12))
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #374151;
                color: #e5e7eb;
                border: none;
                border-radius: 8px;
                padding: 10px 24px;
            }
            QPushButton:hover {
                background-color: #4b5563;
            }
        """)
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        save_btn = QPushButton("Add Agent")
        save_btn.setFont(QFont("SF Pro Text", 12, QFont.Weight.Bold))
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #2563eb;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 24px;
            }
            QPushButton:hover {
                background-color: #1d4ed8;
            }
        """)
        save_btn.clicked.connect(self.accept)
        button_layout.addWidget(save_btn)
        
        layout.addLayout(button_layout)
        
        # Dark mode
        self.setStyleSheet("""
            QDialog {
                background-color: #111827;
            }
        """)
    
    def get_config(self):
        """Get the configuration from fields"""
        config = {}
        for field_name, field in self.fields.items():
            config[field_name] = field.text().strip()
        return config

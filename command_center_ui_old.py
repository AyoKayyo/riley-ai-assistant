#!/usr/bin/env python3
"""
AI Command Center - With Architect Mode Toggle
Press "Architect Mode" to switch to full system building
"""
import os
import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                              QTextEdit, QLineEdit, QPushButton, QSystemTrayIcon, QMenu,
                              QLabel, QFrame, QMessageBox, QCheckBox)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QIcon, QFont, QTextCursor, QPalette, QColor, QPixmap, QPainter, QTextOption
from dotenv import load_dotenv
from langchain_ollama import ChatOllama
from mcp.core import MCP
from agents.researcher import ResearchAgent
from agents.coder import CoderAgent
from agents.executor import ExecutorAgent
from agents.vision import VisionAgent
from agents.gemini_architect import GeminiArchitectAgent

load_dotenv()


class AgentThread(QThread):
    response_ready = pyqtSignal(str)
    agent_name = pyqtSignal(str)
    
    def __init__(self, agent, task, is_architect=False):
        super().__init__()
        self.agent = agent
        self.task = task
        self.is_architect = is_architect
    
    def run(self):
        try:
            if self.is_architect:
                result = self.agent.execute(self.task)
                self.agent_name.emit("Architect")
                self.response_ready.emit(result)
            else:
                result, agent = self.agent.process_task(self.task)
                self.agent_name.emit(agent)
                self.response_ready.emit(result)
        except Exception as e:
            self.response_ready.emit(f"Error: {str(e)}")


class CommandCenter(QMainWindow):
    """Command Center with Architect Mode"""
    
    def __init__(self):
        super().__init__()
        
        # Initialize MCP
        self.llm = ChatOllama(
            model=os.getenv("OLLAMA_MODEL", "qwen2.5-coder:7b"),
            base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
            temperature=0.7,
        )
        
        self.mcp = MCP(self.llm)
        self.mcp.register_agent('researcher', ResearchAgent(self.llm))
        self.mcp.register_agent('coder', CoderAgent(self.llm))
        self.mcp.register_agent('executor', ExecutorAgent(self.llm))
        self.mcp.register_agent('vision', VisionAgent(self.llm))
        
        # Architect agent
        self.architect = GeminiArchitectAgent()
        
        self.agent_thread = None
        self.current_agent = "Assistant"
        self.architect_mode = False  # Mode toggle
        
        self.setup_ui()
    
    def setup_ui(self):
        """ChatGPT UI"""
        self.setWindowTitle("AI Command Center")
        self.setGeometry(100, 100, 1400, 800)
        
        # Pure BLACK theme
        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, QColor(0, 0, 0))
        palette.setColor(QPalette.ColorRole.WindowText, QColor(255, 255, 255))
        palette.setColor(QPalette.ColorRole.Base, QColor(0, 0, 0))
        palette.setColor(QPalette.ColorRole.Text, QColor(255, 255, 255))
        self.setPalette(palette)
        
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # SIDEBAR
        sidebar = self.create_sidebar()
        main_layout.addWidget(sidebar)
        
        # CHAT
        chat_area = self.create_chat_area()
        main_layout.addWidget(chat_area, 1)
    
    def create_sidebar(self):
        """Sidebar with mode toggle"""
        sidebar = QFrame()
        sidebar.setFixedWidth(260)
        sidebar.setStyleSheet("""
            QFrame {
                background-color: #202123;
                border-right: 1px solid #2a2b32;
            }
        """)
        
        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(6)
        
        # ARCHITECT MODE TOGGLE
        self.architect_toggle = QPushButton("⚡ Architect Mode: OFF")
        self.architect_toggle.setCheckable(True)
        self.architect_toggle.setFont(QFont(".AppleSystemUIFont", 13, QFont.Weight.Bold))
        self.architect_toggle.setStyleSheet("""
            QPushButton {
                background-color: #2a2b32;
                color: #8e8ea0;
                border: 2px solid #565869;
                border-radius: 8px;
                padding: 14px;
                text-align: center;
            }
            QPushButton:checked {
                background-color: rgb(25, 195, 125, 0.2);
                color: #19c37d;
                border-color: #19c37d;
            }
            QPushButton:hover {
                background-color: #3a3b42;
            }
        """)
        self.architect_toggle.clicked.connect(self.toggle_architect_mode)
        layout.addWidget(self.architect_toggle)
        
        # MODE INDICATOR
        self.mode_label = QLabel("🤖 Assistant Mode: Local agents, quick tasks")
        self.mode_label.setFont(QFont(".AppleSystemUIFont", 10))
        self.mode_label.setWordWrap(True)
        self.mode_label.setStyleSheet("""
            color: #8e8ea0;
            padding: 8px;
            background-color: #2a2b32;
            border-radius: 22px;
        """)
        layout.addWidget(self.mode_label)
        
        layout.addSpacing(8)
        
        # NEW CHAT BUTTON
        new_chat_btn = QPushButton("+ New chat")
        new_chat_btn.setFont(QFont(".AppleSystemUIFont", 13))
        new_chat_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #ffffff;
                border: 1px solid #565869;
                border-radius: 22px;
                padding: 12px;
                text-align: left;
            }
            QPushButton:hover {
                background-color: #2a2b32;
            }
        """)
        new_chat_btn.clicked.connect(self.new_chat)
        layout.addWidget(new_chat_btn)
        
        # NEW AGENT BUTTON
        new_agent_btn = QPushButton("+ New agent")
        new_agent_btn.setFont(QFont(".AppleSystemUIFont", 13))
        new_agent_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #19c37d;
                border: 1px solid #19c37d;
                border-radius: 22px;
                padding: 12px;
                text-align: left;
            }
            QPushButton:hover {
                background-color: rgba(25, 195, 125, 0.1);
            }
        """)
        new_agent_btn.clicked.connect(self.build_agent)
        layout.addWidget(new_agent_btn)
        
        # FEATURES
        layout.addSpacing(8)
        features_label = QLabel("Features")
        features_label.setFont(QFont(".AppleSystemUIFont", 10))
        features_label.setStyleSheet("color: #8e8ea0; padding: 4px;")
        layout.addWidget(features_label)
        
        for feature in ["Code Generator", "Research", "Python/Terminal", "Memory", "Settings"]:
            btn = QPushButton(feature)
            btn.setFont(QFont(".AppleSystemUIFont", 12))
            btn.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    color: #ffffff;
                    border: none;
                    border-radius: 22px;
                    padding: 8px 12px;
                    text-align: left;
                }
                QPushButton:hover {
                    background-color: #2a2b32;
                }
            """)
            layout.addWidget(btn)
        
        # SEPARATOR
        separator = QFrame()
        separator.setFixedHeight(1)
        separator.setStyleSheet("background-color: #2a2b32; margin: 8px 0;")
        layout.addWidget(separator)
        
        # PAST CHATS
        past_label = QLabel("Past chats")
        past_label.setFont(QFont(".AppleSystemUIFont", 10))
        past_label.setStyleSheet("color: #8e8ea0; padding: 4px;")
        layout.addWidget(past_label)
        
        past_chats = [
            "Built WordPress deployer",
            "Designed sentient assistant",
            "Created ChatGPT UI"
        ]
        
        for chat in past_chats:
            chat_btn = QPushButton(chat)
            chat_btn.setFont(QFont(".AppleSystemUIFont", 12))
            chat_btn.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    color: #ffffff;
                    border: none;
                    border-radius: 22px;
                    padding: 8px 12px;
                    text-align: left;
                }
                QPushButton:hover {
                    background-color: #2a2b32;
                }
            """)
            layout.addWidget(chat_btn)
        
        layout.addStretch()
        
        # AGENT INDICATOR
        self.agent_label = QLabel(f"◉ {self.current_agent}")
        self.agent_label.setFont(QFont(".AppleSystemUIFont", 11))
        self.agent_label.setStyleSheet("""
            color: #19c37d;
            padding: 10px;
            background-color: #2a2b32;
            border-radius: 22px;
        """)
        layout.addWidget(self.agent_label)
        
        return sidebar
    
    def create_chat_area(self):
        """Chat area"""
        chat_frame = QFrame()
        chat_frame.setStyleSheet("background-color: #000000;")
        
        layout = QVBoxLayout(chat_frame)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Messages
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.chat_display.setFont(QFont(".AppleSystemUIFont", 15))
        self.chat_display.setWordWrapMode(QTextOption.WrapMode.WordWrap)
        self.chat_display.setStyleSheet("""
            QTextEdit {
                background-color: #000000;
                border: none;
                padding: 20px;
                color: #ffffff;
            }
        """)
        layout.addWidget(self.chat_display)
        
        # Input
        input_container = QFrame()
        input_container.setStyleSheet("background-color: #000000; border-top: 1px solid #0a0a0a;")
        input_layout = QVBoxLayout(input_container)
        input_layout.setContentsMargins(0, 20, 0, 20)
        
        input_wrapper = QWidget()
        input_wrapper_layout = QHBoxLayout(input_wrapper)
        input_wrapper_layout.setContentsMargins(20, 0, 20, 0)
        
        input_field_container = QFrame()
        input_field_container.setStyleSheet("background-color: #1a1a1a; border-radius: 12px;")
        input_field_layout = QHBoxLayout(input_field_container)
        input_field_layout.setContentsMargins(16, 8, 8, 8)
        input_field_layout.setSpacing(8)
        
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Send a message...")
        self.input_field.setFont(QFont(".AppleSystemUIFont", 15))
        self.input_field.setStyleSheet("""
            QLineEdit {
                background-color: transparent;
                border: none;
                color: #ffffff;
                padding: 8px 0;
            }
        """)
        self.input_field.returnPressed.connect(self.send_message)
        input_field_layout.addWidget(self.input_field)
        
        send_btn = QPushButton("↑")
        send_btn.setFont(QFont(".AppleSystemUIFont", 20, QFont.Weight.Bold))
        send_btn.setFixedSize(40, 40)
        send_btn.setStyleSheet("""
            QPushButton {
                background-color: #19c37d;
                color: white;
                border: none;
                border-radius: 22px;
            }
            QPushButton:hover {
                background-color: #1a7f5a;
            }
        """)
        send_btn.clicked.connect(self.send_message)
        input_field_layout.addWidget(send_btn)
        
        input_wrapper_layout.addWidget(input_field_container)
        input_layout.addWidget(input_wrapper)
        
        self.footer = QLabel("AI Command Center - Assistant Mode")
        self.footer.setFont(QFont(".AppleSystemUIFont", 11))
        self.footer.setStyleSheet("color: #8e8ea0; padding: 8px;")
        self.footer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        input_layout.addWidget(self.footer)
        
        layout.addWidget(input_container)
        
        return chat_frame
    
    def toggle_architect_mode(self):
        """Toggle between Assistant and Architect mode"""
        self.architect_mode = self.architect_toggle.isChecked()
        
        if self.architect_mode:
            self.architect_toggle.setText("⚡ Architect Mode: ON")
            self.mode_label.setText("🏗️ Architect Mode: Full system building, strategic decisions")
            self.mode_label.setStyleSheet("""
                color: #19c37d;
                padding: 8px;
                background-color: rgba(25, 195, 125, 0.2);
                border-radius: 22px;
                border: 1px solid #19c37d;
            """)
            self.footer.setText("Architect Mode: Strategic system building with full authority")
            self.agent_label.setText("◉ Architect (Gemini)")
            self.agent_label.setStyleSheet("""
                color: #19c37d;
                padding: 10px;
                background-color: rgba(25, 195, 125, 0.2);
                border-radius: 22px;
                border: 1px solid #19c37d;
            """)
            # Notify assistant about mode change
            self.add_message("System", "🏗️ **Architect Mode Activated**\n\nYou now have full system building capabilities. I can help with complex architectures, multi-file projects, and strategic decisions.")
        else:
            self.architect_toggle.setText("⚡ Architect Mode: OFF")
            self.mode_label.setText("🤖 Assistant Mode: Local agents, quick tasks")
            self.mode_label.setStyleSheet("""
                color: #8e8ea0;
                padding: 8px;
                background-color: #2a2b32;
                border-radius: 22px;
            """)
            self.footer.setText("AI Command Center - Assistant Mode")
            self.agent_label.setText("◉ Assistant")
            self.agent_label.setStyleSheet("""
                color: #19c37d;
                padding: 10px;
                background-color: #2a2b32;
                border-radius: 22px;
            """)
            # Notify about mode change
            self.add_message("System", "🤖 **Assistant Mode Active**\n\nUsing local agents for quick tasks. Switch to Architect Mode for complex system building.")
    
    def add_message(self, sender, message):
        """Add message"""
        cursor = self.chat_display.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        
        clean_msg = message.replace('<', '&lt;').replace('>', '&gt;').replace('\n', '<br>')
        
        if sender == "You":
            cursor.insertHtml(f'''
                <div style="background-color: #000000; padding: 20px 0;">
                    <div style="max-width: 800px; margin: 0 auto; padding: 0 20px;">
                        <div style="color: #ffffff; font-weight: 600; margin-bottom: 8px;">You</div>
                        <div style="color: #ffffff; line-height: 1.6;">{clean_msg}</div>
                    </div>
                </div>
            ''')
        elif sender == "System":
            cursor.insertHtml(f'''
                <div style="background-color: #2a2b32; padding: 20px 0;">
                    <div style="max-width: 800px; margin: 0 auto; padding: 0 20px;">
                        <div style="color: #8e8ea0; font-weight: 600; margin-bottom: 8px;">System</div>
                        <div style="color: #ffffff; line-height: 1.6;">{clean_msg}</div>
                    </div>
                </div>
            ''')
        else:
            cursor.insertHtml(f'''
                <div style="background-color: #0a0a0a; padding: 20px 0;">
                    <div style="max-width: 800px; margin: 0 auto; padding: 0 20px;">
                        <div style="color: #19c37d; font-weight: 600; margin-bottom: 8px;">Assistant</div>
                        <div style="color: #ffffff; line-height: 1.6;">{clean_msg}</div>
                        <div style="margin-top: 12px;">
                            <span style="color: #8e8ea0; font-size: 20px; cursor: pointer;" title="Copy">⎘</span>
                        </div>
                    </div>
                </div>
            ''')
        
        self.chat_display.setTextCursor(cursor)
        self.chat_display.ensureCursorVisible()
    
    def send_message(self):
        message = self.input_field.text().strip()
        if not message:
            return
        
        self.add_message("You", message)
        self.input_field.clear()
        self.input_field.setEnabled(False)
        
        # Use Architect or MCP based on mode
        if self.architect_mode:
            self.agent_thread = AgentThread(self.architect, message, is_architect=True)
        else:
            self.agent_thread = AgentThread(self.mcp, message, is_architect=False)
        
        self.agent_thread.agent_name.connect(self.update_agent)
        self.agent_thread.response_ready.connect(self.handle_response)
        self.agent_thread.start()
    
    def update_agent(self, agent_name):
        self.current_agent = agent_name
        if not self.architect_mode:
            self.agent_label.setText(f"◉ {agent_name}")
    
    def handle_response(self, response):
        self.add_message("Assistant", response)
        self.input_field.setEnabled(True)
        self.input_field.setFocus()
    
    def new_chat(self):
        self.chat_display.clear()
    
    def build_agent(self):
        """Build new agent"""
        QMessageBox.information(self, "Build Agent", 
            "Agent builder coming soon!\nThis will let you create custom agents via conversation.")


class MenuBarApp:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.window = CommandCenter()
        
        self.tray_icon = QSystemTrayIcon(self.app)
        icon_path = os.path.join(os.path.dirname(__file__), 'assets', 'mcp_icon.png')
        if os.path.exists(icon_path):
            self.tray_icon.setIcon(QIcon(icon_path))
        else:
            pixmap = QPixmap(64, 64)
            pixmap.fill(Qt.GlobalColor.transparent)
            painter = QPainter(pixmap)
            painter.setFont(QFont("SF Pro Text", 40))
            painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, "💬")
            painter.end()
            self.tray_icon.setIcon(QIcon(pixmap))
        
        self.tray_icon.setToolTip("AI Command Center")
        
        menu = QMenu()
        show_action = menu.addAction("Show")
        show_action.triggered.connect(self.show_window)
        menu.addSeparator()
        quit_action = menu.addAction("Quit")
        quit_action.triggered.connect(self.app.quit)
        
        self.tray_icon.setContextMenu(menu)
        self.tray_icon.activated.connect(self.on_tray_activated)
        self.tray_icon.show()
    
    def show_window(self):
        self.window.show()
        self.window.raise_()
        self.window.activateWindow()
    
    def on_tray_activated(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            self.show_window()
    
    def run(self):
        self.show_window()
        return self.app.exec()


if __name__ == "__main__":
    app = MenuBarApp()
    sys.exit(app.run())

#!/usr/bin/env python3
"""
Simple Chat UI - Clean interface like this chat
Just messages, no labels, no emojis
"""
import os
import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                              QTextEdit, QLineEdit, QPushButton, QSystemTrayIcon, QMenu)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QIcon, QFont, QTextCursor, QPalette, QColor, QPixmap, QPainter
from dotenv import load_dotenv
from langchain_ollama import ChatOllama
from mcp.core import MCP
from agents.researcher import ResearchAgent
from agents.coder import CoderAgent
from agents.executor import ExecutorAgent
from agents.vision import VisionAgent

load_dotenv()


class AgentThread(QThread):
    """Background thread for agent"""
    response_ready = pyqtSignal(str)
    
    def __init__(self, mcp, task):
        super().__init__()
        self.mcp = mcp
        self.task = task
    
    def run(self):
        try:
            result, agent_name = self.mcp.process_task(self.task)
            self.response_ready.emit(result)
        except Exception as e:
            self.response_ready.emit(f"Error: {str(e)}")


class SimpleChatWindow(QMainWindow):
    """Clean, simple chat interface"""
    
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
        
        self.agent_thread = None
        
        # Setup UI
        self.setup_ui()
    
    def setup_ui(self):
        """Setup clean UI"""
        self.setWindowTitle("Chat")
        self.setGeometry(100, 100, 700, 600)
        
        # Dark mode
        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, QColor(30, 30, 30))
        palette.setColor(QPalette.ColorRole.WindowText, QColor(255, 255, 255))
        palette.setColor(QPalette.ColorRole.Base, QColor(40, 40, 40))
        palette.setColor(QPalette.ColorRole.Text, QColor(255, 255, 255))
        self.setPalette(palette)
        
        # Main widget
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)
        
        # Chat display
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.chat_display.setFont(QFont(".AppleSystemUIFont", 13))
        self.chat_display.setStyleSheet("""
            QTextEdit {
                background-color: #2a2a2a;
                border: none;
                border-radius: 8px;
                padding: 12px;
                color: #ffffff;
            }
        """)
        layout.addWidget(self.chat_display)
        
        # Input field
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Message...")
        self.input_field.setFont(QFont(".AppleSystemUIFont", 13))
        self.input_field.setStyleSheet("""
            QLineEdit {
                background-color: #3a3a3a;
                border: 1px solid #4a4a4a;
                border-radius: 20px;
                padding: 10px 16px;
                color: #ffffff;
            }
            QLineEdit:focus {
                border-color: #606060;
            }
        """)
        self.input_field.returnPressed.connect(self.send_message)
        layout.addWidget(self.input_field)
        
        self.setWindowFlags(Qt.WindowType.Window | Qt.WindowType.WindowStaysOnTopHint)
    
    def add_message(self, sender, message):
        """Add clean chat bubble"""
        cursor = self.chat_display.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        
        if sender == "You":
            # User - right aligned
            cursor.insertHtml(f'''
                <div style="text-align: right; margin: 6px 0;">
                    <span style="background-color: #3a3a3a; color: #ffffff; 
                                 padding: 8px 12px; border-radius: 16px; 
                                 display: inline-block; max-width: 70%;">
                        {message}
                    </span>
                </div>
            ''')
        else:
            # Assistant - left aligned
            cursor.insertHtml(f'''
                <div style="text-align: left; margin: 6px 0;">
                    <span style="background-color: #2a2a2a; color: #e5e7eb; 
                                 padding: 8px 12px; border-radius: 16px; 
                                 display: inline-block; max-width: 70%; 
                                 border: 1px solid #404040;">
                        {message.replace(chr(10), "<br>")}
                    </span>
                </div>
            ''')
        
        self.chat_display.setTextCursor(cursor)
        self.chat_display.ensureCursorVisible()
    
    def send_message(self):
        """Send user message"""
        message = self.input_field.text().strip()
        if not message:
            return
        
        # Add user message
        self.add_message("You", message)
        self.input_field.clear()
        self.input_field.setEnabled(False)
        
        # Start agent thread
        self.agent_thread = AgentThread(self.mcp, message)
        self.agent_thread.response_ready.connect(self.handle_response)
        self.agent_thread.start()
    
    def handle_response(self, response):
        """Handle agent response"""
        self.add_message("Assistant", response)
        self.input_field.setEnabled(True)
        self.input_field.setFocus()


class MenuBarApp:
    """Mac menu bar app"""
    
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.window = SimpleChatWindow()
        
        # System tray
        self.tray_icon = QSystemTrayIcon(self.app)
        
        # MCP icon
        icon_path = os.path.join(os.path.dirname(__file__), 'assets', 'mcp_icon.png')
        if os.path.exists(icon_path):
            self.tray_icon.setIcon(QIcon(icon_path))
        else:
            # Fallback emoji icon
            pixmap = QPixmap(64, 64)
            pixmap.fill(Qt.GlobalColor.transparent)
            painter = QPainter(pixmap)
            painter.setFont(QFont("SF Pro Text", 40))
            painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, "💬")
            painter.end()
            self.tray_icon.setIcon(QIcon(pixmap))
        
        self.tray_icon.setToolTip("AI Assistant")
        
        # Menu
        menu = QMenu()
        
        show_action = menu.addAction("Show Chat")
        show_action.triggered.connect(self.show_window)
        
        menu.addSeparator()
        
        quit_action = menu.addAction("Quit")
        quit_action.triggered.connect(self.quit_app)
        
        self.tray_icon.setContextMenu(menu)
        self.tray_icon.activated.connect(self.on_tray_icon_activated)
        self.tray_icon.show()
    
    def show_window(self):
        """Show chat window"""
        self.window.show()
        self.window.raise_()
        self.window.activateWindow()
    
    def on_tray_icon_activated(self, reason):
        """Handle tray icon click"""
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            self.show_window()
    
    def quit_app(self):
        """Quit application"""
        self.app.quit()
    
    def run(self):
        """Run the app"""
        return self.app.exec()


if __name__ == "__main__":
    app = MenuBarApp()
    sys.exit(app.run())

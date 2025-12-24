#!/usr/bin/env python3
"""
AI Command Center - Advanced Menu Bar App
Dark mode, file upload, screenshots, vision, memory - the works!
"""
import os
import sys
import base64
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QTextEdit, QLineEdit, QPushButton, QSystemTrayIcon, 
                             QMenu, QLabel, QFileDialog, QToolButton)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QSize
from PyQt6.QtGui import QIcon, QFont, QTextCursor, QPalette, QColor, QAction, QPixmap, QPainter
from dotenv import load_dotenv
from langchain_ollama import ChatOllama
from mcp.core import MCP
from agents.vision import VisionAgent
from agents.memory import MemorySystem
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from ui.agent_marketplace import AddAgentDialog
# Import existing agents to register with MCP
from agents.researcher import ResearchAgent
from agents.coder import CoderAgent
from agents.executor import ExecutorAgent
import pyautogui
from PIL import Image
from io import BytesIO

load_dotenv()


class AgentThread(QThread):
    """Background thread for running agent tasks"""
    response_ready = pyqtSignal(str)
    agent_type = pyqtSignal(str)
    
    def __init__(self, orchestrator, task, image_data=None):
        super().__init__()
        self.orchestrator = orchestrator
        self.task = task
        self.image_data = image_data
    
    def run(self):
        try:
            if self.image_data:
                # Vision task
                self.agent_type.emit("Vision")
                vision_agent = VisionAgent(self.orchestrator.llm)
                result = vision_agent.execute(self.task, image_data=self.image_data)
            else:
                # Regular task - SmartOrchestrator returns (result, agent_name)
                result, agent_name = self.orchestrator.process_task(self.task)
                self.agent_type.emit(agent_name)
            
            self.response_ready.emit(result)
        except Exception as e:
            self.response_ready.emit(f"❌ Error: {str(e)}")


class ChatWindow(QMainWindow):
    """Dark mode AI command center with vision and memory"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🚀 AI Command Center")
        self.setGeometry(100, 100, 700, 800)
        self.setWindowFlags(Qt.WindowType.Window | Qt.WindowType.WindowStaysOnTopHint)
        
        # Initialize systems
        self.llm = ChatOllama(
            model=os.getenv("OLLAMA_MODEL", "qwen2.5-coder:7b"),
            base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
            temperature=0.7,
        )
        # Initialize MCP
        self.mcp = MCP(self.llm)
        
        # Register core agents
        self.mcp.register_agent('researcher', ResearchAgent(self.llm))
        self.mcp.register_agent('coder', CoderAgent(self.llm))
        self.mcp.register_agent('executor', ExecutorAgent(self.llm))
        self.mcp.register_agent('vision', VisionAgent(self.llm))
        
        # For backward compatibility
        self.orchestrator = self.mcp
        self.memory = MemorySystem()
        self.agent_thread = None
        self.current_image = None
        
        # Setup UI
        self.setup_dark_ui()
    
    def setup_dark_ui(self):
        """Create beautiful dark mode UI"""
        # Dark mode palette
        dark_palette = QPalette()
        dark_palette.setColor(QPalette.ColorRole.Window, QColor(30, 30, 30))  # gray-900
        dark_palette.setColor(QPalette.ColorRole.WindowText, QColor(255, 255, 255))  # gray-100
        dark_palette.setColor(QPalette.ColorRole.Base, QColor(40, 40, 40))  # gray-800
        dark_palette.setColor(QPalette.ColorRole.AlternateBase, QColor(30, 30, 30))
        dark_palette.setColor(QPalette.ColorRole.Text, QColor(255, 255, 255))
        dark_palette.setColor(QPalette.ColorRole.Button, QColor(50, 50, 50))  # gray-700
        dark_palette.setColor(QPalette.ColorRole.ButtonText, QColor(255, 255, 255))
        self.setPalette(dark_palette)
        
        # Central widget
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setSpacing(12)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Header
        header_layout = QHBoxLayout()
        header = QLabel("🚀 AI Command Center")
        header.setFont(QFont(".AppleSystemUIFont", 20, QFont.Weight.Bold))
        header.setStyleSheet("color: #a0a0a0; padding: 10px;")
        header_layout.addWidget(header)
        
        # Memory indicator
        memory_btn = QPushButton("💾")
        memory_btn.setToolTip("View Memory & Context")
        memory_btn.setFixedSize(40, 40)
        memory_btn.setStyleSheet("""
            QPushButton {
                background-color: #3a3a3a;
                border: 2px solid #5050 50;
                border-radius: 20px;
                font-size: 18px;
            }
            QPushButton:hover {
                background-color: #5050 50;
                border-color: #a0a0a0;
            }
        """)
        memory_btn.clicked.connect(self.show_memory)
        header_layout.addWidget(memory_btn)
        
        # MCP Status button with custom icon
        mcp_btn = QPushButton()
        mcp_btn.setToolTip("MCP Status & Controls")
        
        # Load MCP icon
        mcp_icon_path = os.path.join(os.path.dirname(__file__), 'assets', 'mcp_icon.png')
        if os.path.exists(mcp_icon_path):
            mcp_icon = QIcon(mcp_icon_path)
            mcp_btn.setIcon(mcp_icon)
            mcp_btn.setIconSize(QSize(32, 32))
        else:
            mcp_btn.setText("MCP")
        
        mcp_btn.setFixedSize(50, 40)
        mcp_btn.setStyleSheet("""
            QPushButton {
                background-color: #059669;
                border: 2px solid #10b981;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #047857;
                border-color: #34d399;
            }
        """)
        mcp_btn.clicked.connect(self.show_mcp_status)
        header_layout.addWidget(mcp_btn)
        
        # Add Agent button
        add_agent_btn = QPushButton("+ Add Agent")
        add_agent_btn.setToolTip("Add external AI agents (Claude, ChatGPT, etc.)")
        add_agent_btn.setFont(QFont(".AppleSystemUIFont", 11, QFont.Weight.Bold))
        add_agent_btn.setStyleSheet("""
            QPushButton {
                background-color: #5a5a5a;
                color: white;
                border: 1px solid #6a6a6a;
                border-radius: 6px;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: #6a6a6a;
            }
        """)
        add_agent_btn.clicked.connect(self.show_agent_marketplace)
        header_layout.addWidget(add_agent_btn)
        
        layout.addLayout(header_layout)
        
        # Status label
        self.status_label = QLabel("✅ Ready")
        self.status_label.setFont(QFont(".AppleSystemUIFont", 12))
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("color: #10b981; padding: 8px; background-color: #2a2a2a; border-radius: 6px;")
        layout.addWidget(self.status_label)
        
        # Toolbar for actions
        toolbar = QHBoxLayout()
        toolbar.setSpacing(8)
        
        # Upload button
        upload_btn = QPushButton("📁 Upload Image")
        upload_btn.setFont(QFont(".AppleSystemUIFont", 11))
        upload_btn.setStyleSheet("""
            QPushButton {
                background-color: #3a3a3a;
                color: #e5e7eb;
                border: 2px solid #5050 50;
                border-radius: 8px;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: #5050 50;
                border-color: #a0a0a0;
            }
        """)
        upload_btn.clicked.connect(self.upload_image)
        toolbar.addWidget(upload_btn)
        
        # Screenshot button
        screenshot_btn = QPushButton("📸 Screenshot")
        screenshot_btn.setFont(QFont(".AppleSystemUIFont", 11))
        screenshot_btn.setStyleSheet("""
            QPushButton {
                background-color: #3a3a3a;
                color: #e5e7eb;
                border: 2px solid #5050 50;
                border-radius: 8px;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: #5050 50;
                border-color: #a78bfa;
            }
        """)
        screenshot_btn.clicked.connect(self.take_screenshot)
        toolbar.addWidget(screenshot_btn)
        
        # Clear image button
        self.clear_img_btn = QPushButton("❌")
        self.clear_img_btn.setFixedSize(35, 35)
        self.clear_img_btn.setToolTip("Clear attached image")
        self.clear_img_btn.setVisible(False)
        self.clear_img_btn.setStyleSheet("""
            QPushButton {
                background-color: #991b1b;
                color: white;
                border: none;
                border-radius: 17px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #b91c1c;
            }
        """)
        self.clear_img_btn.clicked.connect(self.clear_image)
        toolbar.addWidget(self.clear_img_btn)
        
        toolbar.addStretch()
        layout.addLayout(toolbar)
        
        # Image preview label
        self.image_label = QLabel()
        self.image_label.setVisible(False)
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setStyleSheet("""
            QLabel {
                background-color: #2a2a2a;
                border: 2px solid #a0a0a0;
                border-radius: 8px;
                padding: 10px;
            }
        """)
        self.image_label.setMaximumHeight(150)
        layout.addWidget(self.image_label)
        
        # Chat display
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.chat_display.setFont(QFont("SF Mono", 12))
        self.chat_display.setStyleSheet("""
            QTextEdit {
                background-color: #2a2a2a;
                border: 2px solid #3a3a3a;
                border-radius: 12px;
                padding: 20px;
                color: #f3f4f6;
            }
        """)
        layout.addWidget(self.chat_display)
        
        # Input area
        input_layout = QHBoxLayout()
        input_layout.setSpacing(10)
        
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Ask anything, upload images, take screenshots...")
        self.input_field.setFont(QFont(".AppleSystemUIFont", 13))
        self.input_field.setStyleSheet("""
            QLineEdit {
                background-color: #3a3a3a;
                border: 2px solid #5050 50;
                border-radius: 10px;
                padding: 14px 18px;
                color: #f3f4f6;
            }
            QLineEdit:focus {
                border-color: #a0a0a0;
            }
        """)
        self.input_field.returnPressed.connect(self.send_message)
        input_layout.addWidget(self.input_field)
        
        self.send_button = QPushButton("Send")
        self.send_button.setFont(QFont(".AppleSystemUIFont", 13, QFont.Weight.Bold))
        self.send_button.setStyleSheet("""
            QPushButton {
                background-color: #5a5a5a;
                color: white;
                border: none;
                border-radius: 10px;
                padding: 14px 28px;
            }
            QPushButton:hover {
                background-color: #6a6a6a;
            }
            QPushButton:pressed {
                background-color: #1e40af;
            }
            QPushButton:disabled {
                background-color: #5050 50;
            }
        """)
        self.send_button.clicked.connect(self.send_message)
        input_layout.addWidget(self.send_button)
        
        layout.addLayout(input_layout)
        
        # Window style
        self.setStyleSheet("""
            QMainWindow {
                background-color: #111827;
            }
        """)
    
    def add_message(self, sender, message, color="#a0a0a0"):
        """Add message to chat"""
        cursor = self.chat_display.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        
        cursor.insertHtml(f'<p style="margin-top: 12px; margin-bottom: 6px;"><b style="color: {color}; font-size: 14px;">{sender}:</b></p>')
        cursor.insertHtml(f'<p style="margin-left: 12px; margin-bottom: 12px; color: #e5e7eb; line-height: 1.6;">{message.replace(chr(10), "<br>")}</p>')
        
        self.chat_display.setTextCursor(cursor)
        self.chat_display.ensureCursorVisible()
    
    def upload_image(self):
        """Upload an image file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Image", "", "Images (*.png *.jpg *.jpeg *.bmp *.gif)"
        )
        if file_path:
            self.load_image(file_path)
    
    def take_screenshot(self):
        """Take a screenshot"""
        self.hide()  # Hide window temporarily
        QApplication.processEvents()
        
        import time
        time.sleep(0.5)  # Give time for window to hide
        
        # Capture screenshot
        screenshot = pyautogui.screenshot()
        
        # Convert to bytes
        img_byte_arr = BytesIO()
        screenshot.save(img_byte_arr, format='PNG')
        self.current_image = img_byte_arr.getvalue()
        
        # Show preview
        pixmap = QPixmap()
        pixmap.loadFromData(self.current_image)
        scaled = pixmap.scaled(400, 200, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        self.image_label.setPixmap(scaled)
        self.image_label.setVisible(True)
        self.clear_img_btn.setVisible(True)
        
        self.show()
        self.add_message("📸 System", "Screenshot captured! Ask me anything about it.", "#a78bfa")
    
    def load_image(self, file_path):
        """Load image from file"""
        with open(file_path, 'rb') as f:
            self.current_image = f.read()
        
        # Show preview
        pixmap = QPixmap(file_path)
        scaled = pixmap.scaled(400, 200, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        self.image_label.setPixmap(scaled)
        self.image_label.setVisible(True)
        self.clear_img_btn.setVisible(True)
        
        self.add_message("📁 System", f"Image loaded: {os.path.basename(file_path)}", "#a0a0a0")
    
    def clear_image(self):
        """Clear attached image"""
        self.current_image = None
        self.image_label.setVisible(False)
        self.clear_img_btn.setVisible(False)
    
    def show_memory(self):
        """Show memory/context info"""
        recent = self.memory.get_recent_conversations(5)
        if not recent:
            msg = "No conversation history yet."
        else:
            msg = "Recent conversations:\n\n"
            for i, conv in enumerate(reversed(recent), 1):
                msg += f"{i}. {conv['user'][:60]}...\n"
        
        self.add_message("💾 Memory", msg, "#a78bfa")
    
    def show_mcp_status(self):
        """Show MCP status and controls"""
        status = self.mcp.get_status()
        
        msg = f"""🎯 MCP STATUS

Registered Agents: {len(status['registered_agents'])}
{chr(10).join(['  - ' + agent for agent in status['registered_agents']])}

Pending Approvals: {status['pending_approvals']}

Configuration:
  - Auto-notify: {status['config']['auto_notify_yellow']}
  - GUI Notifications: {status['config']['gui_notifications']}
  - iMessage: {'✅' if status['config']['imessage_notifications'] else '❌'}
  - Phone Configured: {'✅' if status['phone_configured'] else '❌'}

To configure:
  - "Set my phone number to +1234567890"
  - "Enable iMessage notifications"
  - "Show action history"
"""
        
        self.add_message("🎯 MCP", msg, "#10b981")
    
    def show_agent_marketplace(self):
        """Show agent marketplace dialog"""
        dialog = AddAgentDialog(self)
        dialog.agent_added.connect(self.on_agent_added)
        dialog.exec()
    
    def on_agent_added(self, agent_id, config):
        """Handle new agent added"""
        # Reload orchestrator's external agents
        self.orchestrator.reload_agents()
        
        # Show success message
        agents = self.orchestrator.list_available_agents()
        agent_list = "\n".join([f"- {name}: {desc}" for name, desc in agents.items()])
        
        self.add_message("🎉 System", 
                        f"Agent added successfully!\n\n" +
                        f"Available agents:\n{agent_list}", 
                        "#a78bfa")
    
    def send_message(self):
        """Send message and get agent response"""
        user_input = self.input_field.text().strip()
        if not user_input:
            return
        
        self.input_field.clear()
        
        # Show user message
        if self.current_image:
            self.add_message("👤 You (with image)", user_input, "#10b981")
        else:
            self.add_message("👤 You", user_input, "#10b981")
        
        # Disable input
        self.input_field.setEnabled(False)
        self.send_button.setEnabled(False)
        self.status_label.setText("🤔 Thinking...")
        self.status_label.setStyleSheet("color: #f59e0b; padding: 8px; background-color: #2a2a2a; border-radius: 6px;")
        
        # Start agent
        self.agent_thread = AgentThread(self.orchestrator, user_input, self.current_image)
        self.agent_thread.agent_type.connect(self.on_agent_type)
        self.agent_thread.response_ready.connect(self.on_response)
        self.agent_thread.start()
        
        # Store in memory
        self.last_user_message = user_input
    
    def on_agent_type(self, agent_type):
        """Update status with agent type"""
        self.status_label.setText(f"🎯 {agent_type} Agent...")
    
    def on_response(self, response):
        """Handle agent response"""
        self.add_message("🤖 Agent", response, "#a0a0a0")
        
        # Save to memory
        if hasattr(self, 'last_user_message'):
            self.memory.add_conversation(self.last_user_message, response, "auto")
        
        # Clear image after use
        if self.current_image:
            self.clear_image()
        
        # Re-enable
        self.input_field.setEnabled(True)
        self.send_button.setEnabled(True)
        self.input_field.setFocus()
        self.status_label.setText("✅ Ready")
        self.status_label.setStyleSheet("color: #10b981; padding: 8px; background-color: #2a2a2a; border-radius: 6px;")
    
    def toggle_visibility(self):
        """Toggle window"""
        if self.isVisible():
            self.hide()
        else:
            self.show()
            self.raise_()
            self.activateWindow()
            self.input_field.setFocus()


class MenuBarApp:
    """Menu bar app"""
    
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.app.setQuitOnLastWindowClosed(False)
        
        self.window = ChatWindow()
        
        # System tray with MCP icon
        self.tray_icon = QSystemTrayIcon(self.app)
        
        # Try to use MCP icon
        mcp_icon_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 
                                     'local-llm-agent', 'assets', 'mcp_icon.png')
        
        # Alternative path
        if not os.path.exists(mcp_icon_path):
            mcp_icon_path = '/Users/mark.kaough/.gemini/antigravity/scratch/local-llm-agent/assets/mcp_icon.png'
        
        if os.path.exists(mcp_icon_path):
            self.tray_icon.setIcon(QIcon(mcp_icon_path))
        else:
            # Fallback to emoji
            pixmap = QPixmap(64, 64)
            pixmap.fill(Qt.GlobalColor.transparent)
            painter = QPainter(pixmap)
            painter.setFont(QFont(".AppleSystemUIFont", 40))
            painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, "🚀")
            painter.end()
            self.tray_icon.setIcon(QIcon(pixmap))
        self.tray_icon.setToolTip("AI Command Center")
        
        menu = QMenu()
        
        show_action = QAction("Show Command Center", self.app)
        show_action.triggered.connect(self.window.show)
        menu.addAction(show_action)
        
        screenshot_action = QAction("📸 Take Screenshot", self.app)
        screenshot_action.triggered.connect(self.quick_screenshot)
        menu.addAction(screenshot_action)
        
        memory_action = QAction("💾 View Memory", self.app)
        memory_action.triggered.connect(self.window.show_memory)
        menu.addAction(memory_action)
        
        menu.addSeparator()
        
        quit_action = QAction("Quit", self.app)
        quit_action.triggered.connect(self.quit_app)
        menu.addAction(quit_action)
        
        self.tray_icon.setContextMenu(menu)
        self.tray_icon.activated.connect(self.on_tray_click)
        self.tray_icon.show()
        
        self.window.show()
    
    def on_tray_click(self, reason):
        """Handle tray click"""
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            self.window.toggle_visibility()
    
    def quick_screenshot(self):
        """Quick screenshot from menu"""
        self.window.show()
        self.window.take_screenshot()
    
    def quit_app(self):
        """Quit"""
        self.tray_icon.hide()
        self.app.quit()
    
    def run(self):
        """Run"""
        sys.exit(self.app.exec())


if __name__ == "__main__":
    app = MenuBarApp()
    app.run()

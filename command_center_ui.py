#!/usr/bin/env python3
"""
AI Command Center - STABLE FOUNDATION
Pure B&W, all features working, ready for companion
"""
import os
import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                              QTextEdit, QLineEdit, QPushButton, QSystemTrayIcon, QMenu,
                              QLabel, QFrame, QMessageBox, QFileDialog)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt6.QtGui import QIcon, QFont, QTextCursor, QPalette, QColor, QPixmap, QPainter, QTextOption
from dotenv import load_dotenv
from langchain_ollama import ChatOllama
from mcp.core import MCP
from agents.researcher import ResearchAgent
from agents.coder import CoderAgent
from agents.executor import ExecutorAgent
from agents.vision import VisionAgent
from agents.gemini_architect import GeminiArchitectAgent
from agents.companion import CompanionAgent
from agents.memory import MemorySystem

load_dotenv()


class AgentThread(QThread):
    response_ready = pyqtSignal(str)
    agent_name = pyqtSignal(str)
    
    def __init__(self, agent, task, is_architect=False, is_companion=False):
        super().__init__()
        self.agent = agent
        self.task = task
        self.is_architect = is_architect
        self.is_companion = is_companion
    
    def run(self):
        try:
            if self.is_companion:
                # Companion handles routing internally
                result = self.agent.process(self.task)
                self.agent_name.emit(self.agent.name)
                self.response_ready.emit(result)
            elif self.is_architect:
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
    """STABLE Foundation - Pure B&W"""
    
    def __init__(self):
        super().__init__()
        
        # MCP
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
        
        # Initialize memory system
        self.memory = MemorySystem()
        
        # Initialize Architect
        self.architect = GeminiArchitectAgent()
        
        # Initialize Companion (personality layer)
        self.companion = CompanionAgent(self.mcp, self.architect, self.memory)
        
        # Initialize Conversation Database
        from agents.conversation_db import ConversationDB
        self.conversation_db = ConversationDB()
        self.current_conversation_id = self.conversation_db.create_conversation()
        
        self.agent_thread = None
        self.current_agent = self.companion.name  # Use Companion's chosen name
        self.architect_mode = False
        self.first_launch = not self.memory.get("companion_name")  # Check if first time
        
        # FIX 1: Health check on startup
        self.check_ollama_connection()
        
        self.setup_ui()
    
    def setup_ui(self):
        self.setWindowTitle("AI Command Center")
        self.setGeometry(100, 100, 1400, 800)
        
        # GEMINI 2025 PREMIUM STYLESHEET
        self.setStyleSheet("""
            QMainWindow {
                background-color: #000000; /* True black OLED background */
            }
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QWidget#ThreadContainer {
                background-color: #000000; /* True black for thread */
            }
            QLineEdit {
                background-color: #1e1f20;
                border: none;
                border-radius: 28px;
                padding: 14px 24px;
                color: #ffffff;
                font-size: 15px;
                font-family: -apple-system, 'SF Pro Display', 'Helvetica Neue', sans-serif;
            }
        """)
        
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        sidebar = self.create_sidebar()
        main_layout.addWidget(sidebar)
        
        chat_area = self.create_chat_area()
        main_layout.addWidget(chat_area, 1)
    
    def create_sidebar(self):
        sidebar = QFrame()
        sidebar.setFixedWidth(260)
        sidebar.setStyleSheet("""
            QFrame {
                background-color: #0a0a0a;
                border-right: 1px solid #1a1a1a;
            }
        """)
        
        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(6)
        
        # ARCHITECT TOGGLE - WHITE WHEN ON
        self.architect_toggle = QPushButton("Architect Mode: OFF")
        self.architect_toggle.setCheckable(True)
        self.architect_toggle.setFont(QFont(".AppleSystemUIFont", 13, QFont.Weight.Bold))
        self.architect_toggle.setStyleSheet("""
            QPushButton {
                background-color: #1a1a1a;
                color: #808080;
                border: 2px solid #2a2a2a;
                border-radius: 8px;
                padding: 14px;
                text-align: center;
            }
            QPushButton:checked {
                background-color: #2a2a2a;
                color: #ffffff;
                border-color: #ffffff;
            }
            QPushButton:hover {
                background-color: #2a2a2a;
            }
        """)
        self.architect_toggle.clicked.connect(self.toggle_architect_mode)
        layout.addWidget(self.architect_toggle)
        
        layout.addSpacing(8)
        
        # NEW CHAT - WHITE
        new_chat_btn = QPushButton("+ New chat")
        new_chat_btn.setFont(QFont(".AppleSystemUIFont", 13))
        new_chat_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #ffffff;
                border: 1px solid #2a2a2a;
                border-radius: 6px;
                padding: 12px;
                text-align: left;
            }
            QPushButton:hover {
                background-color: #1a1a1a;
            }
        """)
        new_chat_btn.clicked.connect(self.new_chat)
        layout.addWidget(new_chat_btn)
        
        # NEW AGENT - WHITE
        new_agent_btn = QPushButton("+ New agent")
        new_agent_btn.setFont(QFont(".AppleSystemUIFont", 13))
        new_agent_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #ffffff;
                border: 1px solid #2a2a2a;
                border-radius: 6px;
                padding: 12px;
                text-align: left;
            }
            QPushButton:hover {
                background-color: #1a1a1a;
            }
        """)
        new_agent_btn.clicked.connect(self.build_agent)
        layout.addWidget(new_agent_btn)
        
        # THE SQUAD (Riley's Agents)
        layout.addSpacing(8)
        squad_label = QLabel("The Squad")
        squad_label.setFont(QFont(".AppleSystemUIFont", 10))
        squad_label.setStyleSheet("color: #666666; padding: 4px;")
        layout.addWidget(squad_label)
        
        features = [
            ("Code Generator", self.open_code_generator),
            ("Research", self.open_research),
            ("Python/Terminal", self.open_terminal),
            ("Memory", self.open_memory),
            ("Settings", self.open_settings)
        ]
        
        # SYSTEM HEARTBEAT
        layout.addSpacing(20)
        heartbeat_label = QLabel(" System")
        heartbeat_label.setFont(QFont(".AppleSystemUIFont", 10))
        heartbeat_label.setStyleSheet("color: #666666; padding: 4px;")
        layout.addWidget(heartbeat_label)
        
        # Real-time stats labels
        self.stats_container = QWidget()
        stats_layout = QVBoxLayout(self.stats_container)
        stats_layout.setContentsMargins(12, 0, 0, 0)
        stats_layout.setSpacing(4)
        
        self.cpu_label = QLabel("CPU: ...")
        self.cpu_label.setStyleSheet("color: #808080; font-size: 11px;")
        self.ram_label = QLabel("Memory: ...")
        self.ram_label.setStyleSheet("color: #808080; font-size: 11px;")
        self.disk_label = QLabel("Disk: ...")
        self.disk_label.setStyleSheet("color: #808080; font-size: 11px;")
        
        stats_layout.addWidget(self.cpu_label)
        stats_layout.addWidget(self.ram_label)
        stats_layout.addWidget(self.disk_label)
        layout.addWidget(self.stats_container)
        
        # Start Heartbeat Timer
        self.heartbeat_timer = QTimer(self)
        self.heartbeat_timer.timeout.connect(self.update_heartbeat)
        self.heartbeat_timer.start(2000) # Check every 2 seconds
        
        for name, callback in features:
            btn = QPushButton(name)
            btn.setFont(QFont(".AppleSystemUIFont", 12))
            btn.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    color: #cccccc;
                    border: none;
                    border-radius: 6px;
                    padding: 8px 12px;
                    text-align: left;
                }
                QPushButton:hover {
                    background-color: #1a1a1a;
                    color: #ffffff;
                }
            """)
            btn.clicked.connect(callback)
            layout.addWidget(btn)
        
        # SEPARATOR
        separator = QFrame()
        separator.setFixedHeight(1)
        separator.setStyleSheet("background-color: #1a1a1a; margin: 8px 0;")
        layout.addWidget(separator)
        
        # PAST CHATS
        past_label = QLabel("Past chats")
        past_label.setFont(QFont(".AppleSystemUIFont", 10))
        past_label.setStyleSheet("color: #666666; padding: 4px;")
        layout.addWidget(past_label)
        
        for chat in ["Built WordPress deployer", "Designed assistant", "Created UI"]:
            chat_btn = QPushButton(chat)
            chat_btn.setFont(QFont(".AppleSystemUIFont", 12))
            chat_btn.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    color: #999999;
                    border: none;
                    border-radius: 6px;
                    padding: 8px 12px;
                    text-align: left;
                }
                QPushButton:hover {
                    background-color: #1a1a1a;
                }
            """)
            layout.addWidget(chat_btn)
        
        layout.addStretch()
        
        # AGENT INDICATOR - WHITE
        self.agent_label = QLabel(f"{self.current_agent}")
        self.agent_label.setFont(QFont(".AppleSystemUIFont", 11))
        self.agent_label.setStyleSheet("""
            color: #ffffff;
            padding: 10px;
            background-color: #1a1a1a;
            border-radius: 6px;
        """)
        layout.addWidget(self.agent_label)
        
        return sidebar
    
    def create_chat_area(self):
        chat_frame = QFrame()
        chat_frame.setStyleSheet("background-color: #000000;")
        
        layout = QVBoxLayout(chat_frame)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # MESSAGES - Use new ChatThread instead of QTextEdit
        from ui.chat_thread import ChatThread
        self.chat_display = ChatThread()
        layout.addWidget(self.chat_display)
        
        # INPUT AREA
        input_container = QFrame()
        input_container.setStyleSheet("background-color: #000000; border-top: 1px solid #1a1a1a;")
        input_layout = QVBoxLayout(input_container)
        input_layout.setContentsMargins(20, 20, 20, 20)
        
        input_row = QHBoxLayout()
        input_row.setSpacing(10)
        
        # ATTACHMENT BUTTON (+)
        attach_btn = QPushButton("+")
        attach_btn.setFont(QFont(".AppleSystemUIFont", 22))
        attach_btn.setFixedSize(45, 45)
        attach_btn.setStyleSheet("""
            QPushButton {
                background-color: #1a1a1a;
                color: #ffffff;
                border: none;
                border-radius: 22px;
            }
            QPushButton:hover {
                background-color: #2a2a2a;
            }
        """)
        attach_btn.clicked.connect(self.attach_file)
        input_row.addWidget(attach_btn)
        
        # TOOLS BUTTON (⋯)
        tools_btn = QPushButton("⋯")
        tools_btn.setFont(QFont(".AppleSystemUIFont", 22))
        tools_btn.setFixedSize(45, 45)
        tools_btn.setStyleSheet("""
            QPushButton {
                background-color: #1a1a1a;
                color: #ffffff;
                border: none;
                border-radius: 22px;
            }
            QPushButton:hover {
                background-color: #2a2a2a;
            }
        """)
        tools_btn.clicked.connect(self.open_tools_menu)
        input_row.addWidget(tools_btn)
        
        # INPUT FIELD
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Send a message...")
        self.input_field.setFont(QFont(".AppleSystemUIFont", 15))
        self.input_field.setMinimumHeight(45)
        self.input_field.setStyleSheet("""
            QLineEdit {
                background-color: #1a1a1a;
                border: 1px solid #2a2a2a;
                border-radius: 22px;
                padding: 0 20px;
                color: #ffffff;
            }
            QLineEdit:focus {
                border-color: #3a3a3a;
            }
        """)
        self.input_field.returnPressed.connect(self.send_message)
        input_row.addWidget(self.input_field, 1)
        
        # SEND BUTTON - PURE WHITE
        send_btn = QPushButton("↑")
        send_btn.setFont(QFont(".AppleSystemUIFont", 20, QFont.Weight.Bold))
        send_btn.setFixedSize(45, 45)
        send_btn.setStyleSheet("""
            QPushButton {
                background-color: #ffffff;
                color: #000000;
                border: none;
                border-radius: 22px;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
            }
        """)
        send_btn.clicked.connect(self.send_message)
        input_row.addWidget(send_btn)
        
        input_layout.addLayout(input_row)
        
        # FOOTER
        self.footer = QLabel("AI Command Center")
        self.footer.setFont(QFont(".AppleSystemUIFont", 10))
        self.footer.setStyleSheet("color: #666666; padding: 8px;")
        self.footer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        input_layout.addWidget(self.footer)
        
        layout.addWidget(input_container)
        
        return chat_frame
    
    def toggle_architect_mode(self):
        self.architect_mode = self.architect_toggle.isChecked()
        
        if self.architect_mode:
            self.architect_toggle.setText("Architect Mode: ON")
            self.footer.setText("Architect Mode Active")
            self.agent_label.setText("Architect")
            self.add_message("System", "Architect Mode activated")
        else:
            self.architect_toggle.setText("Architect Mode: OFF")
            self.footer.setText("AI Command Center")
            self.agent_label.setText("Assistant")
            self.add_message("System", "Assistant Mode active")
    
    def check_ollama_connection(self):
        """FIX 1: Verify Ollama is running on startup"""
        try:
            import requests
            response = requests.get(f"{os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')}/api/tags", timeout=2)
            if response.status_code != 200:
                QMessageBox.warning(self, "Ollama Not Connected", 
                    "Warning: Ollama is not responding.\n\nLocal agents may not work.\n\nPlease start Ollama and restart the app.")
        except:
            QMessageBox.warning(self, "Ollama Not Found", 
                "Warning: Cannot connect to Ollama.\n\nLocal agents will not work.\n\nPlease start Ollama at http://localhost:11434")
    
    def add_message(self, sender, message):
        # Use ChatThread's add_message method (no more HTML hacks!)
        is_user = (sender == "You")
        self.chat_display.add_message(message, is_user=is_user)
    
    def send_message(self):
        # FIX 4: Input validation
        message = self.input_field.text().strip()
        if not message:
            return
        
        # Prepend attachment context if exists
        full_message = message
        if hasattr(self, 'pending_attachments') and self.pending_attachments:
            context_parts = []
            for attachment in self.pending_attachments:
                context_parts.append(f"[Attached File: {attachment['filename']}]\n{attachment['content']}\n")
            
            full_message = "\n".join(context_parts) + f"\n\nUser Message: {message}"
            
            # Clear attachments after sending
            self.pending_attachments = []
            self.input_field.setPlaceholderText("Send a message...")
        
        message = self.input_field.text().strip()
        if not message:
            return

        # 1. UI: Display User Message immediately
        self.add_message("You", message)
        self.input_field.clear()
        
        # 2. LOGIC: Check Architect Mode Toggle
        # If ON, we wrap the prompt to force the Gemini Architect route
        if self.architect_mode:
            print("🏗️ ARCHITECT MODE ACTIVE: Routing to Gemini 1.5 Pro")
            # Visual cue for user
            self.current_ai_bubble = self.chat_display.add_message("🏗️ *Calling the Architect...*", is_user=False)
            full_prompt = f"[SYSTEM: ARCHITECT MODE ACTIVE. IGNORE LOCAL TOOLS. ROUTE THIS REQUEST TO GEMINI ARCHITECT IMMEDIATELY.]\n\n{message}"
        else:
            full_prompt = message
            self.current_ai_bubble = self.chat_display.add_message("...", is_user=False)

        # 3. DB: Save to history
        if self.conversation_db:
            self.conversation_db.add_message(self.current_conversation_id, "user", message)

        # 4. STREAM: Start the worker
        self.input_field.setEnabled(False)
        self.input_field.setPlaceholderText("Riley is thinking...")
        
        from ui.stream_worker import StreamWorker
        self.stream_worker = StreamWorker(self.companion, full_prompt)
        self.stream_worker.token_received.connect(self.update_streaming_response)
        self.stream_worker.finished.connect(self.finish_response)
        self.stream_worker.start()
        
        self.stream_worker.start()
    
    def on_backend_stream_finished(self, final_text):
        """Backend is done, tell animator to wrap up"""
        if self.typing_animator:
            self.typing_animator.stop_stream()
    
    def update_streaming_response(self, text):
        """Update AI bubble as chars are 'typed' by animator"""
        if self.current_ai_bubble:
            self.current_ai_bubble.update_typed_text(text)
            self.chat_display.scroll_to_bottom()
    
    def finish_response(self):
        """Animation complete"""
        self.input_field.setEnabled(True)
        self.input_field.setPlaceholderText("Send a message...")
        self.input_field.setFocus()
        self.current_ai_bubble = None
        self.typing_animator = None
    
    def handle_error(self, error_msg):
        """Handle streaming errors"""
        if self.current_ai_bubble:
            self.current_ai_bubble.update_text(f"Error: {error_msg}")
        self.input_field.setEnabled(True)

    def update_heartbeat(self):
        """Fetch system stats and update sidebar"""
        try:
            from agents.system_observer import SystemObserver
            observer = SystemObserver()
            stats = observer.get_system_status()
            
            # Update labels
            self.cpu_label.setText(f"CPU: {stats['cpu']['usage']}%")
            self.ram_label.setText(f"Memory: {stats['memory']['used_percent']}%")
            self.disk_label.setText(f"Disk: {stats['disk']['percent']}%")
            
            # Dynamic colors based on stress
            color = "#808080" # Default grey
            if stats['status'] == "STRESSED":
                color = "#ff4444" # Red alert
            elif stats['cpu']['usage'] > 50:
                color = "#ffbb33" # Orange warning
                
            self.cpu_label.setStyleSheet(f"color: {color}; font-size: 11px;")
            self.ram_label.setStyleSheet(f"color: {color}; font-size: 11px;")
            self.disk_label.setStyleSheet(f"color: {color}; font-size: 11px;")
            
        except Exception:
            self.cpu_label.setText("CPU: Offline")

    
    
    # OLD METHODS REMOVED - Now using streaming
    
    
    # FEATURE FUNCTIONS
    def new_chat(self):
        self.chat_display.clear()
    
    
    def build_agent(self):
        """Open the Agent Builder Wizard"""
        from ui.agent_builder import AgentBuilderDialog
        
        dialog = AgentBuilderDialog(self.architect, self.llm, self)
        dialog.agent_created.connect(self.on_agent_created)
        dialog.exec()
        
    def on_agent_created(self, agent_data):
        """Handle new agent creation - Hot Reload Logic"""
        name = agent_data["name"]
        filename = agent_data["filename"]
        tool_name = agent_data["tool_name"]
        class_name = agent_data["class_name"]
        
        try:
            # Dynamic Import
            import importlib.util
            spec = importlib.util.spec_from_file_location(f"agents.{tool_name}", agent_data["filepath"])
            module = importlib.util.module_from_spec(spec)
            sys.modules[f"agents.{tool_name}"] = module
            spec.loader.exec_module(module)
            
            # Instantiate
            AgentClass = getattr(module, class_name)
            new_agent_instance = AgentClass(self.llm)
            
            # Register with MCP
            self.mcp.register_agent(tool_name, new_agent_instance)
            
            # Update UI
            self.add_message("System", f"New Agent Built: {name}")
            self.add_message("System", f"Files created at `agents/{filename}`")
            self.agent_label.setText(f"{name} (Active)")
            
            # Refresh sidebar or tools if we had a dynamic list (future todo)
            
        except Exception as e:
            QMessageBox.critical(self, "Hot Reload Failed", 
                f"Agent created but could not load dynamically:\n{e}\n\nPlease restart the app.")
    
    
    def attach_file(self):
        """Handle file attachment with real processing"""
        from PyQt6.QtWidgets import QFileDialog
        
        file, _ = QFileDialog.getOpenFileName(
            self, 
            "Attach File",
            "",
            "All Supported (*.txt *.md *.py *.pdf *.png *.jpg);;Text Files (*.txt *.md *.py);;PDF Files (*.pdf);;Images (*.png *.jpg *.jpeg)"
        )
        
        if not file:
            return
            
        try:
            # Process the file
            from utils.file_handler import FileAttachmentHandler
            handler = FileAttachmentHandler(vision_agent=self.mcp.agents.get('vision'))
            
            self.add_message("System", "Processing file...")
            
            # Process in background to avoid UI freeze
            attachment_data = handler.process_file(file)
            
            # Format and display
            formatted = handler.format_attachment_message(attachment_data)
            self.add_message("You", formatted)
            
            # Store attachment content for next message context
            if not hasattr(self, 'pending_attachments'):
                self.pending_attachments = []
            self.pending_attachments.append(attachment_data)
            
            # Update placeholder to indicate attachment ready
            self.input_field.setPlaceholderText(f"File attached: {attachment_data['filename']} - Send message...")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to process file:\n{str(e)}")

    
    def open_tools_menu(self):
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background-color: #1a1a1a;
                color: #ffffff;
                border: 1px solid #333333;
            }
            QMenu::item {
                padding: 8px 20px;
            }
            QMenu::item:selected {
                background-color: #333333;
            }
        """)
        
        # Add registered agents to menu
        for agent_name in self.mcp.agents.keys():
            action = menu.addAction(agent_name.capitalize())
            # Connect action (requires partial to capture name)
            # For now just showing list
            
        menu.exec(QTextCursor.pos()) # Show at cursor position? No, show at button
        # Actually standard QMenu usage is simpler
    
    def open_code_generator(self):
        QMessageBox.information(self, "Code Generator", "Code generation tool")
    
    def open_research(self):
        QMessageBox.information(self, "Research", "Research tool")
    
    def open_terminal(self):
        QMessageBox.information(self, "Python/Terminal", "Terminal execution")
    
    def open_memory(self):
        # Dump memory stats to chat
        stats = self.memory.stats()
        self.add_message("System", f"Memory Status\nShort-term: {stats['short_term']} items\nLong-term: {stats['long_term']} vectors")
    
    
    def open_settings(self):
        """Open Settings Dialog"""
        from ui.settings_dialog import SettingsDialog
        
        dialog = SettingsDialog(self)
        dialog.settings_changed.connect(lambda: self.add_message("System", "Settings updated. Please restart to apply changes."))
        dialog.exec()


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

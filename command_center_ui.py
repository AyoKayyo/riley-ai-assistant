#!/usr/bin/env python3
"""
AI Command Center - The Riley Interface
"""
import sys
import os
from dotenv import load_dotenv
load_dotenv()

# Initialize crash logging FIRST
from utils.crash_logger import CrashLogger
crash_logger = CrashLogger()
print("✓ Crash logging enabled - Errors will be saved to riley_crash.log")

from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                              QHBoxLayout, QTextEdit, QLineEdit, QPushButton,
                              QLabel, QFrame, QMessageBox, QSplitter, QScrollArea,
                              QSystemTrayIcon, QMenu, QFileDialog)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt6.QtGui import QIcon, QFont, QTextCursor, QPalette, QColor, QPixmap, QPainter, QTextOption
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
        self.current_agent = self.companion.name
        self.architect_mode = False
        self.first_launch = not self.memory.get("companion_name")
        self.current_gem = "Riley"  # Track active gem
        
        # Health check on startup
        self.check_ollama_connection()
        
        self.setup_ui()
    
    # === GEMINI SIDEBAR METHODS ===
    
    def new_chat(self):
        """Create a new conversation (for current gem/agent)"""
        current_agent = getattr(self, 'current_gem', 'Riley')
        self.current_conversation_id = self.conversation_db.create_conversation(agent_name=current_agent)
        self.chat_display.clear()
        self.load_recent_chats()  # Refresh sidebar
        
    def switch_to_gem(self, agent_name):
        """Switch to a different agent/gem"""
        self.current_gem = agent_name
        
        # CRITICAL: Stop any active streaming before clearing display
        if hasattr(self, 'stream_worker') and self.stream_worker:
            try:
                self.stream_worker.stop()
                self.stream_worker = None
            except:
                pass
        
        if hasattr(self, 'typing_worker') and self.typing_worker:
            try:
                self.typing_worker.stop()
                self.typing_worker = None
            except:
                pass
        
        # Highlight active gem
        for name, btn in self.gem_buttons.items():
            if name == agent_name:
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: #2a2a2a;
                        color: #ffffff;
                        border: none;
                        border-radius: 6px;
                        padding: 8px 12px;
                        text-align: left;
                    }
                """)
            else:
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
        
        # Create new chat for this agent
        self.new_chat()
        
    def load_recent_chats(self):
        """Load recent conversations from database into sidebar"""
        # Clear existing chat buttons
        while self.chats_layout.count():
            child = self.chats_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        # Get recent conversations
        conversations = self.conversation_db.get_recent_conversations(limit=15)
        
        for conv in conversations:
            chat_btn = QPushButton(conv['title'])
            chat_btn.setFont(QFont(".AppleSystemUIFont", 11))
            chat_btn.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    color: #999999;
                    border: none;
                    border-radius: 6px;
                    padding: 6px 10px;
                    text-align: left;
                }
                QPushButton:hover {
                    background-color: #1a1a1a;
                    color: #ffffff;
                }
            """)
            chat_btn.clicked.connect(lambda checked, conv_id=conv['id']: self.load_conversation(conv_id))
            self.chats_layout.addWidget(chat_btn)
    
    def filter_chats(self, search_text):
        """Filter visible chats based on search text"""
        search_lower = search_text.lower()
        
        for i in range(self.chats_layout.count()):
            widget = self.chats_layout.itemAt(i).widget()
            if widget and isinstance(widget, QPushButton):
                button_text = widget.text().lower()
                widget.setVisible(search_lower in button_text)
    
    def load_conversation(self, conversation_id):
        """Load a past conversation into the chat display"""
        self.current_conversation_id = conversation_id
        self.chat_display.clear()
        
        messages = self.conversation_db.get_conversation_messages(conversation_id)
        for msg in messages:
            is_user = msg['role'] == 'user'
            self.chat_display.add_message(msg['content'], is_user=is_user)
    
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
        
        # === GEMINI-STYLE SIDEBAR ===
        
        # 1. SEARCH BAR
        search_input = QLineEdit()
        search_input.setPlaceholderText("🔍 Search for chats")
        search_input.setStyleSheet("""
            QLineEdit {
                background-color: #1a1a1a;
                color: #ffffff;
                border: 1px solid #2a2a2a;
                border-radius: 8px;
                padding: 10px;
                font-size: 13px;
            }
            QLineEdit:focus {
                border: 1px solid #3a3a3a;
            }
        """)
        search_input.textChanged.connect(self.filter_chats)
        layout.addWidget(search_input)
        layout.addSpacing(10)
        
        # 2. NEW CHAT BUTTON
        new_chat_btn = QPushButton("✏️  New chat")
        new_chat_btn.setFont(QFont(".AppleSystemUIFont", 13))
        new_chat_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #cccccc;
                border: 1px solid #2a2a2a;
                border-radius: 8px;
                padding: 10px;
                text-align: left;
            }
            QPushButton:hover {
                background-color: #1a1a1a;
                color: #ffffff;
            }
        """)
        new_chat_btn.clicked.connect(self.new_chat)
        layout.addWidget(new_chat_btn)
        layout.addSpacing(15)
        
        # 3. GEMS SECTION (Agents)
        gems_label = QLabel("Gems")
        gems_label.setFont(QFont(".AppleSystemUIFont", 10, QFont.Weight.Bold))
        gems_label.setStyleSheet("color: #666666; padding: 4px;")
        layout.addWidget(gems_label)
        
        # Store gem buttons for highlighting
        self.gem_buttons = {}
        
        gems = [
            ("Riley", "💎", "Riley"),
            ("Architect", "🏗️", "Architect"),
            ("Coder", "💻", "Coder"),
            ("Researcher", "🔍", "Researcher"),
            ("Terminal", "⚡", "Terminal")
        ]
        
        for name, icon, agent_name in gems:
            btn = QPushButton(f"{icon}  {name}")
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
            btn.clicked.connect(lambda checked, a=agent_name: self.switch_to_gem(a))
            self.gem_buttons[agent_name] = btn
            layout.addWidget(btn)
        
        layout.addSpacing(15)
        
        # 4. CHATS SECTION (History)
        chats_label = QLabel("Chats")
        chats_label.setFont(QFont(".AppleSystemUIFont", 10, QFont.Weight.Bold))
        chats_label.setStyleSheet("color: #666666; padding: 4px;")
        layout.addWidget(chats_label)
        
        # Chat history container (will be populated from database)
        self.chats_container = QWidget()
        self.chats_layout = QVBoxLayout(self.chats_container)
        self.chats_layout.setContentsMargins(0, 0, 0, 0)
        self.chats_layout.setSpacing(2)
        layout.addWidget(self.chats_container)
        
        # Load recent chats
        self.load_recent_chats()
        
        layout.addStretch()
        
        # 5. SETTINGS (Bottom)
        separator = QFrame()
        separator.setFixedHeight(1)
        separator.setStyleSheet("background-color: #1a1a1a; margin: 8px 0;")
        layout.addWidget(separator)
        
        settings_btn = QPushButton("⚙️  Settings & help")
        settings_btn.setFont(QFont(".AppleSystemUIFont", 12))
        settings_btn.setStyleSheet("""
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
        settings_btn.clicked.connect(self.open_settings)
        layout.addWidget(settings_btn)

        
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
        """Send message to the currently active gem's agent"""
        message = self.input_field.text().strip()
        if not message:
            return
        
        # 1. Display user message in current gem's chat
        self.chat_display.add_message(message, is_user=True)
        self.input_field.clear()
        
        # 2. Save to database with correct agent context
        if self.conversation_db:
            self.conversation_db.add_message(
                self.current_conversation_id, 
                "user", 
                message
            )
        
        # 3. Route based on active gem
        current_gem = getattr(self, 'current_gem', 'Riley')
        
        # Disable input while processing
        self.input_field.setEnabled(False)
        self.input_field.setPlaceholderText(f"{current_gem} is thinking...")
        
        if current_gem == "Riley":
            # Direct Riley chat - she handles orchestration
            self._send_to_riley(message)
            
        elif current_gem == "Architect":
            # Direct Architect access (Gemini)
            self._send_to_architect(message)
            
        elif current_gem == "Coder":
            # Direct Coder access
            self._send_to_coder(message)
            
        elif current_gem == "Researcher":
            # Direct Researcher access
            self._send_to_researcher(message)
            
        elif current_gem == "Terminal":
            # Direct Executor access
            self._send_to_executor(message)
        
        else:
            # Fallback to Riley
            self._send_to_riley(message)
    
    def _send_to_riley(self, message):
        """Send message to Riley (Companion) - she orchestrates"""
        self.current_ai_bubble = self.chat_display.add_message("...", is_user=False)
        
        from ui.stream_worker import StreamWorker
        self.stream_worker = StreamWorker(self.companion, message)
        self.stream_worker.token_received.connect(self.update_streaming_response)
        self.stream_worker.finished.connect(self.finish_response)
        self.stream_worker.start()
    
    def _send_to_architect(self, message):
        """Send message directly to Gemini Architect"""
        self.current_ai_bubble = self.chat_display.add_message("🏗️ Architect thinking...", is_user=False)
        
        # Use architect agent directly
        from ui.stream_worker import StreamWorker
        self.stream_worker = StreamWorker(self.architect, message)
        self.stream_worker.token_received.connect(self.update_streaming_response)
        self.stream_worker.finished.connect(self.finish_response)
        self.stream_worker.start()
    
    def _send_to_coder(self, message):
        """Send message directly to Coder agent"""
        self.current_ai_bubble = self.chat_display.add_message("💻 Coding...", is_user=False)
        
        try:
            # Get coder agent from MCP
            coder = self.mcp.agents.get('coder')
            if coder:
                response = coder.execute(message)
                self.current_ai_bubble.update_typed_text(response)
                self.finish_response()
            else:
                self.current_ai_bubble.update_typed_text("❌ Coder agent not available")
                self.finish_response()
        except Exception as e:
            self.current_ai_bubble.update_typed_text(f"❌ Error: {str(e)}")
            self.finish_response()
    
    def _send_to_researcher(self, message):
        """Send message directly to Researcher agent"""
        self.current_ai_bubble = self.chat_display.add_message("🔍 Researching...", is_user=False)
        
        try:
            researcher = self.mcp.agents.get('researcher')
            if researcher:
                response = researcher.execute(message)
                self.current_ai_bubble.update_typed_text(response)
                self.finish_response()
            else:
                self.current_ai_bubble.update_typed_text("❌ Researcher agent not available")
                self.finish_response()
        except Exception as e:
            self.current_ai_bubble.update_typed_text(f"❌ Error: {str(e)}")
            self.finish_response()
    
    def _send_to_executor(self, message):
        """Send message directly to Executor agent"""
        self.current_ai_bubble = self.chat_display.add_message("⚡ Executing...", is_user=False)
        
        try:
            executor = self.mcp.agents.get('executor')
            if executor:
                response = executor.execute(message)
                self.current_ai_bubble.update_typed_text(response)
                self.finish_response()
            else:
                self.current_ai_bubble.update_typed_text("❌ Executor agent not available")
                self.finish_response()
        except Exception as e:
            self.current_ai_bubble.update_typed_text(f"❌ Error: {str(e)}")
            self.finish_response()

    
    def on_backend_stream_finished(self, final_text):
        """Backend is done, tell animator to wrap up"""
        if self.typing_animator:
            self.typing_animator.stop_stream()
    
    def update_streaming_response(self, text):
        """Update AI bubble as chars are 'typed' by animator"""
        if self.current_ai_bubble:
            self.current_ai_bubble.update_typed_text(text)
            self.chat_display.scroll_to_bottom()
    
    def finish_response(self, final_text=None):
        """Called when agent response is complete"""
        # Save to database if we have text
        if final_text and self.conversation_db:
            self.conversation_db.add_message(
                self.current_conversation_id,
                "assistant",
                final_text
            )
        
        # Re-enable input
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

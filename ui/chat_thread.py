import sys
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, 
    QScrollArea, QSizePolicy, QToolButton, QApplication, QMenu
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QSize
from PyQt6.QtGui import QFont, QCursor, QIcon, QClipboard

# === CONFIGURATION ===
# The exact font stack used by premium AI interfaces
FONT_FAMILY = ".AppleSystemUIFont" if sys.platform == "darwin" else "Segoe UI"
FONT_SIZE = 15
LINE_HEIGHT = 1.5

class ActionMenuButton(QToolButton):
    """The 'Three Dots' button that appears on hover"""
    def __init__(self, text_content, parent=None):
        super().__init__(parent)
        self.text_content = text_content
        self.setText("⋮")
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setStyleSheet("""
            QToolButton {
                color: #666;
                background: transparent;
                border: none;
                font-size: 18px;
                padding: 4px;
                border-radius: 12px;
            }
            QToolButton:hover {
                background: #2a2a2a;
                color: #fff;
            }
        """)
        self.clicked.connect(self.show_menu)

    def show_menu(self):
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu { background-color: #1e1e1e; border: 1px solid #333; border-radius: 8px; }
            QMenu::item { padding: 8px 24px; color: #ddd; }
            QMenu::item:selected { background-color: #2a2a2a; }
        """)
        
        copy_action = menu.addAction("Copy Text")
        copy_action.triggered.connect(self.copy_to_clipboard)
        
        # Add more actions here (Regenerate, etc.)
        
        menu.exec(QCursor.pos())

    def copy_to_clipboard(self):
        QApplication.clipboard().setText(self.text_content)


class ChatBubble(QFrame):
    """A Single Message Component (User or AI)"""
    def __init__(self, text, is_user=False, parent=None):
        super().__init__(parent)
        self.is_user = is_user
        self.full_text = text
        self.current_text = ""
        self.typing_speed = 12 # Lower = Faster
        
        # Main Layout
        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 10, 20, 10)
        layout.setSpacing(15)
        
        # CONTENT AREA (No avatars - clean like Gemini)
        self.content = QLabel("")
        self.content.setFont(QFont(FONT_FAMILY, FONT_SIZE))
        self.content.setWordWrap(True)
        self.content.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self.content.setStyleSheet("color: #ececf1; padding-top: 5px;")
        
        # ACTION MENU (Create BEFORE calling update_display_text)
        self.action_menu = ActionMenuButton(text)
        if is_user:
            self.action_menu.hide()
        
        # NOW update the display text
        self.update_display_text(text if is_user else "")

        # LAYOUT ASSEMBLY - Clean and minimal
        # AI: Text -> Actions
        # User: Text (right-aligned)
        
        if is_user:
            layout.addStretch()
            layout.addWidget(self.content)
        else:
            layout.addWidget(self.content, 1) # 1 = Stretch to fill width
            layout.addWidget(self.action_menu, 0, Qt.AlignmentFlag.AlignTop)

    def update_display_text(self, text):
        """Updates text with HTML formatting for line height"""
        # We replace newlines with <br> and wrap in styling span
        formatted = text.replace("\n", "<br>")
        html = f"""
        <style>
            p {{ line-height: 150%; margin: 0; }}
        </style>
        <p>{formatted}</p>
        """
        self.content.setText(html)
        # Only update action menu for AI messages (not user messages)
        if hasattr(self, 'action_menu') and not self.is_user:
            self.action_menu.text_content = text

    def update_typed_text(self, new_chunk):
        """Called by streaming events to add text smoothly"""
        self.full_text = new_chunk  # Replace full text (not append)
        self.update_display_text(self.full_text)

    def start_typing_animation(self):
        """Visual effect for initial load"""
        self.timer = QTimer()
        self.timer.timeout.connect(self._animate_step)
        self.timer.start(self.typing_speed)

    def _animate_step(self):
        if len(self.current_text) < len(self.full_text):
            self.current_text += self.full_text[len(self.current_text)]
            self.update_display_text(self.current_text)
        else:
            self.timer.stop()


class ChatThread(QScrollArea):
    """The Main Chat Container replacing QTextEdit"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWidgetResizable(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setStyleSheet("""
            QScrollArea { 
                border: none; 
                background: transparent; 
            }
            QScrollBar:vertical {
                background: transparent;
                width: 6px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: rgba(255, 255, 255, 0.2);
                min-height: 20px;
                border-radius: 3px;
            }
            QScrollBar::handle:vertical:hover {
                background: rgba(255, 255, 255, 0.3);
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: none;
            }
        """)
        
        # Container widget for the bubbles
        self.container = QWidget()
        self.container.setStyleSheet("background: transparent;")
        self.layout = QVBoxLayout(self.container)
        self.layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.layout.setSpacing(0) # Google has no major gaps between bubbles
        self.layout.setContentsMargins(0, 0, 0, 40) # Bottom padding
        
        self.setWidget(self.container)

    def add_message(self, text, is_user=False):
        """Adds a bubble and auto-scrolls"""
        bubble = ChatBubble(text, is_user)
        self.layout.addWidget(bubble)
        
        # Force layout update to calculate height
        QApplication.processEvents()
        self.scroll_to_bottom()
        
        # Return bubble so we can update it later (for streaming)
        return bubble

    def scroll_to_bottom(self):
        """Smooth scroll to bottom"""
        scrollbar = self.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
        
    def clear(self):
        # Delete all bubbles
        while self.layout.count():
            item = self.layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

"""
ChatThread - FINAL Gemini 2025 Premium UI
Perfect fonts, spacing, line-height, and typography
"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QFrame, QScrollArea)
from PyQt6.QtCore import Qt


class MessageWidget(QFrame):
    """Individual message with premium Gemini typography"""
    
    def __init__(self, text, is_user):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        
        self.text_label = QLabel()
        self.text_label.setWordWrap(True)
        self.text_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        
        if is_user:
            # User Bubble: Grey layered effect, rounded
            self.text_label.setText(text)
            self.text_label.setObjectName("UserBubble")
            self.text_label.setStyleSheet("""
                QLabel#UserBubble {
                    background-color: #2b2d31;
                    color: #e3e3e3;
                    border-radius: 20px;
                    padding: 14px 22px;
                    font-family: -apple-system, 'SF Pro Display', 'Helvetica Neue', sans-serif;
                    font-size: 14px;
                    font-weight: 500;
                }
            """)
        else:
            # AI Response: HTML with line-height control (160%)
            html_text = f"<div style='line-height: 160%;'>{text}</div>"
            self.text_label.setText(html_text)
            self.text_label.setObjectName("AIBubble")
            self.text_label.setStyleSheet("""
                QLabel#AIBubble {
                    background-color: transparent;
                    color: #e3e3e3;
                    font-family: -apple-system, 'SF Pro Display', 'Helvetica Neue', sans-serif;
                    font-size: 15px;
                    font-weight: 400;
                    padding: 0px;
                }
            """)
            
        self.layout.addWidget(self.text_label)
        self.is_user = is_user

    def update_text(self, text):
        """Legacy update method"""
        self.update_typed_text(text)

    def update_typed_text(self, text):
        """Receives the growing string from the TypingWorker"""
        if self.is_user:
             self.text_label.setText(text)
        else:
            # High-end typography
            # Escaping assumes raw text is passed, but sometimes we might pass partial HTML
            # For this buffer system, we assume RAW TEXT is accumulated
            safe_text = text.replace('<', '&lt;').replace('>', '&gt;')
            
            # Convert newlines to breaks for HTML display
            safe_text = safe_text.replace('\n', '<br>')
            
            style = "line-height: 160%; font-family: -apple-system, 'SF Pro Display', 'Helvetica Neue', sans-serif; font-size: 15px;"
            html = f"<div style='{style}'>{safe_text}</div>"
            self.text_label.setText(html)


class ChatThread(QScrollArea):
    """
    Gemini 2025 Premium Chat Thread:
    - True black OLED background
    - Premium typography
    - Generous spacing
    - Perfect line-height
    """
    
    def __init__(self):
        super().__init__()
        self.setWidgetResizable(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        self.container = QWidget()
        self.container.setObjectName("ThreadContainer")
        self.thread_layout = QVBoxLayout(self.container)
        
        # CENTERED LAYOUT - Gemini style
        self.thread_layout.setContentsMargins(100, 30, 100, 30)  # Larger side margins to center content
        self.thread_layout.setSpacing(24)  # Tighter spacing
        self.thread_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter) # Center align the column
        
        self.setWidget(self.container)

    def add_message(self, text, is_user=True):
        """Add a message to the thread"""
        wrapper = QHBoxLayout()
        bubble = MessageWidget(text, is_user)
        bubble.setMaximumWidth(820)  # Gemini standard

        if is_user:
            wrapper.addStretch()  # Push to right
            wrapper.addWidget(bubble)
        else:
            wrapper.addWidget(bubble)
            wrapper.addStretch()  # Push to left
        
        self.thread_layout.addLayout(wrapper)
        
        # Auto-scroll to bottom
        self.verticalScrollBar().setValue(self.verticalScrollBar().maximum())
        
        return bubble

    def scroll_to_bottom(self):
        """Force scroll to bottom"""
        self.verticalScrollBar().setValue(self.verticalScrollBar().maximum())
    
    def clear(self):
        """Clear all messages"""
        while self.thread_layout.count():
            item = self.thread_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                while item.layout().count():
                    child = item.layout().takeAt(0)
                    if child.widget():
                        child.widget().deleteLater()

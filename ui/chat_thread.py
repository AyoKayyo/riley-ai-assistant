"""
ChatThread - Gemini 2025 Premium UI
Clean rebuild - no syntax errors
"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QFrame, QScrollArea, QPushButton, QApplication)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont


class MessageWidget(QFrame):
    """Individual message with copy button"""
    
    def __init__(self, text, is_user):
        super().__init__()
        self.original_text = text
        self.is_user = is_user
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)
        
        # Text label
        self.text_label = QLabel(text)
        self.text_label.setWordWrap(True)
        self.text_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self.text_label.setStyleSheet("""
            QLabel {
                color: #e3e3e3;
                font-size: 15px;
                padding: 0px;
            }
        """)
        layout.addWidget(self.text_label)
        
        if is_user:
            self.setStyleSheet("""
                QFrame {
                    background-color: #2d2d2d;
                    border-radius: 16px;
                    padding: 12px 16px;
                }
            """)
            self.setMaximumWidth(500)
    
    def update_text(self, text):
        """Update text content"""
        self.update_typed_text(text)

    def update_typed_text(self, text):
        """Update text for streaming"""
        self.original_text = text
        self.text_label.setText(text)

    def copy_to_clipboard(self):
        """Copy to clipboard"""
        QApplication.clipboard().setText(self.original_text)


class ChatThread(QScrollArea):
    """Premium chat thread"""
    
    def __init__(self):
        super().__init__()
        self.setWidgetResizable(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        self.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
        """)
        
        self.container = QWidget()
        self.container.setObjectName("ThreadContainer")
        self.layout = QVBoxLayout(self.container)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(8)
        self.layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        self.setWidget(self.container)

    def add_message(self, text, is_user=True):
        """Add a message to the thread"""
        wrapper = QHBoxLayout()
        wrapper.setContentsMargins(0, 0, 0, 0)
        wrapper.setSpacing(0)
        
        bubble = MessageWidget(text, is_user)
        
        if is_user:
            wrapper.addStretch()
            wrapper.addWidget(bubble)
        else:
            wrapper.addWidget(bubble)
            wrapper.addStretch()
        
        self.layout.addLayout(wrapper)
        
        # Auto-scroll
        QTimer.singleShot(50, self.scroll_to_bottom)
        
        return bubble

    def scroll_to_bottom(self):
        """Scroll to bottom"""
        self.verticalScrollBar().setValue(self.verticalScrollBar().maximum())
    
    def clear(self):
        """Clear all messages"""
        while self.layout.count():
            item = self.layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                while item.layout().count():
                    child = item.layout().takeAt(0)
                    if child.widget():
                        child.widget().deleteLater()

"""
ChatThread - FINAL Gemini 2025 Premium UI
Perfect fonts, spacing, line-height, and typography
"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QFrame, QScrollArea, QPushButton, QApplication)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont


class MessageWidget(QFrame):
    """Individual message with premium Gemini typography + copy button"""
    
    def __init__(self, text, is_user):
        super().__init__()
        self.original_text = text  # Store for copy functionality
        self.is_user = is_user
        
        # Main vertical layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(4)
        
        # Text content with copy button
        text_container = QHBoxLayout()
        text_container.setContentsMargins(0, 0, 0, 0)
        text_container.setSpacing(8)
        
        self.text_label = QLabel()
        self.text_label.setWordWrap(True)
        self.text_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        
        # TEAM A: Premium Typography with Line-Height
        if is_user:
            # User bubbles: clean and direct
            self.text_label.setText(text)
            self.text_label.setStyleSheet("""
                QLabel {
                    color: #ffffff;
                    font-family: 'Segoe UI', 'Inter', -apple-system, sans-serif;
                    font-size: 14px;
                    font-weight: 500;
                    padding: 0px;
                }
            """)
        else:
            # AI bubbles: premium line-height via HTML
            html_text = f"<div style='line-height: 160%; font-family: \"Segoe UI\", \"Inter\", -apple-system, sans-serif; font-size: 16px; color: #e3e3e3;'>{text}</div>"
            self.text_label.setText(html_text)
            self.text_label.setStyleSheet("""
                QLabel {
                    padding: 0px;
                }
            """)
        
        # Copy button (appears on hover)
        self.copy_btn = QPushButton("📋")
        self.copy_btn.setFixedSize(24, 24)
        self.copy_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.copy_btn.setVisible(False)  # Hidden by default
        self.copy_btn.clicked.connect(self.copy_to_clipboard)
        self.copy_btn.setStyleSheet("""
            QPushButton {
                background-color: #2b2d31;
                color: #ffffff;
                border: none;
                border-radius: 6px;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #3b3d41;
            }
        """)
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
    

    def update_text(self, text):
        """Legacy update method"""
        self.update_typed_text(text)

    def copy_to_clipboard(self):
        """Copy message text to clipboard"""
        QApplication.clipboard().setText(self.original_text)
    
    def enterEvent(self, event):
        """Show copy button on hover"""
        self.copy_btn.show()
        super().enterEvent(event)
    
    def leaveEvent(self, event):
        """Hide copy button when not hovering"""
        self.copy_btn.hide()
        super().leaveEvent(event)

    def update_typed_text(self, text):
        """Receives the growing string from the TypingWorker"""
        self.original_text = text  # Update for copy
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
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)  # HIDE SCROLLBAR
        
        # Remove scrollbar visual completely
        self.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollBar:vertical {
        """)
        
        self.container = QWidget()
        self.container.setObjectName("ThreadContainer")
        # TEAM A: Premium Layout - Centered with breathable gutters
        self.layout = QVBoxLayout(self.container)
        self.layout.setContentsMargins(60, 20, 60, 20)  # Gemini-style centered gutters
        self.layout.setSpacing(32)  # Clear vertical separation
        self.layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        self.setWidget(self.container)
        
        # TEAM A: Hide scrollbar completely for premium feel
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
    def add_message(self, text, is_user=True):
        """Add a new message to the thread"""
        wrapper = QHBoxLayout()
        wrapper.setContentsMargins(0, 0, 0, 0)
        wrapper.setSpacing(0)
        
        bubble = MessageWidget(text, is_user)
        bubble.setMaximumWidth(820)  # Gemini standard
        
        if is_user:
            wrapper.addStretch()
            wrapper.addWidget(bubble)
        else:
            wrapper.addWidget(bubble)
            wrapper.addStretch()
        
        self.layout.addLayout(wrapper)
        
        # TEAM A: Smooth delayed auto-scroll
        QTimer.singleShot(50, self.scroll_to_bottom)
        
        return bubble
    
    def scroll_to_bottom(self):
        """Smoothly scroll to the bottom"""
        scrollbar = self.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
    
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

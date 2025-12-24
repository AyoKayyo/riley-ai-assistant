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
        
        # Horizontal layout for text + copy button
        h_layout = QHBoxLayout()
        h_layout.setSpacing(8)
        
        self.text_label = QLabel()
        self.text_label.setWordWrap(True)
        self.text_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        h_layout.addWidget(self.text_label, 1)  # Stretch factor 1
        
        # Copy button (initially hidden, shows on hover)
        self.copy_btn = QPushButton("📋")
        self.copy_btn.setFixedSize(32, 32)
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
        self.copy_btn.clicked.connect(self.copy_to_clipboard)
        self.copy_btn.hide()  # Hidden by default
        h_layout.addWidget(self.copy_btn)
        
        main_layout.addLayout(h_layout)
        self.layout = main_layout  # Keep reference for compatibility
        
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
                width: 0px;  /* Hide scrollbar */
            }
        """)
        
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
        
        # Improved auto-scroll with delay to ensure layout is complete
        QTimer.singleShot(50, self.scroll_to_bottom)
        
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

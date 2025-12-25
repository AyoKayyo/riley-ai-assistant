from PyQt6.QtWidgets import QListWidget, QListWidgetItem, QWidget, QVBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import pyqtSignal, Qt, QSize
from PyQt6.QtGui import QFont, QColor, QBrush

class HistorySidebar(QWidget):
    # Signals to talk to Command Center
    conversation_selected = pyqtSignal(int)  # Sends the Integer ID
    new_chat_clicked = pyqtSignal()

    def __init__(self, db_manager, parent=None):
        super().__init__(parent)
        self.db = db_manager
        self.active_id = None
        
        # Main Layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        # 1. "New Chat" Button (Gemini Style)
        self.new_btn = QPushButton("＋ New Chat")
        self.new_btn.setStyleSheet("""
            QPushButton {
                background-color: #1a1a1a;
                color: #ececf1;
                border: 1px solid #2a2a2a;
                border-radius: 8px;
                padding: 12px;
                text-align: left;
                font-size: 13px;
                font-weight: bold;
            }
            QPushButton:hover { 
                background-color: #2b2d31; 
                border-color: #3a3a3a;
            }
        """)
        self.new_btn.clicked.connect(self.new_chat_clicked.emit)
        layout.addWidget(self.new_btn)

        # 2. Section Header
        label = QLabel("Recent")
        label.setStyleSheet("color: #8e8ea0; font-weight: bold; font-size: 11px; margin-top: 10px; margin-left: 4px;")
        layout.addWidget(label)

        # 3. The List (Replaces your ScrollArea + Layout)
        self.chat_list = QListWidget()
        self.chat_list.setVerticalScrollMode(QListWidget.ScrollMode.ScrollPerPixel)
        self.chat_list.setStyleSheet("""
            QListWidget {
                background-color: transparent;
                border: none;
                outline: none;
            }
            QListWidget::item {
                color: #ececf1;
                padding: 10px;
                border-radius: 6px;
                margin-bottom: 2px;
            }
            QListWidget::item:hover {
                background-color: #1a1a1a;
            }
            QListWidget::item:selected {
                background-color: #2a2a2a;
                color: #ffffff;
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
        self.chat_list.itemClicked.connect(self.on_item_click)
        layout.addWidget(self.chat_list)

        # Initial Load
        self.refresh_list()

    def refresh_list(self):
        """Reloads from YOUR existing DB method"""
        self.chat_list.clear()
        
        # Matches 'agents/conversation_db.py' return format
        conversations = self.db.get_recent_conversations(limit=20)
        
        for conv in conversations:
            # conv is a dictionary: {'id': 1, 'title': '...', ...}
            title = conv['title']
            conv_id = conv['id']
            
            item = QListWidgetItem(title)
            item.setData(Qt.ItemDataRole.UserRole, conv_id) # Store ID hidden
            item.setSizeHint(QSize(0, 40)) # Consistent height
            
            self.chat_list.addItem(item)
            
            # Re-select active chat if it exists
            if self.active_id == conv_id:
                item.setSelected(True)

    def on_item_click(self, item):
        conv_id = item.data(Qt.ItemDataRole.UserRole)
        self.active_id = conv_id
        self.conversation_selected.emit(conv_id)

    def set_active(self, conv_id):
        """Programmatically select a chat (e.g. after creating new)"""
        self.active_id = conv_id
        self.refresh_list()

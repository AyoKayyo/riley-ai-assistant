"""
Research Panel - Web search and analysis tool
"""
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QTextEdit, QLineEdit, QMessageBox,
                             QProgressBar, QGroupBox)
from PyQt6.QtCore import Qt, pyqtSignal, QThread
from PyQt6.QtGui import QFont

class ResearchWorker(QThread):
    """Background worker for research tasks"""
    finished = pyqtSignal(str)
    error = pyqtSignal(str)
    progress = pyqtSignal(str)
    
    def __init__(self, browser_agent, query, num_results=3):
        super().__init__()
        self.browser_agent = browser_agent
        self.query = query
        self.num_results = num_results
    
    def run(self):
        try:
            self.progress.emit("Searching web...")
            
            # Use browser agent's search function
            result = self.browser_agent.search_and_digest(self.query, num_results=self.num_results)
            
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))

class ResearchPanel(QDialog):
    """Research tool with web search and citation tracking"""
    
    def __init__(self, browser_agent, parent=None):
        super().__init__(parent)
        self.browser_agent = browser_agent
        self.setWindowTitle("Research Tool")
        self.setFixedSize(900, 700)
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Header
        header = QLabel("Research Tool")
        header.setFont(QFont(".AppleSystemUIFont", 18, QFont.Weight.Bold))
        header.setStyleSheet("color: #ffffff;")
        layout.addWidget(header)
        
        # Search input
        search_group = QGroupBox("Search Query")
        search_layout = QVBoxLayout()
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("What do you want to research?")
        self.search_input.returnPressed.connect(self.start_research)
        search_layout.addWidget(self.search_input)
        
        search_btn = QPushButton("Search")
        search_btn.setObjectName("Primary")
        search_btn.clicked.connect(self.start_research)
        search_layout.addWidget(search_btn)
        
        search_group.setLayout(search_layout)
        layout.addWidget(search_group)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setMaximum(0)  # Indeterminate
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # Status label
        self.status_label = QLabel("")
        self.status_label.setStyleSheet("color: #888888; font-size: 11px;")
        layout.addWidget(self.status_label)
        
        # Results display
        results_label = QLabel("Results:")
        results_label.setStyleSheet("color: #e0e0e0; font-size: 13px;")
        layout.addWidget(results_label)
        
        self.results_display = QTextEdit()
        self.results_display.setReadOnly(True)
        self.results_display.setFont(QFont(".AppleSystemUIFont", 12))
        layout.addWidget(self.results_display)
        
        # Action buttons
        btn_layout = QHBoxLayout()
        
        copy_btn = QPushButton("Copy Results")
        copy_btn.clicked.connect(self.copy_results)
        
        export_btn = QPushButton("Export as Markdown")
        export_btn.clicked.connect(self.export_markdown)
        
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        
        btn_layout.addWidget(copy_btn)
        btn_layout.addWidget(export_btn)
        btn_layout.addStretch()
        btn_layout.addWidget(close_btn)
        
        layout.addLayout(btn_layout)
        
        # Styling
        self.setStyleSheet("""
            QDialog {
                background-color: #1e1e1e;
                color: #ffffff;
            }
            QLabel {
                color: #e0e0e0;
            }
            QTextEdit, QLineEdit {
                background-color: #2d2d2d;
                border: 1px solid #3d3d3d;
                border-radius: 5px;
                padding: 8px;
                color: #ffffff;
                font-size: 13px;
            }
            QTextEdit:focus, QLineEdit:focus {
                border-color: #5d5d5d;
            }
            QPushButton {
                background-color: #2d2d2d;
                color: #ffffff;
                border: 1px solid #3d3d3d;
                border-radius: 6px;
                padding: 10px 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #3d3d3d;
            }
            QPushButton#Primary {
                background-color: #ffffff;
                color: #000000;
                border: none;
            }
            QPushButton#Primary:hover {
                background-color: #e0e0e0;
            }
            QGroupBox {
                border: 1px solid #3d3d3d;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 15px;
                font-weight: bold;
                color: #ffffff;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
            QProgressBar {
                border: 1px solid #3d3d3d;
                border-radius: 3px;
                background-color: #2d2d2d;
                height: 20px;
            }
            QProgressBar::chunk {
                background-color: #ffffff;
            }
        """)
    
    def start_research(self):
        query = self.search_input.text().strip()
        if not query:
            QMessageBox.warning(self, "Empty Query", "Please enter a search query.")
            return
        
        if not self.browser_agent:
            QMessageBox.critical(self, "Browser Unavailable", 
                               "Browser agent is not available. Cannot perform research.")
            return
        
        # Show loading state
        self.progress_bar.setVisible(True)
        self.status_label.setText("Searching...")
        self.results_display.setText("")
        
        # Start worker thread
        self.worker = ResearchWorker(self.browser_agent, query)
        self.worker.finished.connect(self.on_research_complete)
        self.worker.error.connect(self.on_error)
        self.worker.progress.connect(self.on_progress)
        self.worker.start()
    
    def on_progress(self, message):
        self.status_label.setText(message)
    
    def on_research_complete(self, results):
        self.progress_bar.setVisible(False)
        self.status_label.setText("Research complete!")
        self.results_display.setText(results)
    
    def on_error(self, error_msg):
        self.progress_bar.setVisible(False)
        self.status_label.setText("Error occurred")
        self.results_display.setText(f"Error during research:\n{error_msg}")
        QMessageBox.critical(self, "Research Error", error_msg)
    
    def copy_results(self):
        text = self.results_display.toPlainText()
        if text:
            from PyQt6.QtWidgets import QApplication
            QApplication.clipboard().setText(text)
            QMessageBox.information(self, "Copied", "Results copied to clipboard!")
    
    def export_markdown(self):
        text = self.results_display.toPlainText()
        if not text:
            QMessageBox.warning(self, "No Results", "No research results to export.")
            return
        
        from PyQt6.QtWidgets import QFileDialog
        file, _ = QFileDialog.getSaveFileName(
            self,
            "Export Research Results",
            "research_results.md",
            "Markdown Files (*.md);;All Files (*)"
        )
        
        if file:
            try:
                with open(file, 'w', encoding='utf-8') as f:
                    query = self.search_input.text()
                    f.write(f"# Research: {query}\n\n")
                    f.write(text)
                QMessageBox.information(self, "Exported", f"Results saved to:\n{file}")
            except Exception as e:
                QMessageBox.critical(self, "Export Error", f"Failed to export:\n{e}")

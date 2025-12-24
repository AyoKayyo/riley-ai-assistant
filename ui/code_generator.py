"""
Code Generator Dialog - Full implementation for generating standalone code files
"""
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QTextEdit, QComboBox, QLineEdit,
                             QMessageBox, QFileDialog, QGroupBox)
from PyQt6.QtCore import Qt, pyqtSignal, QThread
from PyQt6.QtGui import QFont, QSyntaxHighlighter, QTextCharFormat, QColor
import re

class PythonHighlighter(QSyntaxHighlighter):
    """Simple Python syntax highlighter"""
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Define highlighting rules
        self.highlighting_rules = []
        
        # Keywords
        keyword_format = QTextCharFormat()
        keyword_format.setForeground(QColor("#ff79c6"))  # Pink
        keywords = ['def', 'class', 'import', 'from', 'return', 'if', 'else', 'elif', 
                   'for', 'while', 'try', 'except', 'with', 'as', 'pass', 'break', 
                   'continue', 'lambda', 'yield', 'None', 'True', 'False']
        for word in keywords:
            pattern = f'\\b{word}\\b'
            self.highlighting_rules.append((re.compile(pattern), keyword_format))
        
        # Strings
        string_format = QTextCharFormat()
        string_format.setForeground(QColor("#f1fa8c"))  # Yellow
        self.highlighting_rules.append((re.compile(r'"[^"\\]*(\\.[^"\\]*)*"'), string_format))
        self.highlighting_rules.append((re.compile(r"'[^'\\]*(\\.[^'\\]*)*'"), string_format))
        
        # Comments
        comment_format = QTextCharFormat()
        comment_format.setForeground(QColor("#6272a4"))  # Gray
        self.highlighting_rules.append((re.compile(r'#[^\n]*'), comment_format))
    
    def highlightBlock(self, text):
        for pattern, format in self.highlighting_rules:
            for match in pattern.finditer(text):
                self.setFormat(match.start(), match.end() - match.start(), format)

class CodeGenWorker(QThread):
    """Background worker for code generation"""
    finished = pyqtSignal(str)
    error = pyqtSignal(str)
    
    def __init__(self, coder_agent, language, prompt):
        super().__init__()
        self.coder_agent = coder_agent
        self.language = language
        self.prompt = prompt
    
    def run(self):
        try:
            # Build full prompt
            full_prompt = f"Write {self.language} code for: {self.prompt}\n\nProvide ONLY the code, no explanations."
            
            # Generate code
            code = self.coder_agent.execute(full_prompt)
            
            # Clean markdown if present
            if '```' in code:
                code = re.sub(r'```[a-z]*\n', '', code)
                code = re.sub(r'```', '', code)
            
            self.finished.emit(code.strip())
        except Exception as e:
            self.error.emit(str(e))

class CodeGeneratorDialog(QDialog):
    """Code Generator Dialog with language selection and syntax highlighting"""
    
    def __init__(self, coder_agent, parent=None):
        super().__init__(parent)
        self.coder_agent = coder_agent
        self.setWindowTitle("Code Generator")
        self.setFixedSize(900, 700)
        self.generated_code = ""
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Header
        header = QLabel("Code Generator")
        header.setFont(QFont(".AppleSystemUIFont", 18, QFont.Weight.Bold))
        header.setStyleSheet("color: #ffffff;")
        layout.addWidget(header)
        
        # Language selection
        lang_group = QGroupBox("Language")
        lang_layout = QHBoxLayout()
        self.language_combo = QComboBox()
        self.language_combo.addItems([
            "Python", "JavaScript", "HTML", "CSS", 
            "Bash", "SQL", "JSON", "Markdown"
        ])
        lang_layout.addWidget(self.language_combo)
        lang_group.setLayout(lang_layout)
        layout.addWidget(lang_group)
        
        # Prompt input
        prompt_label = QLabel("What do you want to build?")
        prompt_label.setStyleSheet("color: #e0e0e0; font-size: 13px;")
        layout.addWidget(prompt_label)
        
        self.prompt_input = QTextEdit()
        self.prompt_input.setPlaceholderText("Example: Create a function that calculates fibonacci numbers")
        self.prompt_input.setMaximumHeight(100)
        layout.addWidget(self.prompt_input)
        
        # Generate button
        gen_btn = QPushButton("Generate Code")
        gen_btn.setObjectName("Primary")
        gen_btn.clicked.connect(self.generate_code)
        layout.addWidget(gen_btn)
        
        # Code preview
        preview_label = QLabel("Generated Code:")
        preview_label.setStyleSheet("color: #e0e0e0; font-size: 13px;")
        layout.addWidget(preview_label)
        
        self.code_preview = QTextEdit()
        self.code_preview.setReadOnly(True)
        self.code_preview.setFont(QFont("Menlo", 12))
        
        # Add syntax highlighter for Python
        self.highlighter = PythonHighlighter(self.code_preview.document())
        
        layout.addWidget(self.code_preview)
        
        # Action buttons
        btn_layout = QHBoxLayout()
        
        copy_btn = QPushButton("Copy to Clipboard")
        copy_btn.clicked.connect(self.copy_code)
        
        save_btn = QPushButton("Save to File")
        save_btn.clicked.connect(self.save_to_file)
        
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        
        btn_layout.addWidget(copy_btn)
        btn_layout.addWidget(save_btn)
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
            QTextEdit, QLineEdit, QComboBox {
                background-color: #2d2d2d;
                border: 1px solid #3d3d3d;
                border-radius: 5px;
                padding: 8px;
                color: #ffffff;
                font-size: 13px;
            }
            QTextEdit:focus, QLineEdit:focus, QComboBox:focus {
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
        """)
    
    def generate_code(self):
        prompt = self.prompt_input.toPlainText().strip()
        if not prompt:
            QMessageBox.warning(self, "Empty Prompt", "Please describe what you want to build.")
            return
        
        language = self.language_combo.currentText()
        
        # Show loading state
        self.code_preview.setText("Generating code...")
        
        # Start worker thread
        self.worker = CodeGenWorker(self.coder_agent, language, prompt)
        self.worker.finished.connect(self.on_code_generated)
        self.worker.error.connect(self.on_error)
        self.worker.start()
    
    def on_code_generated(self, code):
        self.generated_code = code
        self.code_preview.setText(code)
    
    def on_error(self, error_msg):
        self.code_preview.setText(f"Error generating code:\n{error_msg}")
        QMessageBox.critical(self, "Generation Error", error_msg)
    
    def copy_code(self):
        if self.generated_code:
            from PyQt6.QtWidgets import QApplication
            QApplication.clipboard().setText(self.generated_code)
            QMessageBox.information(self, "Copied", "Code copied to clipboard!")
    
    def save_to_file(self):
        if not self.generated_code:
            QMessageBox.warning(self, "No Code", "Generate code first before saving.")
            return
        
        # Suggest file extension based on language
        lang = self.language_combo.currentText().lower()
        ext_map = {
            "python": ".py", "javascript": ".js", "html": ".html",
            "css": ".css", "bash": ".sh", "sql": ".sql",
            "json": ".json", "markdown": ".md"
        }
        ext = ext_map.get(lang, ".txt")
        
        file, _ = QFileDialog.getSaveFileName(
            self,
            "Save Generated Code",
            f"generated_code{ext}",
            f"Code Files (*{ext});;All Files (*)"
        )
        
        if file:
            try:
                with open(file, 'w', encoding='utf-8') as f:
                    f.write(self.generated_code)
                QMessageBox.information(self, "Saved", f"Code saved to:\n{file}")
            except Exception as e:
                QMessageBox.critical(self, "Save Error", f"Failed to save file:\n{e}")

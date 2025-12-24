from PyQt6.QtCore import pyqtSignal, QTimer, QObject

class TypingWorker(QObject):
    """
    Frontend animator for text revealing.
    INSTANT MODE: No typing delay, immediate display for maximum speed.
    """
    char_typed = pyqtSignal(str)
    finished = pyqtSignal()

    def __init__(self, instant_mode=True):
        super().__init__()
        self.full_text = ""
        self.display_text = ""
        self.stream_active = True
        self.instant_mode = instant_mode
        
        if instant_mode:
            # INSTANT MODE: Update as fast as possible (1ms)
            self.timer = QTimer()
            self.timer.timeout.connect(self.process_instant)
            self.timer.start(1)
        else:
            # Classic typing mode (if ever needed)
            self.timer = QTimer()
            self.timer.timeout.connect(self.process_next_char)
            self.timer.start(10)

    def update_buffer(self, new_text):
        """Called whenever a new token arrives from the LLM"""
        self.full_text = new_text
        
        if not self.timer.isActive() and self.stream_active:
            self.timer.start(1 if self.instant_mode else 10)

    def process_instant(self):
        """INSTANT MODE: Display everything immediately"""
        if self.full_text != self.display_text:
            self.display_text = self.full_text
            self.char_typed.emit(self.display_text)
        elif not self.stream_active:
            self.timer.stop()
            self.finished.emit()

    def process_next_char(self):
        """Classic typing mode (legacy)"""
        diff = len(self.full_text) - len(self.display_text)
        
        if diff > 0:
            # Adaptive speed
            chunk_size = 1
            if diff > 50: chunk_size = 5
            elif diff > 20: chunk_size = 3
            elif diff > 10: chunk_size = 2
            
            next_chars = self.full_text[len(self.display_text) : len(self.display_text) + chunk_size]
            self.display_text += next_chars
            self.char_typed.emit(self.display_text)
            
        elif not self.stream_active and diff == 0:
            self.timer.stop()
            self.finished.emit()

    def stop_stream(self):
        """Called when LLM is done generating"""
        self.stream_active = False

"""
StreamWorker - Real-time token streaming from LLM
Shows responses letter-by-letter as they're generated
"""
from PyQt6.QtCore import QThread, pyqtSignal


class StreamWorker(QThread):
    """
    Worker thread for streaming LLM responses
    Emits tokens in real-time for live chat feel
    """
    
    token_received = pyqtSignal(str)  # Individual token
    finished = pyqtSignal(str)  # Complete response
    error = pyqtSignal(str)  # Error message
    
    def __init__(self, companion_agent, user_message, conversation_db=None, conversation_id=None):
        super().__init__()
        self.companion = companion_agent
        self.message = user_message
        self.full_response = ""
        self.conversation_db = conversation_db
        self.conversation_id = conversation_id
    
    def run(self):
        """Stream response from Companion"""
        try:
            # Build context from conversation history
            context = None
            if self.conversation_db and self.conversation_id:
                messages = self.conversation_db.get_conversation_messages(self.conversation_id)
                context = {'conversation_history': messages}
            
            # Stream with context
            for token in self.companion.stream_process(self.message, context):
                self.full_response += token
                self.token_received.emit(self.full_response)
            
        except StopIteration:
            # Normal end of stream
            pass
        except Exception as e:
            error_msg = f"Error: {str(e)}\n\n(Note: Check if Ollama is running or if Disk is full)"
            self.error.emit(error_msg)
            if not self.full_response:
                self.full_response = error_msg
        finally:
            # ALWAYS emit finished, even on error
            self.finished.emit(self.full_response)


class ArchitectStreamWorker(QThread):
    """
    Worker thread for streaming Architect responses
    (Gemini API doesn't stream same way, so we just run normally)
    """
    
    finished = pyqtSignal(str)
    error = pyqtSignal(str)
    
    def __init__(self, architect_agent, user_message):
        super().__init__()
        self.architect = architect_agent
        self.message = user_message
    
    def run(self):
        """Execute Architect (non-streaming for now)"""
        try:
            response = self.architect.execute(self.message)
            self.finished.emit(response)
        except Exception as e:
            error_msg = f"Architect Error: {str(e)}"
            self.error.emit(error_msg)
            self.finished.emit(error_msg)

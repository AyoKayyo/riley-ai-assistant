"""
Crash Logger - Captures exceptions and errors for debugging
"""
import sys
import traceback
from datetime import datetime
import os

class CrashLogger:
    def __init__(self, log_file="riley_crash.log"):
        self.log_file = log_file
        self.log_path = os.path.join(os.path.dirname(__file__), "..", log_file)
        
    def log_exception(self, exc_type, exc_value, exc_traceback):
        """Log an exception to file"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        error_msg = f"""
{'='*80}
CRASH REPORT - {timestamp}
{'='*80}

Exception Type: {exc_type.__name__}
Exception Value: {exc_value}

Traceback:
{''.join(traceback.format_tb(exc_traceback))}

Full Traceback:
{''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))}
{'='*80}

"""
        
        # Write to file
        with open(self.log_path, 'a') as f:
            f.write(error_msg)
        
        # Also print to console
        print(error_msg)
        
    def install(self):
        """Install as global exception handler"""
        sys.excepthook = self.log_exception

def setup_crash_logging():
    """Setup crash logging for the application"""
    logger = CrashLogger()
    logger.install()
    return logger

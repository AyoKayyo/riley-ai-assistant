"""
File Attachment Handler - Process PDFs, Images, and Text Files
"""
import os
import base64
from typing import Dict, Any

class FileAttachmentHandler:
    """
    Handles file attachment processing for the chat system
    """
    
    def __init__(self, vision_agent=None):
        self.vision_agent = vision_agent
        self.supported_extensions = {
            'text': ['.txt', '.md', '.py', '.js', '.html', '.css', '.json', '.yaml', '.yml'],
            'pdf': ['.pdf'],
            'image': ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp']
        }
        
    def process_file(self, filepath: str) -> Dict[str, Any]:
        """
        Process a file and extract its content
        
        Returns:
            {
                'type': 'text' | 'pdf' | 'image',
                'filename': str,
                'content': str,
                'size': int,
                'preview': str (optional)
            }
        """
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"File not found: {filepath}")
            
        filename = os.path.basename(filepath)
        ext = os.path.splitext(filename)[1].lower()
        size = os.path.getsize(filepath)
        
        # Determine file type
        file_type = self._get_file_type(ext)
        
        if file_type == 'text':
            return self._process_text_file(filepath, filename, size)
        elif file_type == 'pdf':
            return self._process_pdf_file(filepath, filename, size)
        elif file_type == 'image':
            return self._process_image_file(filepath, filename, size)
        else:
            raise ValueError(f"Unsupported file type: {ext}")
            
    def _get_file_type(self, ext: str) -> str:
        """Determine file type from extension"""
        for file_type, extensions in self.supported_extensions.items():
            if ext in extensions:
                return file_type
        return 'unknown'
        
    def _process_text_file(self, filepath: str, filename: str, size: int) -> Dict[str, Any]:
        """Read text file"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Create preview (first 500 chars)
            preview = content[:500] + "..." if len(content) > 500 else content
            
            return {
                'type': 'text',
                'filename': filename,
                'content': content,
                'size': size,
                'preview': preview,
                'line_count': len(content.split('\n'))
            }
        except UnicodeDecodeError:
            # Try binary mode for non-UTF8 files
            with open(filepath, 'r', encoding='latin-1') as f:
                content = f.read()
            return {
                'type': 'text',
                'filename': filename,
                'content': content,
                'size': size,
                'preview': content[:500],
                'encoding': 'latin-1'
            }
            
    def _process_pdf_file(self, filepath: str, filename: str, size: int) -> Dict[str, Any]:
        """Extract text from PDF"""
        try:
            import PyPDF2
            
            with open(filepath, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                text_chunks = []
                
                for page_num, page in enumerate(reader.pages):
                    text = page.extract_text()
                    text_chunks.append(f"--- Page {page_num + 1} ---\n{text}")
                    
                content = "\n\n".join(text_chunks)
                preview = content[:500] + "..." if len(content) > 500 else content
                
                return {
                    'type': 'pdf',
                    'filename': filename,
                    'content': content,
                    'size': size,
                    'preview': preview,
                    'page_count': len(reader.pages)
                }
                
        except ImportError:
            return {
                'type': 'pdf',
                'filename': filename,
                'content': f"[PDF file: {filename}]\n\nNote: Install PyPDF2 to extract text automatically.\nRun: pip install PyPDF2",
                'size': size,
                'error': 'PyPDF2 not installed'
            }
        except Exception as e:
            return {
                'type': 'pdf',
                'filename': filename,
                'content': f"[PDF file: {filename}]\n\nError reading PDF: {str(e)}",
                'size': size,
                'error': str(e)
            }
            
    def _process_image_file(self, filepath: str, filename: str, size: int) -> Dict[str, Any]:
        """Process image file"""
        # Read as base64 for display
        with open(filepath, 'rb') as f:
            image_data = base64.b64encode(f.read()).decode('utf-8')
            
        # Get image description from Vision agent if available
        description = "[Image attached]"
        if self.vision_agent:
            try:
                # Vision agent can analyze the image
                description = self.vision_agent.execute(f"Describe this image in detail: {filepath}")
            except:
                description = f"[Image: {filename}]\n\nNote: Vision agent not available for analysis."
                
        return {
            'type': 'image',
            'filename': filename,
            'content': description,
            'size': size,
            'image_data': image_data,
            'filepath': filepath
        }
        
    def format_attachment_message(self, attachment_data: Dict[str, Any]) -> str:
        """Format attachment data for display in chat"""
        file_type = attachment_data['type']
        filename = attachment_data['filename']
        size_kb = attachment_data['size'] / 1024
        
        if file_type == 'text':
            lines = attachment_data.get('line_count', '?')
            return f"📄 **{filename}** ({size_kb:.1f} KB, {lines} lines)\n\n```\n{attachment_data['preview']}\n```"
            
        elif file_type == 'pdf':
            pages = attachment_data.get('page_count', '?')
            return f"📕 **{filename}** ({size_kb:.1f} KB, {pages} pages)\n\n{attachment_data['preview']}"
            
        elif file_type == 'image':
            return f"🖼️ **{filename}** ({size_kb:.1f} KB)\n\n{attachment_data['content']}"
            
        return f"📎 **{filename}** ({size_kb:.1f} KB)"

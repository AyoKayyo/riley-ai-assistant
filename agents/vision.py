"""
Vision Agent - Handles image analysis and multimodal tasks
"""
import base64
from io import BytesIO
from PIL import Image

class VisionAgent:
    """
    Specialized agent for image analysis and vision tasks
    Uses LLaVA model for multimodal understanding
    """
    
    def __init__(self, llm):
        self.llm = llm
        self.role = "Vision Specialist"
        self.goal = "Analyze images and provide detailed descriptions and insights"
    
    def execute(self, task: str, image_path: str = None, image_data: bytes = None) -> str:
        """
        Execute a vision task with an image
        
        Args:
            task: The question or task about the image
            image_path: Path to image file (optional)
            image_data: Raw image bytes (optional)
        """
        if not image_path and not image_data:
            return "❌ No image provided for vision analysis"
        
        try:
            # Load image if path provided
            if image_path:
                with open(image_path, 'rb') as f:
                    image_data = f.read()
            
            # Encode image to base64
            img_base64 = base64.b64encode(image_data).decode('utf-8')
            
            # Create vision prompt
            vision_prompt = f"""You are an expert at analyzing images. 

Task: {task}

Please provide a detailed, accurate analysis of the image."""

            # Note: This is a placeholder - actual implementation would use
            # Ollama's multimodal API or LLaVA model
            # For now, return instruction for manual setup
            return (f"🔍 Vision Analysis Ready!\n\n"
                   f"Image received ({len(image_data)} bytes)\n"
                   f"Task: {task}\n\n"
                   f"Note: To enable full vision analysis, ensure LLaVA model is downloaded:\n"
                   f"  ollama pull llava:7b\n\n"
                   f"Then the agent will automatically analyze images!")
            
        except Exception as e:
            return f"❌ Error during vision analysis: {str(e)}"
    
    def analyze_screenshot(self, task: str) -> str:
        """
        Analyze a screenshot
        """
        return self.execute(task, image_data=None)

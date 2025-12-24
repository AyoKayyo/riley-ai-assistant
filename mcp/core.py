"""
MCP - Main Control Program
Central command system with safety and notifications
"""
import os
import json
from datetime import datetime
from typing import Dict, List, Tuple, Optional
from enum import Enum
from agents.memory import MemorySystem


class SafetyLevel(Enum):
    """Safety levels for actions"""
    GREEN = "auto"      # Safe to auto-execute
    YELLOW = "notify"   # Execute but notify user
    RED = "approval"    # Require explicit approval


class Action:
    """Represents an action the assistant wants to take"""
    
    def __init__(self, action_type: str, description: str, safety_level: SafetyLevel, 
                 function, *args, **kwargs):
        self.action_type = action_type
        self.description = description
        self.safety_level = safety_level
        self.function = function
        self.args = args
        self.kwargs = kwargs
        self.timestamp = datetime.now()
        self.approved = False
        self.executed = False
        self.result = None
    
    def to_dict(self):
        """Convert to dictionary for logging"""
        return {
            'action_type': self.action_type,
            'description': self.description,
            'safety_level': self.safety_level.value,
            'timestamp': self.timestamp.isoformat(),
            'approved': self.approved,
            'executed': self.executed
        }


class SafetyController:
    """
    Controls what actions can be executed automatically
    Provides approval gates for dangerous operations
    """
    
    def __init__(self):
        self.action_log = []
        self.pending_approvals = []
        
        # Define safety rules
        self.safety_rules = {
            # GREEN - Auto-execute
            'read_file': SafetyLevel.GREEN,
            'search_web': SafetyLevel.GREEN,
            'analyze_text': SafetyLevel.GREEN,
            'generate_code': SafetyLevel.GREEN,
            'chat': SafetyLevel.GREEN,
            
            # YELLOW - Notify user
            'create_file': SafetyLevel.YELLOW,
            'navigate_browser': SafetyLevel.YELLOW,
            'send_email': SafetyLevel.YELLOW,
            'modify_file': SafetyLevel.YELLOW,
            
            # RED - Require approval
            'delete_file': SafetyLevel.RED,
            'delete_directory': SafetyLevel.RED,
            'system_command': SafetyLevel.RED,
            'deploy_website': SafetyLevel.RED,
            'install_software': SafetyLevel.RED,
            'access_credentials': SafetyLevel.RED,
        }
    
    def evaluate_action(self, action_type: str) -> SafetyLevel:
        """Determine safety level for an action"""
        # Default to YELLOW for unknown actions
        return self.safety_rules.get(action_type, SafetyLevel.YELLOW)
    
    def can_execute(self, action: Action) -> Tuple[bool, str]:
        """
        Check if action can be executed
        Returns: (can_execute, reason)
        """
        if action.safety_level == SafetyLevel.GREEN:
            return (True, "Safe to auto-execute")
        
        elif action.safety_level == SafetyLevel.YELLOW:
            # Can execute but should notify
            return (True, "Will execute and notify")
        
        elif action.safety_level == SafetyLevel.RED:
            # Needs approval
            if action.approved:
                return (True, "User approved")
            else:
                self.pending_approvals.append(action)
                return (False, "Waiting for user approval")
        
        return (False, "Unknown safety level")
    
    def request_approval(self, action: Action) -> str:
        """Generate approval request message"""
        return f"""
🔴 APPROVAL REQUIRED

Action: {action.action_type}
Description: {action.description}
Time: {action.timestamp.strftime('%H:%M:%S')}

This action requires your approval to proceed.
Reply 'approve' to allow, 'deny' to cancel.
"""
    
    def approve_action(self, action_id: int):
        """Approve a pending action"""
        if action_id < len(self.pending_approvals):
            self.pending_approvals[action_id].approved = True
            return True
        return False
    
    def log_action(self, action: Action):
        """Log an executed action"""
        self.action_log.append(action)
        
        # Keep only last 1000 actions
        if len(self.action_log) > 1000:
            self.action_log = self.action_log[-1000:]
    
    def get_action_history(self, limit: int = 10) -> List[Dict]:
        """Get recent action history"""
        return [action.to_dict() for action in self.action_log[-limit:]]


class NotificationSystem:
    """
    Handles notifications to user
    Supports iMessage, GUI popups, and in-app notifications
    """
    
    def __init__(self, phone_number: Optional[str] = None):
        self.phone_number = phone_number
        self.notification_log = []
    
    def send_imessage(self, message: str, phone_number: Optional[str] = None):
        """Send iMessage via macOS"""
        target = phone_number or self.phone_number
        
        if not target:
            print("⚠️ No phone number configured for iMessage")
            return False
        
        try:
            # Use AppleScript to send iMessage
            import subprocess
            
            # Escape quotes in message
            safe_message = message.replace('"', '\\"')
            
            applescript = f'''
            tell application "Messages"
                set targetService to 1st account whose service type = iMessage
                set targetBuddy to participant "{target}" of targetService
                send "{safe_message}" to targetBuddy
            end tell
            '''
            
            subprocess.run(['osascript', '-e', applescript], check=True)
            self.log_notification('imessage', message, target)
            return True
            
        except Exception as e:
            print(f"❌ iMessage failed: {e}")
            return False
    
    def gui_notification(self, title: str, message: str):
        """Show macOS notification"""
        try:
            import subprocess
            subprocess.run([
                'osascript', '-e', 
                f'display notification "{message}" with title "{title}"'
            ])
            self.log_notification('gui', f"{title}: {message}")
            return True
        except Exception as e:
            print(f"❌ GUI notification failed: {e}")
            return False
    
    def log_notification(self, notification_type: str, message: str, recipient: str = 'local'):
        """Log sent notification"""
        self.notification_log.append({
            'type': notification_type,
            'message': message,
            'recipient': recipient,
            'timestamp': datetime.now().isoformat()
        })


class MCP:
    """
    Main Control Program
    Central orchestration system with safety and notifications
    """
    
    def __init__(self, llm, phone_number: Optional[str] = None):
        self.llm = llm
        self.memory = MemorySystem()
        self.safety = SafetyController()
        self.notifications = NotificationSystem(phone_number)
        
        # Load phone number from memory if available
        if not phone_number:
            saved_number = self.memory.get_context('phone_number')
            if saved_number:
                self.notifications.phone_number = saved_number
        
        # Sub-agent registry (populated later)
        self.agents = {}
        
        # Configuration
        self.config = {
            'auto_notify_yellow': True,  # Auto-notify for YELLOW actions
            'auto_notify_complete': True,  # Notify when tasks complete
            'gui_notifications': True,  # Show GUI notifications
            'imessage_notifications': False,  # Send iMessage (enable manually)
        }
        
        # Load config from memory
        saved_config = self.memory.get_context('mcp_config')
        if saved_config:
            self.config.update(saved_config)
    
    def register_agent(self, name: str, agent):
        """Register a sub-agent"""
        self.agents[name] = agent
        print(f"✅ Registered agent: {name}")
    
    def execute_action(self, action_type: str, description: str, function, *args, **kwargs):
        """
        Execute an action with safety checks
        """
        # Determine safety level
        safety_level = self.safety.evaluate_action(action_type)
        
        # Create action
        action = Action(action_type, description, safety_level, function, *args, **kwargs)
        
        # Check if can execute
        can_execute, reason = self.safety.can_execute(action)
        
        if not can_execute:
            # Need approval
            approval_msg = self.safety.request_approval(action)
            
            if self.config['gui_notifications']:
                self.notifications.gui_notification("Approval Required", description)
            
            if self.config['imessage_notifications']:
                self.notifications.send_imessage(approval_msg)
            
            return {
                'status': 'pending_approval',
                'message': approval_msg,
                'action_id': len(self.safety.pending_approvals) - 1
            }
        
        # Execute the action
        try:
            result = function(*args, **kwargs)
            action.executed = True
            action.result = result
            
            # Log the action
            self.safety.log_action(action)
            
            # Notify if configured
            if safety_level == SafetyLevel.YELLOW and self.config['auto_notify_yellow']:
                self.notifications.gui_notification(
                    "Action Executed",
                    description
                )
            
            return {
                'status': 'success',
                'result': result,
                'safety_level': safety_level.value
            }
            
        except Exception as e:
            # Notify on error
            error_msg = f"Error in {action_type}: {str(e)}"
            
            if self.config['gui_notifications']:
                self.notifications.gui_notification("Action Failed", description)
            
            if self.config['imessage_notifications']:
                self.notifications.send_imessage(f"❌ {error_msg}")
            
            return {
                'status': 'error',
                'error': str(e),
                'action_type': action_type
            }
    
    def process_task(self, task: str, **kwargs) -> Tuple[str, str]:
        """
        Process a task by delegating to appropriate agent
        With safety checks and notifications
        """
        # Determine which agent to use
        task_lower = task.lower()
        
        # Vision tasks
        if 'image' in task_lower or 'picture' in task_lower or 'photo' in task_lower:
            if 'vision' in self.agents:
                result = self.agents['vision'].execute(task, **kwargs)
                self.memory.add_conversation(task, result, "Vision")
                return (result, "Vision")
        
        # Research tasks
        if any(word in task_lower for word in ['search', 'find', 'research', 'look up', 'what is', 'who is']):
            if 'researcher' in self.agents:
                result = self.agents['researcher'].execute(task)
                self.memory.add_conversation(task, result, "Researcher")
                return (result, "Researcher")
        
        # Coding tasks
        if any(word in task_lower for word in ['code', 'function', 'write', 'implement', 'bug', 'debug', 'fix']):
            if 'coder' in self.agents:
                result = self.agents['coder'].execute(task)
                self.memory.add_conversation(task, result, "Coder")
                return (result, "Coder")
        
        # Default to executor
        if 'executor' in self.agents:
            result = self.agents['executor'].execute(task)
            self.memory.add_conversation(task, result, "Executor")
            return (result, "Executor")
        
        # Fallback to direct LLM
        try:
            response = self.llm.invoke(task)
            if hasattr(response, 'content'):
                result = response.content
            else:
                result = str(response)
            self.memory.add_conversation(task, result, "Assistant")
            return (result, "Assistant")
        except Exception as e:
            error_msg = f"Error: {str(e)}"
            self.memory.add_conversation(task, error_msg, "Error")
            return (error_msg, "Error")
    
    def configure(self, **kwargs):
        """Update MCP configuration"""
        self.config.update(kwargs)
        self.memory.set_context('mcp_config', self.config)
    
    def set_phone_number(self, phone_number: str):
        """Set phone number for iMessage notifications"""
        self.notifications.phone_number = phone_number
        self.memory.set_context('phone_number', phone_number)
        return f"✅ Phone number saved: {phone_number}"
    
    def enable_imessage(self):
        """Enable iMessage notifications"""
        if self.notifications.phone_number:
            self.config['imessage_notifications'] = True
            self.memory.set_context('mcp_config', self.config)
            return "✅ iMessage notifications enabled"
        else:
            return "❌ Set phone number first using: set_phone_number('+1234567890')"
    
    def get_status(self) -> Dict:
        """Get MCP status"""
        return {
            'registered_agents': list(self.agents.keys()),
            'pending_approvals': len(self.safety.pending_approvals),
            'recent_actions': self.safety.get_action_history(5),
            'config': self.config,
            'phone_configured': bool(self.notifications.phone_number)
        }

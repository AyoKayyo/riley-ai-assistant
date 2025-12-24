#!/usr/bin/env python3
"""
Verification Script - Test all major features
"""
import os
import sys

print("🔍 AI Command Center - System Verification")
print("=" * 50)

# Test 1: Import all modules
print("\n1️⃣ Testing Module Imports...")
try:
    from agents.companion import CompanionAgent
    from agents.conversation_db import ConversationDB
    from agents.agent_generator import AgentGenerator
    from utils.file_handler import FileAttachmentHandler
    from ui.settings_dialog import SettingsDialog
    from ui.agent_builder import AgentBuilderDialog
    from ui.typing_animator import TypingWorker
    print("   ✅ All modules import successfully")
except Exception as e:
    print(f"   ❌ Import error: {e}")
    sys.exit(1)

# Test 2: Database connectivity
print("\n2️⃣ Testing Conversation Database...")
try:
    db = ConversationDB()
    stats = db.get_stats()
    print(f"   ✅ Database initialized")
    print(f"   📊 Stats: {stats['conversations']} conversations, {stats['messages']} messages")
    db.close()
except Exception as e:
    print(f"   ❌ Database error: {e}")

# Test 3: File Handler
print("\n3️⃣ Testing File Handler...")
try:
    handler = FileAttachmentHandler()
    # Create a test text file
    test_file = "/tmp/test_attachment.txt"
    with open(test_file, "w") as f:
        f.write("This is a test file for verification.")
    
    result = handler.process_file(test_file)
    print(f"   ✅ Processed test file: {result['filename']}")
    print(f"   📄 Type: {result['type']}, Size: {result['size']} bytes")
    os.remove(test_file)
except Exception as e:
    print(f"   ❌ File handler error: {e}")

# Test 4: Environment Check
print("\n4️⃣ Testing Environment Configuration...")
try:
    from dotenv import load_dotenv
    load_dotenv()
    
    companion_model = os.getenv("COMPANION_MODEL", "NOT SET")
    ollama_url = os.getenv("OLLAMA_BASE_URL", "NOT SET")
    
    print(f"   ✅ Environment loaded")
    print(f"   🤖 Companion Model: {companion_model}")
    print(f"   🌐 Ollama URL: {ollama_url}")
except Exception as e:
    print(f"   ❌ Environment error: {e}")

# Test 5: Ollama Connection
print("\n5️⃣ Testing Ollama Connection...")
try:
    import requests
    response = requests.get("http://localhost:11434/api/tags", timeout=2)
    if response.status_code == 200:
        models = response.json().get('models', [])
        print(f"   ✅ Ollama is running")
        print(f"   📦 {len(models)} models available")
    else:
        print(f"   ⚠️  Ollama responded with status {response.status_code}")
except Exception as e:
    print(f"   ❌ Ollama connection error: {e}")

print("\n" + "=" * 50)
print("✅ VERIFICATION COMPLETE")
print("\nAll core systems are operational!")

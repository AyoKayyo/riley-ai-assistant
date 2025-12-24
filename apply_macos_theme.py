# Quick Theme Update Script
# Run this to apply macOS system theme to your GUI

import re

# Read the current GUI file
with open('agent_gui.py', 'r') as f:
    content = f.read()

# Replace blue colors with macOS grays
replacements = {
    # Background colors - switch to macOS dark mode
    'QColor(17, 24, 39)': 'QColor(30, 30, 30)',   # Main bg
    'QColor(31, 41, 55)': 'QColor(40, 40, 40)',   # Input bg
    'QColor(55, 65, 81)': 'QColor(50, 50, 50)',   # Button bg
    'QColor(243, 244, 246)': 'QColor(255, 255, 255)',  # Text
    
    # Remove blue accents
    '#60a5fa': '#a0a0a0',  # Title colors
    '#2563eb': '#5a5a5a',  # Buttons
    '#1d4ed8': '#6a6a6a',  # Button hover
    '#374151': '#3a3a3a',  # Secondary bg
    '#4b5563': '#5050 50',  # Hover states
    '#1f2937': '#2a2a2a',  # Chat display
    
    # Fonts - use system font
    'SF Pro Text': '.AppleSystemUIFont',
    'SF Pro Display': '.AppleSystemUIFont',
}

for old, new in replacements.items():
    content = content.replace(old, new)

# Write back
with open('agent_gui.py', 'w') as f:
    f.write(content)

print("✅ Theme updated to macOS system colors!")
print("🚀 Restart the GUI to see changes")

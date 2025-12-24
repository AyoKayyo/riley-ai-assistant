#!/bin/bash
# Launch Local AI Agent Menu Bar App

cd "$(dirname "$0")"

echo "🚀 Launching Local AI Agent Menu Bar App..."
echo ""

# Activate virtual environment
source venv/bin/activate

# Run the GUI
python agent_gui.py

#!/bin/bash
# Quick start script for Local LLM Agent System

cd "$(dirname "$0")"

echo "🤖 Local LLM Agent System"
echo "=========================="
echo ""
echo "Activating Python environment..."
source venv/bin/activate

echo "✅ Environment activated"
echo ""
echo "Starting in interactive mode..."
echo ""

python main.py --interactive

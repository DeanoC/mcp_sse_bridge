#!/bin/bash
# Installation script for VSCode MCP Server

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

echo "Installation complete!"
echo "To run the server manually: source venv/bin/activate && python app/main.py"
echo "To configure as a systemd service, run: sudo ./setup_systemd.sh"

#!/bin/bash
# Setup script for VSCode MCP Server systemd service

# Check if running as root
if [ "$EUID" -ne 0 ]; then
  echo "Please run as root (use sudo)"
  exit 1
fi

# Get the current directory
INSTALL_DIR=$(pwd)
SERVICE_NAME="vscode-mcp-server"
SERVICE_FILE="/etc/systemd/system/${SERVICE_NAME}.service"

# Create systemd service file
cat > $SERVICE_FILE << EOL
[Unit]
Description=VSCode MCP Server with SSE Protocol
After=network.target

[Service]
Type=simple
User=$(logname)
WorkingDirectory=${INSTALL_DIR}
Environment="PATH=${INSTALL_DIR}/venv/bin:/usr/local/bin:/usr/bin:/bin"
Environment="MCP_PORT=3001"
Environment="MCP_API_TOKEN=test-token"
ExecStart=${INSTALL_DIR}/venv/bin/python ${INSTALL_DIR}/app/main.py
Restart=on-failure
RestartSec=5s

[Install]
WantedBy=multi-user.target
EOL

# Set permissions
chmod 644 $SERVICE_FILE

# Reload systemd
systemctl daemon-reload

# Enable and start the service
systemctl enable $SERVICE_NAME
systemctl start $SERVICE_NAME

echo "Systemd service installed and started!"
echo "Service name: $SERVICE_NAME"
echo "Service status: $(systemctl is-active $SERVICE_NAME)"
echo ""
echo "To check logs: sudo journalctl -u $SERVICE_NAME -f"
echo "To restart: sudo systemctl restart $SERVICE_NAME"
echo "To stop: sudo systemctl stop $SERVICE_NAME"

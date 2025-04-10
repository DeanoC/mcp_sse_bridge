# VSCode MCP Server with SSE Protocol - User Guide

This guide explains how to install, configure, and use the VSCode MCP Server that operates using the Server-Sent Events (SSE) protocol.

## Installation

1. Clone or download this repository to your server
2. Run the installation script to set up the Python virtual environment and install dependencies:

```bash
chmod +x install.sh
./install.sh
```

## Running the Server

### Method 1: Running Manually

You can run the server manually with:

```bash
source venv/bin/activate
python app/main.py
```

The server will start on port 3001 by default.

### Method 2: Running as a Systemd Service

To install and run the server as a systemd service:

```bash
sudo ./setup_systemd.sh
```

This will:
1. Create a systemd service file
2. Enable the service to start on boot
3. Start the service immediately

### Systemd Service Management

Once installed as a systemd service, you can manage it with these commands:

```bash
# Check status
sudo systemctl status vscode-mcp-server

# View logs
sudo journalctl -u vscode-mcp-server -f

# Restart the service
sudo systemctl restart vscode-mcp-server

# Stop the service
sudo systemctl stop vscode-mcp-server

# Start the service
sudo systemctl start vscode-mcp-server
```

## Configuration

The server can be configured using environment variables:

- `MCP_PORT`: The port to listen on (default: 3001)
- `MCP_API_TOKEN`: The Bearer token for authentication (default: "test-token")

You can set these in the systemd service file or when running manually:

```bash
MCP_PORT=3002 MCP_API_TOKEN=your-secret-token python app/main.py
```

## Connecting from VSCode

To connect VSCode to this MCP server:

1. Create a `.vscode/mcp.json` file in your workspace with the following content:

```json
{
  "servers": {
    "Echo MCP Server": {
      "type": "sse",
      "url": "http://localhost:3001",
      "headers": {
        "Authorization": "Bearer test-token"
      }
    }
  }
}
```

2. In VSCode, open the Command Palette (Ctrl+Shift+P) and run "MCP: List Servers"
3. Your server should appear in the list
4. Use GitHub Copilot's agent mode to interact with the echo tool

## Testing with the Example Client

An example client is provided to test the server:

1. Install the required dependencies:

```bash
pip install requests sseclient-py
```

2. Run the example client:

```bash
python examples/client_example.py
```

The client will:
- Connect to the SSE stream
- List available tools
- Call the echo tool with a test message
- Display the results

## Security Considerations

For production use:
- Change the default API token
- Use HTTPS with a valid SSL certificate
- Consider implementing more robust authentication
- Restrict access to the server using firewall rules

## Troubleshooting

If you encounter issues:
1. Check the server logs
2. Verify the API token is correct
3. Ensure the port is not blocked by a firewall
4. Check that the server is running and accessible

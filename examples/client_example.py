#!/usr/bin/env python3
"""
Example client for testing the VSCode MCP Server with SSE Protocol

This script demonstrates how to connect to the MCP server and use the echo tool.
"""

import json
import requests
import sseclient
import threading
import time

# Configuration
SERVER_URL = "http://localhost:3001"
API_TOKEN = "test-token"
HEADERS = {
    "Authorization": f"Bearer {API_TOKEN}",
    "Content-Type": "application/json"
}

def listen_for_sse_events():
    """Listen for SSE events from the server"""
    url = f"{SERVER_URL}/mcp/sse"
    response = requests.get(url, headers=HEADERS, stream=True)
    client = sseclient.SSEClient(response)
    
    print("Connected to SSE stream, listening for events...")
    for event in client.events():
        print(f"Received SSE event: {event.data}")

def call_echo_tool(message):
    """Call the echo tool on the server"""
    url = f"{SERVER_URL}/mcp/jsonrpc"
    payload = {
        "jsonrpc": "2.0",
        "method": "tools/call",
        "params": {
            "name": "echo",
            "arguments": {
                "message": message
            }
        },
        "id": "1"
    }
    
    response = requests.post(url, headers=HEADERS, json=payload)
    return response.json()

def list_tools():
    """List available tools on the server"""
    url = f"{SERVER_URL}/mcp/jsonrpc"
    payload = {
        "jsonrpc": "2.0",
        "method": "tools/list",
        "id": "1"
    }
    
    response = requests.post(url, headers=HEADERS, json=payload)
    return response.json()

def main():
    # Start SSE listener in a separate thread
    sse_thread = threading.Thread(target=listen_for_sse_events)
    sse_thread.daemon = True
    sse_thread.start()
    
    # Give the SSE connection time to establish
    time.sleep(1)
    
    # List available tools
    print("\nListing available tools:")
    tools_response = list_tools()
    print(json.dumps(tools_response, indent=2))
    
    # Call the echo tool
    message = "Hello from MCP client!"
    print(f"\nCalling echo tool with message: '{message}'")
    echo_response = call_echo_tool(message)
    print(json.dumps(echo_response, indent=2))
    
    # Keep the main thread alive to receive SSE events
    print("\nPress Ctrl+C to exit")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Exiting...")

if __name__ == "__main__":
    main()

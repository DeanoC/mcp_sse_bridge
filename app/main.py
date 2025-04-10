#!/usr/bin/env python3
"""
VSCode MCP Server with SSE Protocol

This server implements a simple MCP server that operates using the SSE protocol.
It provides a simple echo tool and uses Bearer Authentication.
"""

import asyncio
import json
import logging
import os
import sys
import uuid
from typing import Dict, List, Optional, Union, Any

import uvicorn
from fastapi import FastAPI, HTTPException, Depends, Request, Response, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
from sse_starlette.sse import EventSourceResponse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("mcp-server")

# Configuration
DEFAULT_PORT = 3001
API_TOKEN = os.environ.get("MCP_API_TOKEN", "test-token")

# Initialize FastAPI app
app = FastAPI(title="VSCode MCP Server", description="MCP Server with SSE Protocol")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security scheme
security = HTTPBearer()

# Active SSE connections
connections: Dict[str, asyncio.Queue] = {}

# MCP Models
class Tool(BaseModel):
    name: str
    description: str
    inputSchema: Dict[str, Any]

class TextContent(BaseModel):
    type: str = "text"
    text: str

class ToolCallResult(BaseModel):
    id: str
    result: Union[TextContent, Dict[str, Any]]

class ListChangedEvent(BaseModel):
    type: str = "list_changed"
    tools: List[Tool]

# Authentication dependency
async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    if credentials.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication scheme. Bearer authentication required.",
        )
    if credentials.credentials != API_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )
    return credentials.credentials

# Define MCP tools
def get_tools() -> List[Tool]:
    return [
        Tool(
            name="echo",
            description="Echoes back the input message",
            inputSchema={
                "type": "object",
                "properties": {
                    "message": {
                        "type": "string",
                        "description": "Message to echo back"
                    }
                },
                "required": ["message"]
            }
        )
    ]

# Routes
@app.get("/")
async def root():
    return {"message": "VSCode MCP Server with SSE Protocol"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# MCP SSE connection endpoint
@app.get("/mcp/sse")
async def mcp_sse(request: Request, token: str = Depends(verify_token)):
    client_id = str(uuid.uuid4())
    queue = asyncio.Queue()
    connections[client_id] = queue
    
    logger.info(f"Client connected: {client_id}")
    
    # Send initial list_changed event with available tools
    await queue.put(json.dumps(ListChangedEvent(tools=get_tools()).dict()))
    
    async def event_generator():
        try:
            while True:
                if await request.is_disconnected():
                    break
                
                # Get message from queue
                message = await queue.get()
                yield message
                
                # Wait a bit before checking for the next message
                await asyncio.sleep(0.1)
        except asyncio.CancelledError:
            logger.info(f"Connection closed for client: {client_id}")
        finally:
            if client_id in connections:
                del connections[client_id]
            logger.info(f"Client disconnected: {client_id}")
    
    return EventSourceResponse(event_generator())

# MCP JSON-RPC endpoint for client-to-server communication
@app.post("/mcp/jsonrpc")
async def mcp_jsonrpc(request: Request, token: str = Depends(verify_token)):
    try:
        data = await request.json()
        logger.info(f"Received JSON-RPC request: {data}")
        
        # Process JSON-RPC request
        if "method" not in data:
            return {"jsonrpc": "2.0", "error": {"code": -32600, "message": "Invalid Request"}, "id": data.get("id")}
        
        method = data.get("method")
        params = data.get("params", {})
        req_id = data.get("id")
        
        # Handle tools/list method
        if method == "tools/list":
            return {
                "jsonrpc": "2.0",
                "result": [tool.dict() for tool in get_tools()],
                "id": req_id
            }
        
        # Handle tools/call method
        elif method == "tools/call":
            tool_name = params.get("name")
            arguments = params.get("arguments", {})
            
            if tool_name == "echo":
                message = arguments.get("message", "")
                result = TextContent(type="text", text=message)
                
                # Create a response
                response = {
                    "jsonrpc": "2.0",
                    "result": ToolCallResult(id=str(uuid.uuid4()), result=result).dict(),
                    "id": req_id
                }
                
                return response
            else:
                return {
                    "jsonrpc": "2.0",
                    "error": {"code": -32601, "message": f"Tool not found: {tool_name}"},
                    "id": req_id
                }
        
        # Handle unknown method
        else:
            return {
                "jsonrpc": "2.0",
                "error": {"code": -32601, "message": f"Method not found: {method}"},
                "id": req_id
            }
    
    except Exception as e:
        logger.error(f"Error processing JSON-RPC request: {str(e)}")
        return {
            "jsonrpc": "2.0",
            "error": {"code": -32603, "message": "Internal error"},
            "id": data.get("id") if "data" in locals() and isinstance(data, dict) else None
        }

def main():
    port = int(os.environ.get("MCP_PORT", DEFAULT_PORT))
    logger.info(f"Starting MCP server on port {port}")
    logger.info(f"Using Bearer Authentication with token: {API_TOKEN}")
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=False,
        log_level="info"
    )

if __name__ == "__main__":
    main()

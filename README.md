# VSCode MCP Server with SSE Protocol

This documentation provides key information about implementing a VSCode Model Context Protocol (MCP) server that operates using the Server-Sent Events (SSE) protocol.

## What is MCP?

Model Context Protocol (MCP) is an open standard that enables AI models to interact with external tools and services through a unified interface. In VS Code, MCP support enhances GitHub Copilot's agent mode by allowing you to connect any MCP-compatible server to your agentic coding workflow.

MCP follows a client-server architecture:
- **MCP clients** (like VS Code) connect to MCP servers and request actions on behalf of the AI model
- **MCP servers** provide one or more tools that expose specific functionalities through a well-defined interface
- **The Model Context Protocol (MCP)** defines the message format for communication between clients and servers, including tool discovery, invocation, and response handling

## Server-Sent Events (SSE) Transport

VS Code supports both standard input/output (`stdio`) and server-sent events (`sse`) for MCP server transport. This implementation focuses on the SSE transport method.

Key characteristics of SSE transport:
- Uses HTTP POST requests for client-to-server communication
- Uses Server-Sent Events for server-to-client streaming
- Suitable when only server-to-client streaming is needed
- Works well with restricted networks
- Good for implementing simple updates

## Security Considerations for SSE Transport

SSE transports require proper security measures:
1. **Always validate Origin headers** on incoming SSE connections
2. **Avoid binding servers to all network interfaces** (0.0.0.0) when running locally - bind only to localhost (127.0.0.1) instead
3. **Implement proper authentication** for all SSE connections - in this case, Bearer Authentication

## MCP Tools Implementation

Tools are a powerful primitive in MCP that enable servers to expose executable functionality to clients. Through tools, LLMs can interact with external systems, perform computations, and take actions in the real world.

Key aspects of tools include:
- **Discovery**: Clients can list available tools through the `tools/list` endpoint
- **Invocation**: Tools are called using the `tools/call` endpoint, where servers perform the requested operation and return results
- **Flexibility**: Tools can range from simple calculations to complex API interactions

### Tool Definition Structure

Each tool is defined with the following structure:
```json
{
  "name": "string",         // Unique identifier for the tool
  "description": "string",  // Human-readable description
  "inputSchema": {          // JSON Schema for the tool's parameters
    "type": "object",
    "properties": { ... }   // Tool-specific parameters
  }
}
```

## Bearer Authentication Implementation

Bearer Authentication is a simple HTTP authentication scheme that involves security tokens called bearer tokens. The client must include a valid token in the Authorization header when making requests to protected resources.

For our MCP server implementation:
1. The server will validate the Authorization header for each request
2. The header should be in the format: `Authorization: Bearer <token>`
3. If the token is invalid or missing, the server will return a 401 Unauthorized response
4. The token validation will be a simple comparison with a predefined token for this example

## Message Format

MCP uses JSON-RPC 2.0 as its wire format. The transport layer is responsible for:
- Converting MCP protocol messages into JSON-RPC format for transmission
- Converting received JSON-RPC messages back into MCP protocol messages

There are three types of JSON-RPC messages used:
1. Requests
2. Responses
3. Notifications

## Implementation Considerations

When implementing an MCP server with SSE protocol:
1. Handle connection lifecycle properly
2. Implement proper error handling
3. Clean up resources on connection close
4. Use appropriate timeouts
5. Validate messages before sending
6. Log transport events for debugging
7. Implement reconnection logic when appropriate
8. Handle backpressure in message queues
9. Monitor connection health
10. Implement proper security measures

## Next Steps

The following sections will provide a practical implementation of an MCP server with SSE protocol, including:
- A simple echo tool implementation
- Bearer Authentication handling
- Systemd service configuration for deployment

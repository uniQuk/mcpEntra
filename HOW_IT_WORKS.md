# How the Microsoft Graph MCP Server Works

This document provides a technical overview of how the Microsoft Graph MCP Server installation and setup process works.

## Overview

The Microsoft Graph MCP Server is designed to be easy to install and configure, while also being secure and flexible. The system consists of several components:

1. **MCP Server**: The core server that implements the Model Context Protocol and connects to Microsoft Graph API
2. **Installation System**: Scripts to help users install the server with minimal effort
3. **Configuration System**: Tools to configure the server with user credentials

## Installation Process

The one-line installer (`install.py`) performs the following steps:

1. **Checks Requirements**: Verifies that `git` and `python` are installed
2. **Clones Repository**: Downloads the code from GitHub
3. **Installs Dependencies**: Uses pip to install required Python packages
4. **Creates Launcher Script**: Adds a `mcp-graph-server` command to the user's PATH
5. **Runs Setup**: Guides the user through the credential configuration process

## Authentication Flow

The server uses a multi-layered authentication approach:

1. **Client Authentication**: 
   - MCP clients (Claude, Copilot, Cursor) authenticate to the MCP server using an API key
   - The API key is automatically generated during setup
   - This ensures only authorized clients can access the MCP server

2. **Microsoft Graph Authentication**:
   - The MCP server authenticates to Microsoft Graph using client credentials flow
   - Authentication uses the Azure.Identity library
   - Credentials are stored in a secure .env file

## Configuration System

The `setup_mcp.py` script:

1. **Prompts for Credentials**: Asks the user for tenant ID, client ID, and client secret
2. **Generates API Key**: Creates a random API key for client authentication
3. **Creates .env File**: Stores credentials securely
4. **Generates Client Configs**: Provides ready-to-use configuration snippets for:
   - VS Code
   - Claude Desktop
   - Cursor Agent

## Security Considerations

Several security measures are implemented:

1. **API Key Protection**: Secures the MCP server against unauthorized access
2. **Local Credential Storage**: Credentials are stored in a local .env file with restricted permissions
3. **Zero Trust**: The server does not make any assumptions about the environment
4. **No Hardcoded Secrets**: All sensitive information is provided by the user during setup
5. **Least Privilege**: Users are instructed to create app registrations with minimal required permissions

## How to Integrate with MCP Clients

Integration with different MCP clients follows these patterns:

### VS Code

VS Code uses an HTTP (SSE) connection directly to the MCP server. Configuration includes:

```json
{
  "servers": {
    "microsoft-graph": {
      "type": "sse",
      "url": "http://localhost:8000/sse",
      "headers": {
        "x-api-key": "YOUR_API_KEY"
      }
    }
  }
}
```

### Claude Desktop

Claude Desktop uses a command-line approach to connect to the MCP server:

```json
{
  "mcpServers": {
    "microsoft-graph": {
      "command": "python",
      "args": [
        "-m",
        "mcp_microsoft_graph"
      ],
      "env": {
        "TENANT_ID": "your-tenant-id",
        "CLIENT_ID": "your-client-id",
        "CLIENT_SECRET": "your-client-secret",
        "API_KEYS": "your-api-key"
      }
    }
  }
}
```

### Cursor Agent

Cursor uses a similar command-line approach to Claude Desktop:

```json
{
  "mcpServers": {
    "microsoft-graph": {
      "command": "python",
      "args": [
        "-m",
        "mcp_microsoft_graph"
      ],
      "env": {
        "TENANT_ID": "your-tenant-id",
        "CLIENT_ID": "your-client-id",
        "CLIENT_SECRET": "your-client-secret",
        "API_KEYS": "your-api-key"
      }
    }
  }
}
```

## MCP Tools Provided

The server implements the following MCP tools:

1. **listUsers**: Lists users in the Microsoft Entra ID tenant
2. **getUser**: Gets details for a specific user
3. **searchUsers**: Searches for users by name, email, etc.
4. **listGroups**: Lists groups in the Microsoft Entra ID tenant
5. **getGroupMembers**: Gets members of a specific group

## Extending the Server

The MCP server is designed to be extensible. Developers can:

1. Add new tools in the `add_graph_tools` function
2. Implement corresponding handler functions
3. Add new Microsoft Graph API endpoints

## Troubleshooting

Common issues and solutions:

1. **Installation fails**: 
   - Check Python version (3.8+ required)
   - Ensure git is installed
   - Verify you have write permissions for the installation directory

2. **Authentication errors**:
   - Verify client ID and secret are correct
   - Check that the app registration has the necessary permissions
   - Ensure admin consent has been granted

3. **MCP client connection issues**:
   - Make sure the MCP server is running
   - Verify API key in client configuration
   - Check network connectivity 
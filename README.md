# Microsoft Graph MCP Server

This is a Model Context Protocol (MCP) server that connects to the Microsoft Graph API. It allows AI assistants like Claude, GitHub Copilot, or Cursor Agent to access and query data from Microsoft Entra ID (formerly Azure Active Directory) through a standardized interface.

## Features

- Securely authenticate to Microsoft Graph using client credentials flow
- Query users, groups, and other Microsoft 365 data
- API key protection for MCP server access (automatically bypassed when used with AI assistants)
- Simple integration with Claude Desktop, VS Code, or other MCP clients

## Quick Start (GitHub Installation)

You can install directly from GitHub:

```bash
# Global installation
npm install -g github:YOUR_USERNAME/mcp-entra

# Run the server
mcp-entra
```

On first run, you'll be guided through the setup process to configure your Microsoft Entra ID credentials.

## AI Assistant Integration

For AI assistants like Claude Desktop, VS Code with Copilot, or Cursor, you can reference the GitHub repository directly in your configuration:

### Claude Desktop Configuration
```json
{
  "mcpServers": {
    "Microsoft-Entra": {
      "command": "npx",
      "args": [
        "-y",
        "github:YOUR_USERNAME/mcp-entra"
      ],
      "env": {
        "TENANT_ID": "your-tenant-id",
        "CLIENT_ID": "your-client-id",
        "CLIENT_SECRET": "your-client-secret",
        "AI_ASSISTANT": "true"
      }
    }
  }
}
```

### VS Code/GitHub Copilot Configuration
```json
{
  "servers": {
    "Microsoft-Entra": {
      "type": "npm",
      "packageInfo": {
        "name": "github:uniQuk/mcp-entra"
      },
      "env": {
        "TENANT_ID": "your-tenant-id",
        "CLIENT_ID": "your-client-id",
        "CLIENT_SECRET": "your-client-secret",
        "AI_ASSISTANT": "true"
      }
    }
  }
}
```

### Cursor Configuration
```json
{
  "mcpServers": {
    "Microsoft-Entra": {
      "command": "npx",
      "args": [
        "-y",
        "github:uniQuk/mcp-entra"
      ],
      "env": {
        "TENANT_ID": "your-tenant-id",
        "CLIENT_ID": "your-client-id",
        "CLIENT_SECRET": "your-client-secret",
        "AI_ASSISTANT": "true"
      }
    }
  }
}
```

## Prerequisites

Before you can use this MCP server, you'll need:

1. **Node.js 14+** and **Python 3.8+**
2. **Microsoft Entra ID App Registration** with appropriate permissions
3. **API Keys** for securing the MCP server (generated during setup, optional when used with AI assistants)

## AI Assistant Integration

When used with AI assistants like GitHub Copilot, Claude, or Cursor, the API key authentication is automatically bypassed for a more seamless experience. The server detects when it's running in an AI assistant environment and disables the API key requirement.

## Creating a Microsoft Entra ID App Registration

1. Go to the [Azure Portal](https://portal.azure.com)
2. Navigate to Azure Active Directory > App Registrations > New Registration
3. Enter a name for your app (e.g., "Graph MCP Server")
4. Select "Accounts in this organizational directory only" (single tenant)
5. No redirect URI is needed - click "Register"
6. Note down the **Application (client) ID** and **Directory (tenant) ID**
7. Navigate to "Certificates & secrets" and create a new client secret
8. Note down the secret value (you won't be able to see it again)
9. Go to "API Permissions" and add the following permissions:
   - User.Read.All
   - Group.Read.All
   - (Add other permissions as needed for your use case)
10. Click "Grant admin consent for [your tenant]"

## Available Tools

The MCP server exposes the following tools:

1. **listUsers** - Retrieve a list of users from Microsoft Entra ID tenant
2. **getUser** - Retrieve a specific user by ID or UPN from Microsoft Entra ID tenant
3. **searchUsers** - Search for users by display name, email, etc.
4. **listGroups** - Retrieve a list of groups from Microsoft Entra ID tenant
5. **getGroupMembers** - Retrieve members of a specific group from Microsoft Entra ID tenant

## Security Considerations

- API key authentication is automatically bypassed when running with AI assistants
- For non-AI usage, always use strong, unique API keys (the setup script generates one for you)
- Store your client credentials securely
- Consider deploying behind a reverse proxy for additional security
- Set appropriate Microsoft Graph API permissions (least privilege)

## Extending the Server

To add more Microsoft Graph API capabilities:

1. Add a new tool definition in the `add_graph_tools` function in `mcp_microsoft_graph.py`
2. Implement the tool handler function
3. Restart the server

## Troubleshooting

**Invalid API Key Error**:
- Make sure the API key in your client configuration matches one of the keys in your environment variables
- Or set `AI_ASSISTANT=true` in your environment variables when using with AI assistants

**Authentication Error**:
- Verify your Microsoft Graph client credentials are correct
- Ensure the app has the required permissions and admin consent

**MCP Connection Issues**:
- Check that the server is running and accessible from your client
- Verify the URL and transport configuration

## License

MIT 
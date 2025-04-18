#!/usr/bin/env python3
import os
import sys
import getpass
import argparse
import json
from pathlib import Path

def setup_mcp_server():
    """
    Interactive setup for the Microsoft Graph MCP Server.
    Prompts for credentials and stores them securely.
    """
    print("\n=== Microsoft Graph MCP Server Setup ===\n")
    print("This script will guide you through setting up the Microsoft Graph MCP Server.")
    print("You'll need to provide credentials for your Microsoft Entra ID tenant.")
    print("These credentials will be stored locally and used to connect to Microsoft Graph.")
    print("\nIMPORTANT: Make sure you have created an app registration in Microsoft Entra ID")
    print("with the necessary permissions (User.Read.All, Group.Read.All, etc.)\n")
    
    # Get credentials
    tenant_id = input("Enter your Microsoft Entra ID Tenant ID: ").strip()
    client_id = input("Enter your App Registration Client ID: ").strip()
    client_secret = getpass.getpass("Enter your App Registration Client Secret: ").strip()
    
    # Generate a random API key
    import secrets
    api_key = secrets.token_urlsafe(32)
    print(f"\nGenerated API key: {api_key}")
    print("This key will be used to secure your MCP server. Keep it safe!")
    
    # Create .env file
    env_file = Path(".env")
    
    # Check if file exists and ask for confirmation to overwrite
    if env_file.exists():
        overwrite = input("\n.env file already exists. Overwrite? (y/n): ").strip().lower()
        if overwrite != 'y':
            print("Setup canceled. Existing .env file preserved.")
            return False
    
    # Write credentials to .env file
    with open(env_file, 'w') as f:
        f.write(f"# Microsoft Entra ID App Registration credentials\n")
        f.write(f"TENANT_ID={tenant_id}\n")
        f.write(f"CLIENT_ID={client_id}\n")
        f.write(f"CLIENT_SECRET={client_secret}\n\n")
        f.write(f"# API Keys for accessing the MCP server\n")
        f.write(f"API_KEYS={api_key}\n")
    
    # Update permissions on .env file to restrict access
    try:
        env_file.chmod(0o600)  # Owner read/write only
        print("\n.env file created with restricted permissions (600).")
    except:
        print("\n.env file created, but couldn't set restrictive permissions.")
        print("Consider restricting access to this file manually.")

    # Generate configuration for MCP clients
    vs_code_config = {
        "servers": {
            "microsoft-graph": {
                "type": "sse",
                "url": "http://localhost:8000/sse",
                "headers": {
                    "x-api-key": api_key
                }
            }
        }
    }
    
    claude_desktop_config = {
        "mcpServers": {
            "microsoft-graph": {
                "command": "python",
                "args": [
                    "-m",
                    "mcp_microsoft_graph"
                ],
                "env": {
                    "TENANT_ID": tenant_id,
                    "CLIENT_ID": client_id,
                    "CLIENT_SECRET": client_secret,
                    "API_KEYS": api_key
                }
            }
        }
    }
    
    cursor_config = {
        "mcpServers": {
            "microsoft-graph": {
                "command": "python",
                "args": [
                    "-m",
                    "mcp_microsoft_graph"
                ],
                "env": {
                    "TENANT_ID": tenant_id,
                    "CLIENT_ID": client_id,
                    "CLIENT_SECRET": client_secret,
                    "API_KEYS": api_key
                }
            }
        }
    }
    
    # Display configurations
    print("\n=== VS Code Configuration ===")
    print("Run the 'MCP: Add server' command in VS Code and paste:")
    print(json.dumps(vs_code_config, indent=2))
    
    print("\n=== Claude Desktop Configuration ===")
    print("Add this to your Claude Desktop configuration file:")
    print(json.dumps(claude_desktop_config, indent=2))
    
    print("\n=== Cursor Configuration ===")
    print("Add this to your Cursor configuration file:")
    print(json.dumps(cursor_config, indent=2))
    
    print("\nSetup complete! You can now run the server with:")
    print("  python -m mcp_microsoft_graph")
    
    return True

def main():
    parser = argparse.ArgumentParser(description="Setup the Microsoft Graph MCP Server")
    args = parser.parse_args()
    
    try:
        setup_mcp_server()
    except KeyboardInterrupt:
        print("\nSetup canceled.")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 
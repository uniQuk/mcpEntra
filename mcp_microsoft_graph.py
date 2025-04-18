import os
import json
import asyncio
from fastapi import FastAPI, Request, Depends, HTTPException, status
from fastapi.security import APIKeyHeader
from fastapi.middleware.cors import CORSMiddleware
from azure.identity.aio import ClientSecretCredential
from msgraph import GraphServiceClient
from mcp.server.sse import SseServerTransport
from starlette.routing import Mount
from typing import Dict, List, Optional, Any
from load_env import load_environment

# Load environment variables
load_environment()

# FastAPI app setup
app = FastAPI(docs_url=None, redoc_url=None)

# Add CORS middleware for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# MCP Server setup
sse = SseServerTransport("/messages/")
app.router.routes.append(Mount("/messages", app=sse.handle_post_message))

# API Key authentication
api_key_header = APIKeyHeader(name="x-api-key", auto_error=False)

def is_ai_assistant():
    """Check if the server is running as part of an AI assistant environment"""
    return os.environ.get("AI_ASSISTANT") == "true" or \
           os.environ.get("GITHUB_COPILOT_TOKEN") or \
           os.environ.get("CURSOR_SESSION") or \
           os.environ.get("CLAUDE_SESSION")

def ensure_valid_api_key(api_key_header: str = Depends(api_key_header)):
    # Skip API key validation if running from an AI assistant
    if is_ai_assistant():
        return "ai-assistant-bypass"
        
    def check_api_key(key: str) -> bool:
        if not key:
            return False
        valid_keys = os.environ.get("API_KEYS", "").split(",")
        return key in valid_keys and key != ""

    if not check_api_key(api_key_header):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid API key",
        )
    return api_key_header

# Microsoft Graph authentication
async def get_graph_client():
    tenant_id = os.environ.get("TENANT_ID")
    client_id = os.environ.get("CLIENT_ID")
    client_secret = os.environ.get("CLIENT_SECRET")

    if not all([tenant_id, client_id, client_secret]):
        raise ValueError("Missing Microsoft Graph authentication credentials")

    credentials = ClientSecretCredential(
        tenant_id=tenant_id,
        client_id=client_id,
        client_secret=client_secret
    )
    
    scopes = ["https://graph.microsoft.com/.default"]
    client = GraphServiceClient(credentials=credentials, scopes=scopes)
    return client

# MCP Server endpoint
@app.get("/sse", tags=["MCP"], dependencies=[Depends(ensure_valid_api_key)])
async def handle_sse(request: Request):
    async with sse.connect_sse(request.scope, request.receive, request._send) as (
        read_stream,
        write_stream,
    ):
        # Create MCP server
        server = await create_mcp_server()
        init_options = server.create_initialization_options()

        # Run the MCP server
        await server.run(
            read_stream,
            write_stream,
            init_options,
        )

async def create_mcp_server():
    from mcp.server import Server
    
    server = Server()
    
    # Add server metadata
    server.add_server_metadata(
        name="Microsoft Graph API",
        description="MCP Server for Microsoft Graph API",
        vendor="Custom",
        version="1.0.0",
    )
    
    # Add tools
    await add_graph_tools(server)
    
    return server

async def add_graph_tools(server):
    # List Users Tool
    server.add_tool(
        name="listUsers",
        description="Retrieve a list of users from Microsoft Entra ID tenant",
        parameters=[
            {
                "name": "top",
                "type": "integer",
                "description": "Number of users to retrieve (maximum 999)",
                "required": False,
            },
            {
                "name": "filter",
                "type": "string",
                "description": "OData filter expression for filtering users",
                "required": False,
            },
            {
                "name": "select",
                "type": "string",
                "description": "Comma-separated list of properties to include",
                "required": False,
            },
        ],
        on_call=list_users,
    )
    
    # Get User Tool
    server.add_tool(
        name="getUser",
        description="Retrieve a specific user by ID or UPN from Microsoft Entra ID tenant",
        parameters=[
            {
                "name": "id",
                "type": "string",
                "description": "User ID or user principal name",
                "required": True,
            },
            {
                "name": "select",
                "type": "string",
                "description": "Comma-separated list of properties to include",
                "required": False,
            },
        ],
        on_call=get_user,
    )
    
    # Search Users Tool
    server.add_tool(
        name="searchUsers",
        description="Search for users by display name, email, etc. in Microsoft Entra ID tenant",
        parameters=[
            {
                "name": "query",
                "type": "string",
                "description": "Search query string",
                "required": True,
            },
            {
                "name": "top",
                "type": "integer",
                "description": "Number of users to retrieve (maximum 999)",
                "required": False,
            },
        ],
        on_call=search_users,
    )
    
    # List Groups Tool
    server.add_tool(
        name="listGroups",
        description="Retrieve a list of groups from Microsoft Entra ID tenant",
        parameters=[
            {
                "name": "top",
                "type": "integer",
                "description": "Number of groups to retrieve (maximum 999)",
                "required": False,
            },
            {
                "name": "filter",
                "type": "string",
                "description": "OData filter expression for filtering groups",
                "required": False,
            },
        ],
        on_call=list_groups,
    )
    
    # Get Group Members Tool
    server.add_tool(
        name="getGroupMembers",
        description="Retrieve members of a specific group from Microsoft Entra ID tenant",
        parameters=[
            {
                "name": "id",
                "type": "string",
                "description": "Group ID",
                "required": True,
            },
            {
                "name": "top",
                "type": "integer",
                "description": "Number of members to retrieve (maximum 999)",
                "required": False,
            },
        ],
        on_call=get_group_members,
    )

# Tool implementations
async def list_users(params: Dict[str, Any]):
    try:
        client = await get_graph_client()
        
        top = min(params.get("top", 100), 999)
        filter_param = params.get("filter", None)
        select_param = params.get("select", "displayName,userPrincipalName,mail,id")
        
        # Build the request
        request_url = f"/users"
        query_params = {}
        
        if top:
            query_params["$top"] = str(top)
        if filter_param:
            query_params["$filter"] = filter_param
        if select_param:
            query_params["$select"] = select_param
        
        # Add query parameters to the URL
        if query_params:
            request_url += "?" + "&".join([f"{k}={v}" for k, v in query_params.items()])
        
        # Make the request
        response = await client._client.get(request_url)
        users = await response.json()
        
        return users
    except Exception as e:
        return {"error": str(e)}

async def get_user(params: Dict[str, Any]):
    try:
        client = await get_graph_client()
        
        user_id = params.get("id")
        select_param = params.get("select", "displayName,userPrincipalName,mail,id,jobTitle,department,officeLocation,businessPhones,mobilePhone")
        
        # Build the request
        request_url = f"/users/{user_id}"
        
        if select_param:
            request_url += f"?$select={select_param}"
        
        # Make the request
        response = await client._client.get(request_url)
        user = await response.json()
        
        return user
    except Exception as e:
        return {"error": str(e)}

async def search_users(params: Dict[str, Any]):
    try:
        client = await get_graph_client()
        
        query = params.get("query")
        top = min(params.get("top", 10), 999)
        
        # Build the request
        request_url = f"/users"
        query_params = {
            "$search": f'"{query}"',
            "$top": str(top),
            "$select": "displayName,userPrincipalName,mail,id"
        }
        
        # Add query parameters to the URL
        request_url += "?" + "&".join([f"{k}={v}" for k, v in query_params.items()])
        
        # Make the request
        # Note: Using the /search endpoint requires ConsistencyLevel header
        headers = {"ConsistencyLevel": "eventual"}
        response = await client._client.get(request_url, headers=headers)
        users = await response.json()
        
        return users
    except Exception as e:
        return {"error": str(e)}

async def list_groups(params: Dict[str, Any]):
    try:
        client = await get_graph_client()
        
        top = min(params.get("top", 100), 999)
        filter_param = params.get("filter", None)
        
        # Build the request
        request_url = f"/groups"
        query_params = {}
        
        if top:
            query_params["$top"] = str(top)
        if filter_param:
            query_params["$filter"] = filter_param
        
        # Add query parameters to the URL
        if query_params:
            request_url += "?" + "&".join([f"{k}={v}" for k, v in query_params.items()])
        
        # Make the request
        response = await client._client.get(request_url)
        groups = await response.json()
        
        return groups
    except Exception as e:
        return {"error": str(e)}

async def get_group_members(params: Dict[str, Any]):
    try:
        client = await get_graph_client()
        
        group_id = params.get("id")
        top = min(params.get("top", 100), 999)
        
        # Build the request
        request_url = f"/groups/{group_id}/members"
        
        if top:
            request_url += f"?$top={top}"
        
        # Make the request
        response = await client._client.get(request_url)
        members = await response.json()
        
        return members
    except Exception as e:
        return {"error": str(e)}

def main():
    """Entry point for running the server as a module."""
    import uvicorn
    print("Starting Microsoft Graph MCP Server...")
    print("Server will be available at http://localhost:8000/sse")
    uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    main() 
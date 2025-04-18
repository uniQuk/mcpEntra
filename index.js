/**
 * Microsoft Graph MCP Server for AI assistants
 */

// This is just a wrapper to start the Python server
module.exports = {
  /**
   * Start the MCP server
   * @param {Object} options - Configuration options
   * @param {string} options.tenantId - Microsoft Entra ID tenant ID
   * @param {string} options.clientId - Microsoft Entra ID client ID
   * @param {string} options.clientSecret - Microsoft Entra ID client secret
   * @param {string} options.apiKey - API key for the MCP server (optional for AI assistants)
   * @returns {ChildProcess} - The server process
   */
  start: function(options = {}) {
    const { spawn } = require('cross-spawn');
    const path = require('path');
    const fs = require('fs');
    const dotenv = require('dotenv');
    
    // Check if running with an AI assistant
    const isAIAssistant = () => {
      return process.env.GITHUB_COPILOT_TOKEN || 
             process.env.CURSOR_SESSION || 
             process.env.CLAUDE_SESSION ||
             process.env.AI_ASSISTANT;
    };
    
    // Set AI_ASSISTANT flag if detected
    if (isAIAssistant() && !process.env.AI_ASSISTANT) {
      process.env.AI_ASSISTANT = "true";
    }
    
    // Set environment variables if provided
    if (options.tenantId) process.env.TENANT_ID = options.tenantId;
    if (options.clientId) process.env.CLIENT_ID = options.clientId;
    if (options.clientSecret) process.env.CLIENT_SECRET = options.clientSecret;
    if (options.apiKey) process.env.API_KEYS = options.apiKey;
    
    // Find Python executable
    const pythonCommand = process.platform === 'win32' ? 'python' : 'python3';
    
    // Path to the Python script
    const scriptPath = path.join(__dirname, 'mcp_microsoft_graph.py');
    
    // Run the MCP server
    const server = spawn(pythonCommand, [scriptPath], {
      stdio: 'inherit',
      env: process.env
    });
    
    return server;
  }
}; 
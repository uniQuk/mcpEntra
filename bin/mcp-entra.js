#!/usr/bin/env node

/**
 * Microsoft Graph MCP Server CLI
 */

const spawn = require('cross-spawn');
const path = require('path');
const fs = require('fs-extra');
const readline = require('readline');
const crypto = require('crypto');

// Path to the Python script
const scriptPath = path.join(__dirname, '..', 'mcp_microsoft_graph.py');
const setupPath = path.join(__dirname, '..', 'setup_mcp.py');
const envPath = path.join(__dirname, '..', '.env');

// Check if Python is installed
function checkPythonInstallation() {
  const pythonCommand = process.platform === 'win32' ? 'python' : 'python3';
  try {
    const result = spawn.sync(pythonCommand, ['--version']);
    if (result.status !== 0) {
      throw new Error('Python not found');
    }
    return pythonCommand;
  } catch (error) {
    console.error('Error: Python 3.8+ is required but not found on your system.');
    console.error('Please install Python from https://www.python.org/downloads/');
    process.exit(1);
  }
}

// Install Python dependencies
function installPythonDependencies() {
  const pythonCommand = checkPythonInstallation();
  const requirementsPath = path.join(__dirname, '..', 'requirements.txt');
  
  console.log('Installing Python dependencies...');
  const installResult = spawn.sync(pythonCommand, ['-m', 'pip', 'install', '-r', requirementsPath], {
    stdio: 'inherit'
  });
  
  if (installResult.status !== 0) {
    console.error('Failed to install Python dependencies.');
    process.exit(1);
  }
}

// Create a readline interface for user input
function createPrompt() {
  return readline.createInterface({
    input: process.stdin,
    output: process.stdout
  });
}

// Check if running as part of an AI assistant
function isRunningWithAI() {
  // Check common environment variables set by AI assistants
  return process.env.GITHUB_COPILOT_TOKEN || 
         process.env.CURSOR_SESSION || 
         process.env.CLAUDE_SESSION ||
         process.env.AI_ASSISTANT;
}

// Setup environment if not already configured
async function setup() {
  // Check if .env file exists
  if (fs.existsSync(envPath)) {
    return;
  }
  
  console.log('\n=== Microsoft Graph MCP Server Setup ===\n');
  console.log('This script will guide you through setting up the Microsoft Graph MCP Server.');
  console.log('You\'ll need to provide credentials for your Microsoft Entra ID tenant.');
  console.log('\nIMPORTANT: Make sure you have created an app registration in Microsoft Entra ID');
  console.log('with the necessary permissions (User.Read.All, Group.Read.All, etc.)\n');
  
  const rl = createPrompt();
  
  const question = (query) => new Promise((resolve) => rl.question(query, resolve));
  
  try {
    const tenantId = await question('Enter your Microsoft Entra ID Tenant ID: ');
    const clientId = await question('Enter your App Registration Client ID: ');
    const clientSecret = await question('Enter your App Registration Client Secret: ');
    
    // Generate a random API key only if not running with an AI assistant
    let apiKey = '';
    let apiKeyMessage = '';
    
    if (!isRunningWithAI()) {
      apiKey = crypto.randomBytes(32).toString('base64url');
      console.log(`\nGenerated API key: ${apiKey}`);
      console.log('This key will be used to secure your MCP server. Keep it safe!');
      apiKeyMessage = `\n# API Keys for accessing the MCP server\nAPI_KEYS=${apiKey}\n`;
    } else {
      console.log('\nRunning with an AI assistant - API key security bypassed.');
      apiKeyMessage = "\n# API Keys disabled when running with AI assistant\n# API_KEYS=\n";
    }
    
    // Create .env file
    const envContent = `# Microsoft Entra ID App Registration credentials
TENANT_ID=${tenantId}
CLIENT_ID=${clientId}
CLIENT_SECRET=${clientSecret}
${apiKeyMessage}`;
    
    fs.writeFileSync(envPath, envContent, { mode: 0o600 });
    console.log('\n.env file created with restricted permissions (600).');
    
    // Generate configuration examples for MCP clients
    const vsCodeConfig = {
      "servers": {
        "microsoft-graph": {
          "type": "sse",
          "url": "http://localhost:8000/sse",
          "headers": isRunningWithAI() ? {} : { "x-api-key": apiKey }
        }
      }
    };
    
    const claudeDesktopConfig = {
      "mcpServers": {
        "microsoft-graph": {
          "command": "npx",
          "args": [
            "-y",
            "@mcp/entra"
          ],
          "env": {
            "TENANT_ID": tenantId,
            "CLIENT_ID": clientId,
            "CLIENT_SECRET": clientSecret,
            "AI_ASSISTANT": "true"
          }
        }
      }
    };
    
    const cursorConfig = {
      "mcpServers": {
        "microsoft-graph": {
          "command": "npx",
          "args": [
            "-y",
            "@mcp/entra"
          ],
          "env": {
            "TENANT_ID": tenantId,
            "CLIENT_ID": clientId,
            "CLIENT_SECRET": clientSecret,
            "AI_ASSISTANT": "true"
          }
        }
      }
    };
    
    // Display configurations
    console.log('\n=== VS Code Configuration ===');
    console.log('Run the \'MCP: Add server\' command in VS Code and paste:');
    console.log(JSON.stringify(vsCodeConfig, null, 2));
    
    console.log('\n=== Claude Desktop Configuration ===');
    console.log('Add this to your Claude Desktop configuration file:');
    console.log(JSON.stringify(claudeDesktopConfig, null, 2));
    
    console.log('\n=== Cursor Configuration ===');
    console.log('Add this to your Cursor configuration file:');
    console.log(JSON.stringify(cursorConfig, null, 2));
    
  } finally {
    rl.close();
  }
}

// Main function
async function main() {
  try {
    const pythonCommand = checkPythonInstallation();
    installPythonDependencies();
    await setup();
    
    console.log('\nStarting Microsoft Graph MCP Server...');
    
    // Set AI_ASSISTANT environment variable if detected
    if (isRunningWithAI() && !process.env.AI_ASSISTANT) {
      process.env.AI_ASSISTANT = "true";
    }
    
    // Run the MCP server
    const server = spawn(pythonCommand, [scriptPath], {
      stdio: 'inherit',
      env: process.env
    });
    
    server.on('close', (code) => {
      if (code !== 0) {
        console.error(`Server exited with code ${code}`);
      }
      process.exit(code);
    });
    
    // Handle termination signals
    process.on('SIGINT', () => {
      console.log('\nShutting down server...');
      server.kill('SIGINT');
    });
    
    process.on('SIGTERM', () => {
      console.log('\nShutting down server...');
      server.kill('SIGTERM');
    });
    
  } catch (error) {
    console.error('Error:', error.message);
    process.exit(1);
  }
}

// Run the main function
main(); 
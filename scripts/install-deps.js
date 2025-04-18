#!/usr/bin/env node

/**
 * Script to install Python dependencies during npm installation
 */

const spawn = require('cross-spawn');
const path = require('path');
const fs = require('fs');

console.log('Installing Python dependencies for Microsoft Graph MCP Server...');

// Find Python executable
const pythonCommand = process.platform === 'win32' ? 'python' : 'python3';

// Check if Python is installed
try {
  const result = spawn.sync(pythonCommand, ['--version']);
  if (result.status !== 0) {
    console.error('Python not found. Skipping Python dependency installation.');
    console.error('Please install Python 3.8+ manually and run:');
    console.error('  pip install -r requirements.txt');
    process.exit(0);
  }
} catch (error) {
  console.error('Python not found. Skipping Python dependency installation.');
  console.error('Please install Python 3.8+ manually and run:');
  console.error('  pip install -r requirements.txt');
  process.exit(0);
}

// Path to the requirements.txt file
const requirementsPath = path.join(__dirname, '..', 'requirements.txt');

// Install Python dependencies
try {
  const installResult = spawn.sync(pythonCommand, ['-m', 'pip', 'install', '-r', requirementsPath], {
    stdio: 'inherit'
  });
  
  if (installResult.status !== 0) {
    console.error('Failed to install Python dependencies.');
    console.error('Please install them manually:');
    console.error('  pip install -r requirements.txt');
    process.exit(1);
  }
  
  console.log('Python dependencies installed successfully.');
} catch (error) {
  console.error('Error installing Python dependencies:', error.message);
  console.error('Please install them manually:');
  console.error('  pip install -r requirements.txt');
  process.exit(1);
} 
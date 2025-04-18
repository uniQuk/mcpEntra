#!/usr/bin/env python3
"""
Microsoft Graph MCP Server Installer

This script clones the repository and installs all the requirements
for the Microsoft Graph MCP Server.
"""
import os
import sys
import subprocess
import tempfile
import shutil
from pathlib import Path

# GitHub repository URL
REPO_URL = "https://github.com/your-username/mcp-graph-server.git"  # Change this to your actual repo
INSTALL_DIR = Path.home() / "mcp-graph-server"

def check_requirements():
    """Check if required tools are installed."""
    requirements = ["git", "python"]
    missing = []
    
    for req in requirements:
        try:
            subprocess.run([req, "--version"], 
                           stdout=subprocess.PIPE, 
                           stderr=subprocess.PIPE, 
                           check=True)
        except (subprocess.SubprocessError, FileNotFoundError):
            missing.append(req)
    
    if missing:
        print(f"Error: The following requirements are missing: {', '.join(missing)}")
        print("Please install them and try again.")
        return False
    return True

def install_server():
    """Clone the repository and install requirements."""
    print("\n=== Microsoft Graph MCP Server Installer ===\n")
    
    # Check if install directory already exists
    if INSTALL_DIR.exists():
        print(f"Installation directory already exists: {INSTALL_DIR}")
        response = input("Do you want to overwrite it? (y/n): ").strip().lower()
        if response != 'y':
            print("Installation canceled.")
            return False
        shutil.rmtree(INSTALL_DIR)
    
    print(f"Installing to: {INSTALL_DIR}")
    
    # Create installation directory
    INSTALL_DIR.mkdir(parents=True, exist_ok=True)
    
    # Clone repository
    print("\nCloning repository...")
    try:
        subprocess.run(["git", "clone", REPO_URL, str(INSTALL_DIR)], 
                       check=True, 
                       stdout=subprocess.PIPE, 
                       stderr=subprocess.PIPE)
    except subprocess.SubprocessError as e:
        print(f"Error cloning repository: {e}")
        return False
    
    # Install requirements
    print("\nInstalling Python dependencies...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", 
                        str(INSTALL_DIR / "requirements.txt")], 
                       check=True)
    except subprocess.SubprocessError as e:
        print(f"Error installing dependencies: {e}")
        return False

    # Add to PATH if not already there
    bin_dir = Path.home() / ".local" / "bin"
    bin_dir.mkdir(parents=True, exist_ok=True)
    
    script_path = bin_dir / "mcp-graph-server"
    
    with open(script_path, 'w') as f:
        f.write(f"""#!/usr/bin/env python3
import sys
import os

# Add the installation directory to the Python path
sys.path.insert(0, "{INSTALL_DIR}")

# Change to the installation directory
os.chdir("{INSTALL_DIR}")

# Import and run the server
from mcp_microsoft_graph import main
main()
""")
    
    # Make the script executable
    script_path.chmod(0o755)
    
    print("\nRunning setup script...")
    try:
        subprocess.run([sys.executable, str(INSTALL_DIR / "setup_mcp.py")], check=True)
    except subprocess.SubprocessError as e:
        print(f"Error running setup: {e}")
        return False

    print("\n=== Installation Complete ===")
    print(f"The server has been installed to: {INSTALL_DIR}")
    print(f"A launcher script has been added to: {script_path}")
    
    # Check if ~/.local/bin is in PATH
    if str(bin_dir) not in os.environ.get("PATH", ""):
        print("\nNOTE: You may need to add the following to your shell profile:")
        print(f"export PATH=\"$PATH:{bin_dir}\"")
    
    print("\nYou can now run the server with the command:")
    print("  mcp-graph-server")
    
    return True

def main():
    """Main entry point."""
    if not check_requirements():
        return 1
    
    try:
        success = install_server()
        return 0 if success else 1
    except KeyboardInterrupt:
        print("\nInstallation canceled.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 
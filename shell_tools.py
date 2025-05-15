import subprocess
import os
from typing import Dict, Any

ALLOWED_COMMANDS = [
    # Basic file & directory operations
    "ls", "pwd", "cd", "mkdir", "touch", "rm", "cp", "mv", "cat", "head", "tail", 
    "echo", "find", "grep", "wc", "less", "more",
    
    # Git commands
    "git", "git status", "git add", "git commit", "git push", "git pull", "git checkout",
    "git branch", "git log", "git diff", "git clone", "git fetch", "git merge",
    "git stash", "git reset",
    
    # Python related
    "python", "python3", "pip", "pip3", "pytest", "venv",
    
    # Node related
    "node", "npm", "npx", "yarn",
    
    # System info
    "ps", "top", "htop", "df", "du", "free", "whoami", "which", "whereis",
    
    # Network
    "curl", "wget", "ping", "netstat", "ssh",
    
    # Package managers
    "apt", "apt-get", "brew", "yum", "dnf"
]

def is_command_allowed(command_str: str) -> bool:
    """Check if the command is allowed to run."""
    # Extract the base command (before any spaces or special chars)
    parts = command_str.split()
    if not parts:
        return False
        
    base_command = parts[0]
    
    # Handle git commands (special case)
    if base_command == "git" and len(parts) > 1:
        git_subcommand = f"git {parts[1]}"
        if git_subcommand in ALLOWED_COMMANDS:
            return True
    
    # Check if base command is in allowed list
    return base_command in ALLOWED_COMMANDS

def execute_bash(params: Dict[str, Any]) -> str:
    """Execute bash commands in a shell session with confirmation."""
    command = params.get("command", "")
    
    if not command:
        return "Error: No command provided"
    
    if not is_command_allowed(command):
        return f"Error: Command '{command.split()[0]}' is not allowed for security reasons. Allowed commands include: {', '.join(ALLOWED_COMMANDS)}"
    
    # Get confirmation
    print(f"\n\033[93m⚠️ BASH COMMAND CONFIRMATION ⚠️\033[0m")
    print(f"Command: {command}")
    confirmation = input("Type 'y' to execute or anything else to cancel: ")
    
    if confirmation.lower() != 'y':
        return "Command execution cancelled by user."
    
    # Execute command
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=30  # 30 second timeout
        )
        
        output = result.stdout
        error = result.stderr
        exit_code = result.returncode
        
        response = f"Exit Code: {exit_code}\n"
        
        if output:
            response += f"\nOutput:\n{output}"
        
        if error:
            response += f"\nError:\n{error}"
            
        return response
    except subprocess.TimeoutExpired:
        return "Error: Command execution timed out after 30 seconds"
    except Exception as e:
        return f"Error executing command: {str(e)}"

BASH_SCHEMA = {
    "type": "object",
    "properties": {
        "command": {
            "type": "string",
            "description": "The bash command to execute"
        }
    },
    "required": ["command"]
}
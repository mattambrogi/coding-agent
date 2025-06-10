# main.py
import os
import sys
import argparse
from dotenv import load_dotenv
from agent import Agent
from tool import Tool
from llm_providers import create_provider
from file_tools import (
    read_file,
    list_files,
    edit_file,
    create_new_file,
    grep_tool,
    glob_tool,
    update_todos,
    READ_FILE_SCHEMA,
    LIST_FILES_SCHEMA,
    EDIT_FILE_SCHEMA,
    CREATE_FILE_SCHEMA,
    GREP_SCHEMA,
    GLOB_SCHEMA,
    UPDATE_TODOS_SCHEMA
)
from shell_tools import execute_bash, BASH_SCHEMA

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Coding Agent with multi-provider LLM support")
    parser.add_argument("--provider", choices=["anthropic", "openai"], 
                       help="LLM provider to use (default: from LLM_PROVIDER env var or 'anthropic')")
    args = parser.parse_args()
    
    # Load environment variables
    load_dotenv()
    
    # Determine provider
    provider_type = args.provider or os.environ.get("LLM_PROVIDER", "anthropic").lower()
    
    # Get appropriate API key
    if provider_type == "anthropic":
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            print("Error: ANTHROPIC_API_KEY environment variable not set")
            print("Please set your Anthropic API key with:")
            print("export ANTHROPIC_API_KEY='your-key-here'")
            return
    elif provider_type == "openai":
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            print("Error: OPENAI_API_KEY environment variable not set")
            print("Please set your OpenAI API key with:")
            print("export OPENAI_API_KEY='your-key-here'")
            return
    else:
        print(f"Error: Unsupported provider '{provider_type}'. Supported providers: anthropic, openai")
        return
    
    # Initialize LLM provider
    try:
        llm_provider = create_provider(provider_type, api_key)
        print(f"Using {provider_type.upper()} provider")
    except Exception as e:
        print(f"Error initializing {provider_type} provider: {e}")
        return
    
    # Create tools
    tools = [
        Tool(
            name="read_file",
            description="Read the contents of a given relative file path. Use this when you want to see what's inside a file. Do not use this with directory names.",
            input_schema=READ_FILE_SCHEMA,
            function=read_file
        ),
        Tool(
            name="list_files",
            description="""List files and directories at a given path. If no path is provided, lists files in the current directory. To list root files you may need to pass "." as the path""",
            input_schema=LIST_FILES_SCHEMA,
            function=list_files
        ),
        Tool(
            name="edit_file",
            description="""Make edits to a text file.

Replaces 'old_str' with 'new_str' in the given file. 'old_str' and 'new_str' MUST be different from each other.

This tool also takes an expected_replacements parameter. This is the number of replacements you expect to make. If the number of replacements is not as expected, the tool will return an error. This helps prevent the tool from making extra unintended replacements.

If the file specified with path doesn't exist, it will be created (when old_str is empty).
""",
            input_schema=EDIT_FILE_SCHEMA,
            function=edit_file
        ),
        Tool(
            name="create_file",
            description="Create a new file with the given content. This is specifically for creating new files, while edit_file can be used for both creating and modifying files.",
            input_schema=CREATE_FILE_SCHEMA,
            function=create_new_file
        ),
        Tool(
            name="glob",
            description="""Search for files using a glob pattern.
Use this tool to find files matching specific patterns, excluding certain directories like .git, __pycache__, and node_modules.
""",
            input_schema=GLOB_SCHEMA,
            function=glob_tool
        ),
        Tool(
            name="grep",
            description="""Search file contents using regular expressions.
Use this to find text patterns within files. Provides file paths, line numbers, and matching lines.
For searching file paths by pattern, use list_files instead.
Use this when you need to locate specific code, functions, variables, or text within the codebase.""",
            input_schema=GREP_SCHEMA,
            function=grep_tool
        ),
        Tool(
            name="execute_bash",
            description="""Execute bash commands in a shell session.
Use this for running system commands and git operations.
Commands are limited to a set of approved operations for security.
Examples of useful commands:
- File operations: ls -la, find . -name "*.py", cat file.txt
- Git operations: git status, git add ., git commit -m "message", git diff
- Python: python script.py, pip install package
- Node.js: npm install, node script.js

Each command requires confirmation before execution.
""",
            input_schema=BASH_SCHEMA,
            function=execute_bash
        ),
        Tool(
            name="update_todos",
            description=""" Create or update todo list for complex tasks. Use this to track progress on multi-step work.
            
Actions:
- set: Create or update the todo list with your own format
- get: Display current todos  
- clear: Remove all todos

You control the format - use markdown, emojis, whatever works best for the task. The primary purpose of this tool is to help you as the agent to keep track of your progress on complex tasks. It also helps communicate intent to the user.""",
            input_schema=UPDATE_TODOS_SCHEMA,
            function=update_todos
        )
    ]
    
    # Create and run the agent
    agent = Agent(llm_provider, tools)
    agent.run()

if __name__ == "__main__":
    main()
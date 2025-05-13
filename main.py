# main.py
import os
import anthropic
from dotenv import load_dotenv


from agent import Agent
from tool import Tool
from file_tools import (
    read_file,
    list_files,
    edit_file,
    create_new_file,
    grep_tool,
    READ_FILE_SCHEMA,
    LIST_FILES_SCHEMA,
    EDIT_FILE_SCHEMA,
    CREATE_FILE_SCHEMA,
    GREP_SCHEMA
)

def main():
    # Check for API key
    load_dotenv()

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("Error: ANTHROPIC_API_KEY environment variable not set")
        print("Please set your Anthropic API key with:")
        print("export ANTHROPIC_API_KEY='your-key-here'")
        return
    
    # Initialize Anthropic client
    client = anthropic.Anthropic(api_key=api_key)
    
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
            description="List files and directories at a given path. If no path is provided, lists files in the current directory.",
            input_schema=LIST_FILES_SCHEMA,
            function=list_files
        ),
        Tool(
            name="edit_file",
            description="""Make edits to a text file.

Replaces 'old_str' with 'new_str' in the given file. 'old_str' and 'new_str' MUST be different from each other.

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
            name="grep",
            description="""Search file contents using regular expressions.
Use this to find text patterns within files. Provides file paths, line numbers, and matching lines.
For searching file paths by pattern, use list_files instead.
Use this when you need to locate specific code, functions, variables, or text within the codebase.""",
            input_schema=GREP_SCHEMA,
            function=grep_tool
        )
    ]
    
    # Create and run the agent
    agent = Agent(client, tools)
    agent.run()

if __name__ == "__main__":
    main()
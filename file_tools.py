# file_tools.py
import os
import json
import glob
import ast  # Added for parsing Python literal strings when edits are provided as a string
from typing import Dict, Any, List, TypedDict

class EditOperation(TypedDict):
    old_str: str
    new_str: str
    expected_replacements: int

class EditFileParams(TypedDict):
    path: str
    old_str: str
    new_str: str
    expected_replacements: int

class MultiEditParams(TypedDict):
    path: str
    edits: List[EditOperation]

def read_file(params: Dict[str, Any]) -> str:
    """Read the contents of a file."""
    path = params.get("path", "")
    if not path:
        return "Error: No file path provided"
    
    try:
        with open(path, 'r', encoding='utf-8') as file:
            return file.read()
    except Exception as e:
        return f"Error reading file: {str(e)}"

def list_files(params: Dict[str, Any]) -> str:
    """List files in a directory."""
    path = params.get("path", ".")
    
    try:
        files = []
        for item in os.listdir(path):
            full_path = os.path.join(path, item)
            if os.path.isdir(full_path):
                files.append(f"{item}/")
            else:
                files.append(item)
        return json.dumps(files)
    except Exception as e:
        return f"Error listing files: {str(e)}"

def edit_file(params: EditFileParams) -> str:
    """Edit a file by replacing text."""
    path = params.get("path", "")
    old_str = params.get("old_str", "")
    new_str = params.get("new_str", "")
    expected_replacements = params.get("expected_replacements", 1)
    
    if not path or old_str == new_str:
        return "Error: Invalid parameters"
    
    try:
        # Create new file if it doesn't exist and old_str is empty
        if not os.path.exists(path) and old_str == "":
            directory = os.path.dirname(path)
            if directory and not os.path.exists(directory):
                os.makedirs(directory)
                
            with open(path, 'w', encoding='utf-8') as file:
                file.write(new_str)
            return f"Successfully created file {path}"
        
        # Edit existing file
        with open(path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        # Count actual occurrences
        actual_count = content.count(old_str)
        if actual_count == 0:
            return "Error: old_str not found in file"
        
        if actual_count != expected_replacements:
            return f"Error: Expected {expected_replacements} replacements but found {actual_count}"
        
        # Replace text (limit to expected count for safety)
        new_content = content.replace(old_str, new_str, expected_replacements)
        
        # Write the new content
        with open(path, 'w', encoding='utf-8') as file:
            file.write(new_content)
            
        return f"OK - Made {expected_replacements} replacement(s)"
    except Exception as e:
        return f"Error editing file: {str(e)}"

def multi_edit_file(params: MultiEditParams) -> str:
    """Apply multiple edits atomically with sequential validation."""
    
    path = params.get("path", "")
    edits = params.get("edits")  # May be list or string

    # Basic path check first
    if not path:
        error_msg = _generate_multi_edit_help()
        return error_msg

    # Now handle string-encoded edits
    if isinstance(edits, str):
        try:
            # Try JSON first
            edits_parsed = json.loads(edits)
        except json.JSONDecodeError:
            try:
                # Try Python literal (handles single quotes & multiline)
                edits_parsed = ast.literal_eval(edits)
            except Exception as e:
                error_msg = f"{_generate_multi_edit_help()}\n\nSpecific issue: Unable to parse 'edits' string: {str(e)}"
                return error_msg
        edits = edits_parsed

    # Final validation
    if not isinstance(edits, list) or len(edits) == 0:
        error_msg = _generate_multi_edit_help()
        return error_msg
    
    try:
        # Read original content
        if not os.path.exists(path):
            error_msg = f"Error: File '{path}' does not exist"
            return error_msg
            
        with open(path, 'r', encoding='utf-8') as file:
            working_content = file.read()
        
        # Validate and apply each edit sequentially
        for i, edit in enumerate(edits):
            old_str = edit.get("old_str", "")
            new_str = edit.get("new_str", "")
            expected_count = edit.get("expected_replacements", 1)
                
            # Count occurrences in CURRENT state
            actual_count = working_content.count(old_str)
            
            if actual_count == 0:
                error_msg = f"Error: Edit {i+1} - '{old_str}' not found (may conflict with previous edits)"
                return error_msg
            
            if actual_count != expected_count:
                error_msg = f"Error: Edit {i+1} - expected {expected_count} replacements, found {actual_count}"
                return error_msg
            
            # Apply edit to working copy
            working_content = working_content.replace(old_str, new_str, expected_count)
        
        # Write final result atomically
        with open(path, 'w', encoding='utf-8') as file:
            file.write(working_content)
        
        success_msg = f"Successfully applied {len(edits)} edits to {path}"
        return success_msg
        
    except Exception as e:
        error_msg = f"Error in multi-edit: {str(e)}"
        return error_msg
    
def create_new_file(params: Dict[str, Any]) -> str:
    """Create a new file with the given content."""
    path = params.get("path", "")
    content = params.get("content", "")
    
    if not path:
        return "Error: No file path provided"
    
    try:
        # Create directory if it doesn't exist
        directory = os.path.dirname(path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory, mode=0o755)
        
        # Write the file
        with open(path, 'w', encoding='utf-8') as file:
            file.write(content)
        
        return f"Successfully created file {path}"
    except Exception as e:
        return f"Error creating file: {str(e)}"

def grep_tool(params: Dict[str, Any]) -> str:
    """Search file contents using regular expressions."""
    pattern = params.get("pattern", "")
    path = params.get("path", ".")
    recursive = params.get("recursive", True)
    
    if not pattern:
        return "Error: No search pattern provided"
    
    try:
        import re
        
        results = []
        
        # Directories to exclude from search
        excluded_dirs = {'venv', '.git', '__pycache__', 'node_modules', '.venv', 'env'}
        
        # Determine which files to search
        if os.path.isfile(path):
            files_to_search = [path]
        else:
            files_to_search = []
            if recursive:
                for root, dirs, files in os.walk(path):
                    # Remove excluded directories from the search
                    dirs[:] = [d for d in dirs if d not in excluded_dirs]
                    for file in files:
                        files_to_search.append(os.path.join(root, file))
            else:
                for item in os.listdir(path):
                    full_path = os.path.join(path, item)
                    if os.path.isfile(full_path):
                        files_to_search.append(full_path)
        
        # Search through files
        for file_path in files_to_search:
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    for line_num, line in enumerate(file, 1):
                        if re.search(pattern, line):
                            results.append({
                                "file": file_path,
                                "line": line_num,
                                "content": line.strip()
                            })
            except UnicodeDecodeError:
                # Skip binary files
                continue
            except Exception as e:
                results.append({
                    "file": file_path,
                    "error": str(e)
                })
        
        if not results:
            return "No matches found"
        
        # Format results
        response = f"Found {len(results)} matches:\n\n"
        for result in results:
            if "error" in result:
                response += f"{result['file']}: ERROR: {result['error']}\n"
            else:
                response += f"{result['file']}:{result['line']}: {result['content']}\n"
                
        return response
    except Exception as e:
        return f"Error performing grep: {str(e)}"

def glob_tool(params: Dict[str, Any]) -> str:
    """Search for files using a pattern."""
    pattern = params.get("pattern", "")
    if not pattern:
        return "Error: No pattern provided"

    try:
        # Exclude specific directories
        excluded_dirs = {'*/.git/*', '*/__pycache__/*', '*/node_modules/*'}
        matched_files = [f for f in glob.glob(pattern, recursive=True) if not any(glob.fnmatch.fnmatch(f, ex) for ex in excluded_dirs)]
        if not matched_files:
            return "No files matched the pattern"
        return json.dumps(matched_files)
    except Exception as e:
        return f"Error in glob operation: {str(e)}"

# Tool schemas
READ_FILE_SCHEMA = {
    "type": "object",
    "properties": {
        "path": {
            "type": "string",
            "description": "The relative path of a file in the working directory."
        }
    },
    "required": ["path"]
}

LIST_FILES_SCHEMA = {
    "type": "object",
    "properties": {
        "path": {
            "type": "string",
            "description": "Optional relative path to list files from. Defaults to current directory if not provided."
        }
    }
}

EDIT_FILE_SCHEMA = {
    "type": "object",
    "properties": {
        "path": {
            "type": "string",
            "description": "The path to the file"
        },
        "old_str": {
            "type": "string",
            "description": "Text to search for - must match exactly"
        },
        "new_str": {
            "type": "string",
            "description": "Text to replace old_str with"
        },
        "expected_replacements": {
            "type": "integer",
            "description": "Number of replacements expected (default: 1)",
            "default": 1
        }
    },
    "required": ["path", "old_str", "new_str"]
}

MULTI_EDIT_SCHEMA = {
    "type": "object",
    "properties": {
        "path": {
            "type": "string",
            "description": "Path to the file to edit"
        },
        "edits": {
            "type": "array",
            "minItems": 1,
            "items": {
                "type": "object",
                "properties": {
                    "old_str": {
                        "type": "string",
                        "description": "Text to find and replace"
                    },
                    "new_str": {
                        "type": "string", 
                        "description": "Text to replace old_str with"
                    },
                    "expected_replacements": {
                        "type": "integer", 
                        "default": 1,
                        "description": "Number of replacements expected (default: 1)"
                    }
                },
                "required": ["old_str", "new_str"],
                "additionalProperties": False
            },
            "description": "Array of edit operations to apply sequentially. Each edit must have old_str (text to find) and new_str (replacement text)."
        }
    },
    "required": ["path", "edits"],
    "additionalProperties": False
}

CREATE_FILE_SCHEMA = {
    "type": "object",
    "properties": {
        "path": {
            "type": "string",
            "description": "The path where the new file should be created"
        },
        "content": {
            "type": "string",
            "description": "The content to write to the new file"
        }
    },
    "required": ["path", "content"]
}

GREP_SCHEMA = {
    "type": "object",
    "properties": {
        "pattern": {
            "type": "string",
            "description": "Regular expression pattern to search for"
        },
        "path": {
            "type": "string",
            "description": "Path to search within (file or directory)"
        },
        "recursive": {
            "type": "boolean",
            "description": "Whether to search recursively through subdirectories"
        }
    },
    "required": ["pattern"]
}

# Simple in-memory storage for todo list
_todo_state = ""

def update_todos(params: Dict[str, Any]) -> str:
    """Update and display todo list. Let the LLM manage the format and logic."""
    global _todo_state
    action = params.get("action", "")
    content = params.get("content", "")
    if action == "set":
         _todo_state = content
         print(f"\n📋 TODOS UPDATED:\n{content}\n")
         return f"Todo list updated:\n{content}"
    elif action == "get":
         if _todo_state:
             print(f"\n📋 CURRENT TODOS:\n{_todo_state}\n")
             return f"Current todos:\n{_todo_state}"
         else:
             return "No todos currently set."
    elif action == "clear":
         _todo_state = ""
         print("\n📋 TODOS CLEARED\n")
         return "Todo list cleared."
    else:
         return "Error: action must be 'set', 'get', or 'clear'"

# Schema for the glob_tool
GLOB_SCHEMA = {
    "type": "object",
    "properties": {
        "pattern": {
            "type": "string",
            "description": "Glob pattern to search for files"
        }
    },
    "required": ["pattern"]
}

# Simple schema for update_todos
UPDATE_TODOS_SCHEMA = {
    "type": "object",
    "properties": {
        "action": {
            "type": "string",
            "enum": ["set", "get", "clear"],
            "description": "set: update todos with content, get: display current todos, clear: remove all todos"
        },
        "content": {
            "type": "string",
            "description": "Todo list content in any format (for 'set' action)"
        }
    },
    "required": ["action"]
}

def _generate_multi_edit_help() -> str:
    """Generate a helpful error message showing the expected structure for multi_edit_file."""
    return """Error: Invalid parameters for multi_edit_file.

Expected structure:
{
  "path": "string (required) - file to edit",
  "edits": [
    {
      "old_str": "string (required) - text to find and replace",
      "new_str": "string (required) - replacement text", 
      "expected_replacements": "integer (optional, default=1) - number of expected replacements"
    }
  ]
}

Example:
{
  "path": "example.py",
  "edits": [
    {"old_str": "old_function", "new_str": "new_function", "expected_replacements": 1},
    {"old_str": "old_var", "new_str": "new_var", "expected_replacements": 3}
  ]
}"""
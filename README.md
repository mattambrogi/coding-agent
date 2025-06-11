## Coding Agent

A terminal-based coding agent with support for both Anthropic and OpenAI LLM providers.

Inpsiration: 
- Base implementation: https://ampcode.com/how-to-build-an-agent
- Additional tools: Claude Code

## Features

- **Multi-Provider Support**: Works with both Anthropic Claude and OpenAI GPT models
- **File Operations**: Read, write, edit, and search files
- **Shell Commands**: Execute approved bash commands with safety restrictions
- **Tool System**: Extensible tool framework for adding new capabilities

## Setup

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set API Keys**
   
   For Anthropic (default):
   ```bash
   export ANTHROPIC_API_KEY='your-anthropic-key-here'
   ```
   
   For OpenAI:
   ```bash
   export OPENAI_API_KEY='your-openai-key-here'
   ```

3. **Optional: Set Default Provider**
   ```bash
   export LLM_PROVIDER=anthropic  # or "openai"
   ```

## Usage

### Using Anthropic (default)
```bash
python main.py
```

### Using OpenAI
```bash
# Via environment variable
LLM_PROVIDER=openai python main.py

# Via command line argument
python main.py --provider openai
```

### Available Commands
```bash
python main.py --help
```

### Tips for Use
- The agent is capable of working on itself or any other repo on your computer. Simply instruct it which repo to navigate to. It should be able to use the built in bash tool to navigate to, read, and edit files in other repos.
- The Todo tool is useful for complex tasks and will be used by default when the agent deems it appropriate. If you do not want the agent to use this tool as it can clutter the terminal, just instruct it not to.
- Code editing and implementation works well on simple tasks but may struggle on feature level work. Try breaking tasks into smaller sub-tasks.
- Before asking the agent to edit code, it is helpful to prompt it to explore the part of the codebase you are interested in modifying.
- This agent excels at code understanding and search
- Search is done entirely locally and no code will be embedded or indexed elsewhere.


## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `ANTHROPIC_API_KEY` | Your Anthropic API key | Required for Anthropic |
| `OPENAI_API_KEY` | Your OpenAI API key | Required for OpenAI |
| `LLM_PROVIDER` | Default provider (`anthropic` or `openai`) | `anthropic` |

## Provider Support

### Anthropic Claude
- **Models**: claude-3-7-sonnet-20250219
- **Features**: Full tool calling support, conversation management
- **Status**: ✅ Fully supported

### OpenAI GPT
- **Models**: gpt-4o
- **Features**: Full tool calling support with format conversion
- **Status**: ✅ Fully supported

## Architecture

The agent uses a provider abstraction layer that allows seamless switching between LLM providers while maintaining full backward compatibility:

- `llm_providers.py` - Provider abstraction and implementations
- `agent.py` - Core agent logic (provider-agnostic)
- `main.py` - Entry point with provider selection
- `tool.py` - Tool definition framework
- `file_tools.py` - File manipulation tools
- `shell_tools.py` - Bash execution tools

## Tools

### File Operations
- **read_file**: Read contents of a file
- **list_files**: List contents of a directory
- **edit_file**: Modify existing files
- **multi_edit_file**: Apply multiple edits to one file with reduced chance of conflicts
- **create_file**: Create new files
- **grep**: Search file contents using regex
- **glob**: Search for files using glob patterns
  - Supports recursive search
  - Automatically excludes common directories (.git, __pycache__, node_modules)
  - Returns JSON array of matched files
  - *Note: This agent implemented this tool for itself*

### Task Management
- **update_todos**: Manage task tracking for complex operations
  - Actions: set, get, clear
  - Supports custom formatting (markdown, emojis, etc.)
  - Maintains state between operations
  - Useful for tracking progress on multi-step tasks

### Shell Operations
- **execute_bash**: Run approved shell commands
  - File operations (ls, find, cat)
  - Git operations
  - Package management
  - Requires confirmation before execution

## Limitations
- Tool calls are not currently executed in parallel

## Todos
* ✅ Abstract system such that it can work with OpenAI or Anthropic models
* ✅ Add a thinking tool
* ✅ Add glob tool
* ✅ Improve prompting and instructions
* ✅ Add multi-edit tool
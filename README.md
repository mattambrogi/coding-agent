## Coding Agent

A multi-provider coding agent with support for both Anthropic and OpenAI LLM providers.

Inspired by: https://ampcode.com/how-to-build-an-agent

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
- **Models**: gpt-4
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

## Todos
* Add a thinking tool
* Improve prompting and instructions
* ✅ Abstract system such that it can work with OpenAI or Anthropic models
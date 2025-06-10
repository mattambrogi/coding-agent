# agent.py
import json
from typing import List, Dict, Any, Callable, Optional, Union

from tool import Tool
from llm_providers import LLMProvider

class Agent:
    """
    An agent that uses LLM providers with access to tools.
    
    The agent maintains a conversation with the user and the LLM,
    and allows the LLM to execute tools when needed.
    """
    
    def __init__(self, llm_provider: LLMProvider, tools: List[Tool]):
        self.llm_provider = llm_provider
        self.tools = tools
        self.conversation = []
    
    def run(self):
        """Run the agent in a loop, processing user input and LLM responses."""
        print("Chat with AI (use 'ctrl-c' to quit)")
        
        read_user_input = True
        
        try:
            while True:
                if read_user_input:
                    user_input = input("\033[94mYou\033[0m: ")
                    user_message = {"role": "user", "content": [{"type": "text", "text": user_input}]}
                    self.conversation.append(user_message)
                
                # Prepare tools for LLM
                tools = [tool.to_dict() for tool in self.tools]
                
                # Send message to LLM
                system = """You are a coding assistant with access to the following tools:
- read_file (read file contents)
- list_files (list directory contents)
- edit_file (modify files)
- create_file (create new files)
- grep (search file contents)
- execute_bash (run shell commands)
- glob_files (search for files using a pattern)
- update_todos (create or update todo list for complex tasks)

When asked about code or how something works, immediately use these tools to examine the relevant files without asking for permission. Use tools proactively to investigate the codebase and provide accurate, context-specific answers based on the actual code.

For complex tasks (3+ steps), use the update_todos tool to:
1. Create a todo list when starting complex work
2. Update the list as you complete tasks
3. Use any format you prefer (markdown, numbered list, etc.)

Use todos to keep the user informed of your progress on multi-step tasks. Update them frequently as you work.

When asked about code, immediately examine relevant files to provide accurate answers."""

                response = self.llm_provider.create_message(
                    system=system,
                    messages=self.conversation,
                    tools=tools
                )
                
                # Process LLM response
                llm_message = {"role": "assistant", "content": []}
                tool_outputs = []
                
                # Parse response using provider
                content_blocks = self.llm_provider.parse_response(response)
                
                for content_block in content_blocks:
                    if content_block["type"] == "text":
                        print(f"\033[93mAI\033[0m: {content_block['text']}")
                        llm_message["content"].append({"type": "text", "text": content_block["text"]})
                    
                    elif content_block["type"] == "tool_use":
                        # Execute the tool
                        tool_name = content_block["name"]
                        tool_id = content_block["id"]
                        tool_input = content_block["input"]
                        
                        # Find the tool
                        for tool in self.tools:
                            if tool.name == tool_name:
                                result = tool.execute(tool_input)
                                print(f"\033[92mtool\033[0m: {tool_name}({json.dumps(tool_input)})")
                                tool_outputs.append({
                                    "type": "tool_result",
                                    "tool_use_id": tool_id,
                                    "content": result
                                })
                                break
                        else:
                            # Tool not found
                            tool_outputs.append({
                                "type": "tool_result",
                                "tool_use_id": tool_id,
                                "content": "Tool not found"
                            })
                        
                        llm_message["content"].append({
                            "type": "tool_use",
                            "id": tool_id,
                            "name": tool_name,
                            "input": tool_input
                        })
                
                self.conversation.append(llm_message)
                
                # If tools were used, send the results back to LLM
                if tool_outputs:
                    # Format tool results as a single message with multiple content blocks
                    tool_response = {
                        "role": "user",
                        "content": tool_outputs
                    }
                    self.conversation.append(tool_response)
                    read_user_input = False
                else:
                    read_user_input = True
                    
        except KeyboardInterrupt:
            print("\nGoodbye!")
# agent.py
import json
from typing import List, Dict, Any, Callable, Optional, Union
import anthropic

from tool import Tool

class Agent:
    """
    An agent that uses Claude with access to tools.
    
    The agent maintains a conversation with the user and Claude,
    and allows Claude to execute tools when needed.
    """
    
    def __init__(self, client: anthropic.Anthropic, tools: List[Tool]):
        self.client = client
        self.tools = tools
        self.conversation = []
    
    def run(self):
        """Run the agent in a loop, processing user input and Claude's responses."""
        print("Chat with Claude (use 'ctrl-c' to quit)")
        
        read_user_input = True
        
        try:
            while True:
                if read_user_input:
                    user_input = input("\033[94mYou\033[0m: ")
                    user_message = {"role": "user", "content": [{"type": "text", "text": user_input}]}
                    self.conversation.append(user_message)
                
                # Prepare tools for Claude
                tools = [tool.to_dict() for tool in self.tools]
                
                # Send message to Claude
                response = self.client.messages.create(
                    model="claude-3-7-sonnet-20250219",
                    max_tokens=1024,
                    system="You are a helpful assistant with access to tools.",
                    messages=self.conversation,
                    tools=tools
                )
                
                # Process Claude's response
                claude_message = {"role": "assistant", "content": []}
                tool_outputs = []
                
                for content_block in response.content:
                    if content_block.type == "text":
                        print(f"\033[93mClaude\033[0m: {content_block.text}")
                        claude_message["content"].append({"type": "text", "text": content_block.text})
                    
                    elif content_block.type == "tool_use":
                        # Execute the tool
                        tool_name = content_block.name
                        tool_id = content_block.id
                        tool_input = content_block.input
                        
                        # Find the tool
                        for tool in self.tools:
                            if tool.name == tool_name:
                                result = tool.execute(tool_input)
                                print(f"\033[92mtool\033[0m: {tool_name}({json.dumps(tool_input)})")
                                tool_outputs.append({
                                    "type": "tool_result",
                                    "tool_use_id": tool_id,
                                    "output": result
                                })
                                break
                        else:
                            # Tool not found
                            tool_outputs.append({
                                "type": "tool_result",
                                "tool_use_id": tool_id,
                                "output": "Tool not found"
                            })
                        
                        claude_message["content"].append({
                            "type": "tool_use",
                            "id": tool_id,
                            "name": tool_name,
                            "input": tool_input
                        })
                
                self.conversation.append(claude_message)
                
                # If tools were used, send the results back to Claude
                if tool_outputs:
                    # Format tool results as a single message with multiple content blocks
                    tool_response = {
                        "role": "user",
                        "content": [
                            {
                                "type": "tool_result",
                                "tool_use_id": output["tool_use_id"],
                                "content": output["output"]
                            } for output in tool_outputs
                        ]
                    }
                    self.conversation.append(tool_response)
                    read_user_input = False
                else:
                    read_user_input = True
                    
        except KeyboardInterrupt:
            print("\nGoodbye!")
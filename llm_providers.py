# llm_providers.py
import json
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import anthropic
import openai

class LLMProvider(ABC):
    """
    Abstract base class for LLM providers.
    
    Provides a unified interface for different LLM providers (Anthropic, OpenAI, etc.)
    while handling provider-specific message formatting and API calls.
    """
    
    @abstractmethod
    def create_message(self, system: str, messages: List[Dict[str, Any]], tools: List[Dict[str, Any]]) -> Any:
        """
        Create a message request to the LLM provider.
        
        Args:
            system: System prompt
            messages: Conversation history in normalized format
            tools: Available tools in normalized format
            
        Returns:
            Provider-specific response object
        """
        pass
    
    @abstractmethod
    def parse_response(self, response: Any) -> List[Dict[str, Any]]:
        """
        Parse the LLM response into normalized format.
        
        Args:
            response: Provider-specific response object
            
        Returns:
            List of content blocks in normalized format:
            [{"type": "text", "text": "..."} or {"type": "tool_use", "id": "...", "name": "...", "input": {...}}]
        """
        pass

class AnthropicProvider(LLMProvider):
    """
    Anthropic Claude provider implementation.
    
    Wraps the existing Anthropic client and maintains compatibility with
    the current implementation.
    """
    
    def __init__(self, api_key: str):
        self.client = anthropic.Anthropic(api_key=api_key)
    
    def create_message(self, system: str, messages: List[Dict[str, Any]], tools: List[Dict[str, Any]]) -> Any:
        """Create message using Anthropic API."""
        return self.client.messages.create(
            model="claude-3-7-sonnet-20250219",
            max_tokens=1024,
            system=system,
            messages=messages,
            tools=tools
        )
    
    def parse_response(self, response: Any) -> List[Dict[str, Any]]:
        """Parse Anthropic response - no conversion needed as it's already in our target format."""
        content_blocks = []
        
        for content_block in response.content:
            if content_block.type == "text":
                content_blocks.append({
                    "type": "text",
                    "text": content_block.text
                })
            elif content_block.type == "tool_use":
                content_blocks.append({
                    "type": "tool_use",
                    "id": content_block.id,
                    "name": content_block.name,
                    "input": content_block.input
                })
        
        return content_blocks

class OpenAIProvider(LLMProvider):
    """
    OpenAI GPT provider implementation.
    
    Handles format conversion between OpenAI and Anthropic message formats
    to maintain compatibility with the existing agent logic.
    """
    
    def __init__(self, api_key: str):
        self.client = openai.OpenAI(api_key=api_key)
    
    def create_message(self, system: str, messages: List[Dict[str, Any]], tools: List[Dict[str, Any]]) -> Any:
        """Create message using OpenAI API with format conversion."""
        # Convert messages from Anthropic format to OpenAI format
        openai_messages = self._convert_messages_to_openai(system, messages)
        
        # Convert tools from Anthropic format to OpenAI format
        openai_tools = self._convert_tools_to_openai(tools) if tools else None
        
        # Make the API call
        kwargs = {
            "model": "gpt-4o",
            "max_tokens": 1024,
            "messages": openai_messages
        }
        
        if openai_tools:
            kwargs["tools"] = openai_tools
            kwargs["tool_choice"] = "auto"
        
        return self.client.chat.completions.create(**kwargs)
    
    def parse_response(self, response: Any) -> List[Dict[str, Any]]:
        """Parse OpenAI response and convert to Anthropic-compatible format."""
        content_blocks = []
        
        message = response.choices[0].message
        
        # Handle text content
        if message.content:
            content_blocks.append({
                "type": "text",
                "text": message.content
            })
        
        # Handle tool calls
        if hasattr(message, 'tool_calls') and message.tool_calls:
            for tool_call in message.tool_calls:
                content_blocks.append({
                    "type": "tool_use",
                    "id": tool_call.id,
                    "name": tool_call.function.name,
                    "input": json.loads(tool_call.function.arguments)
                })
        
        return content_blocks
    
    def _convert_messages_to_openai(self, system: str, messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Convert Anthropic message format to OpenAI format."""
        openai_messages = []
        
        # Add system message
        if system:
            openai_messages.append({"role": "system", "content": system})
        
        for message in messages:
            role = message["role"]
            content = message["content"]
            
            if role == "user":
                # Handle user messages with potential tool results
                if isinstance(content, list):
                    # Check if this is a tool result message
                    tool_results = [c for c in content if c.get("type") == "tool_result"]
                    if tool_results:
                        # Convert tool results to OpenAI format
                        for tool_result in tool_results:
                            openai_messages.append({
                                "role": "tool",
                                "tool_call_id": tool_result["tool_use_id"],
                                "content": tool_result["content"]
                            })
                    else:
                        # Regular user message with text content
                        text_content = ""
                        for c in content:
                            if c.get("type") == "text":
                                text_content += c["text"]
                        openai_messages.append({"role": "user", "content": text_content})
                else:
                    # Simple string content
                    openai_messages.append({"role": "user", "content": content})
            
            elif role == "assistant":
                # Handle assistant messages with potential tool calls
                if isinstance(content, list):
                    text_content = ""
                    tool_calls = []
                    
                    for c in content:
                        if c.get("type") == "text":
                            text_content += c["text"]
                        elif c.get("type") == "tool_use":
                            tool_calls.append({
                                "id": c["id"],
                                "type": "function",
                                "function": {
                                    "name": c["name"],
                                    "arguments": json.dumps(c["input"])
                                }
                            })
                    
                    assistant_message = {"role": "assistant"}
                    if text_content:
                        assistant_message["content"] = text_content
                    if tool_calls:
                        assistant_message["tool_calls"] = tool_calls
                    
                    openai_messages.append(assistant_message)
                else:
                    # Simple string content
                    openai_messages.append({"role": "assistant", "content": content})
        
        return openai_messages
    
    def _convert_tools_to_openai(self, tools: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Convert Anthropic tool format to OpenAI function format."""
        openai_tools = []
        
        for tool in tools:
            # OpenAI expects the parameters to have a "type": "object" at the root level
            parameters = tool["input_schema"].copy()
            if "type" not in parameters:
                parameters["type"] = "object"
            
            openai_tool = {
                "type": "function",
                "function": {
                    "name": tool["name"],
                    "description": tool["description"],
                    "parameters": parameters
                }
            }
            openai_tools.append(openai_tool)
        
        return openai_tools

def create_provider(provider_type: str, api_key: str) -> LLMProvider:
    """
    Factory function to create the appropriate LLM provider.
    
    Args:
        provider_type: Either "anthropic" or "openai"
        api_key: API key for the provider
        
    Returns:
        LLMProvider instance
        
    Raises:
        ValueError: If provider_type is not supported
    """
    if provider_type.lower() == "anthropic":
        return AnthropicProvider(api_key)
    elif provider_type.lower() == "openai":
        return OpenAIProvider(api_key)
    else:
        raise ValueError(f"Unsupported provider type: {provider_type}. Supported types: anthropic, openai")
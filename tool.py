# tool.py
from typing import Dict, Any, Callable

class Tool:
    """
    Represents a tool that Claude can use to interact with the environment.
    
    Attributes:
        name: The name of the tool
        description: A detailed description explaining what the tool does
        input_schema: JSON Schema describing the input parameters
        function: The function that executes the tool's logic
    """
    
    def __init__(self, 
                 name: str, 
                 description: str, 
                 input_schema: Dict[str, Any],
                 function: Callable[[Dict[str, Any]], str]):
        self.name = name
        self.description = description
        self.input_schema = input_schema
        self.function = function
    
    def execute(self, params: Dict[str, Any]) -> str:
        """Execute the tool with the given parameters."""
        return self.function(params)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the tool to a dictionary format for Claude API."""
        return {
            "name": self.name,
            "description": self.description,
            "input_schema": self.input_schema
        }
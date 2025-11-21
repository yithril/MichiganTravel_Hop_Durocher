"""
Example agent service demonstrating the pattern.

This is a template for creating new agent services.
Each agent should:
1. Extend BaseAgentService[YourPydanticModel]
2. Implement parse_response() method
3. Define their Pydantic response model
4. Optionally load system prompt from prompts/ folder
"""
import json
import re
from typing import Optional
from pydantic import BaseModel
from services.core.agent.base_agent_service import BaseAgentService
from services.core.agent.conversation_service import ConversationService


# Example Pydantic response model for this agent
class ExampleAgentResponse(BaseModel):
    """Example response model for the example agent."""
    answer: str
    confidence: float
    reasoning: Optional[str] = None


class ExampleAgentService(BaseAgentService[ExampleAgentResponse]):
    """
    Example agent service that returns structured responses.
    
    This demonstrates the pattern for creating agent services.
    """
    
    def __init__(
        self,
        model_id: Optional[str] = None,
        api_key: Optional[str] = None,
        project_id: Optional[str] = None,
        url: Optional[str] = None,
        conversation_service: Optional[ConversationService] = None,
        **kwargs
    ):
        """
        Initialize the example agent.
        
        You can load a system prompt from prompts/ folder here:
        ```
        from pathlib import Path
        prompt_path = Path(__file__).parent.parent.parent.parent / "prompts" / "example_agent.txt"
        system_prompt = prompt_path.read_text() if prompt_path.exists() else None
        ```
        """
        # Load system prompt from prompts folder if needed
        system_prompt = None  # Load from prompts/example_agent.txt if desired
        
        super().__init__(
            model_id=model_id,
            api_key=api_key,
            project_id=project_id,
            url=url,
            system_prompt=system_prompt,
            conversation_service=conversation_service,
            **kwargs
        )
    
    def parse_response(self, response_text: str) -> ExampleAgentResponse:
        """
        Parse the raw response into ExampleAgentResponse.
        
        This method should handle the specific format your agent returns.
        Common patterns:
        - JSON response: Parse JSON and validate with Pydantic
        - Structured text: Use regex or parsing logic
        - Markdown-wrapped JSON: Extract JSON from code blocks
        
        Args:
            response_text: Raw text response from WatsonX
            
        Returns:
            Parsed ExampleAgentResponse instance
            
        Raises:
            ValueError: If response cannot be parsed
        """
        # Example: Try to parse as JSON first
        try:
            data = json.loads(response_text)
            return ExampleAgentResponse(**data)
        except json.JSONDecodeError:
            pass
        
        # Example: Try to extract JSON from markdown code blocks
        json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', response_text, re.DOTALL)
        if json_match:
            try:
                data = json.loads(json_match.group(1))
                return ExampleAgentResponse(**data)
            except json.JSONDecodeError:
                pass
        
        # Example: Fallback - try to find JSON object in text
        json_match = re.search(r'(\{.*?\})', response_text, re.DOTALL)
        if json_match:
            try:
                data = json.loads(json_match.group(1))
                return ExampleAgentResponse(**data)
            except json.JSONDecodeError:
                pass
        
        # If all parsing fails, raise an error
        raise ValueError(
            f"Could not parse response as ExampleAgentResponse: {response_text[:200]}"
        )


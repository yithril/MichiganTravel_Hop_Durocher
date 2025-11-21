"""Base agent service with generic Pydantic model support."""
from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Optional
from pydantic import BaseModel
from langchain_ibm import ChatWatsonx
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from core.config import settings
from services.core.agent.conversation_service import ConversationService

T = TypeVar('T', bound=BaseModel)


class BaseAgentService(ABC, Generic[T]):
    """Base agent service for IBM WatsonX with Pydantic response models."""
    
    def __init__(
        self,
        model_id: Optional[str] = None,
        api_key: Optional[str] = None,
        project_id: Optional[str] = None,
        url: Optional[str] = None,
        system_prompt: Optional[str] = None,
        conversation_service: Optional[ConversationService] = None,
        **kwargs
    ):
        """
        Initialize the agent service with IBM WatsonX credentials.
        
        Args:
            model_id: The WatsonX model ID (defaults to WATSONX_MODEL_ID from settings)
            api_key: IBM WatsonX API key (defaults to WATSONX_APIKEY from settings)
            project_id: IBM WatsonX project ID (defaults to WATSONX_PROJECT_ID from settings)
            url: IBM WatsonX service URL (defaults to WATSONX_URL from settings)
            system_prompt: System prompt for this agent (can be loaded from prompts folder)
            conversation_service: Optional conversation service for history management
            **kwargs: Additional parameters to pass to ChatWatsonx (including params dict)
        """
        # Use explicit parameters first, fall back to settings
        self.model_id = model_id or settings.watsonx_model_id or "ibm/granite-3-8b-instruct"
        self.api_key = api_key if api_key is not None else settings.watsonx_apikey
        self.project_id = project_id if project_id is not None else settings.watsonx_project_id
        self.url = url if url is not None else settings.watsonx_url
        
        if not self.api_key:
            raise ValueError("WATSONX_APIKEY is required. Set it in .env file or pass as parameter.")
        if not self.project_id:
            raise ValueError("WATSONX_PROJECT_ID is required. Set it in .env file or pass as parameter.")
        if not self.url:
            raise ValueError("WATSONX_URL is required. Set it in .env file or pass as parameter.")
        
        self.system_prompt = system_prompt
        self.conversation_service = conversation_service
        
        # Default parameters for the model
        default_params = {
            "max_new_tokens": 200,
            "temperature": 0.0,
            "top_p": 0.9,
            **kwargs.get("params", {})
        }
        
        self.chat_model = ChatWatsonx(
            model_id=self.model_id,
            url=self.url,
            apikey=self.api_key,
            project_id=self.project_id,
            params=default_params
        )
    
    @abstractmethod
    def parse_response(self, response_text: str) -> T:
        """
        Parse the raw response text into the agent's Pydantic model.
        
        This method should be implemented by each agent to handle
        their specific response format (JSON, structured text, etc.).
        
        Args:
            response_text: Raw text response from WatsonX
            
        Returns:
            Parsed Pydantic model instance
            
        Raises:
            ValueError: If response cannot be parsed
        """
        pass
    
    async def process(
        self,
        prompt: str,
        user_id: Optional[int] = None,
        trip_id: Optional[int] = None,
        conversation_id: Optional[int] = None,
        use_history: bool = False,
        original_user_message: Optional[str] = None,
    ) -> T:
        """
        Process a prompt and return a parsed Pydantic response.
        
        Args:
            prompt: User's input prompt
            user_id: Optional user ID for conversation history
            trip_id: Optional trip ID for conversation context
            conversation_id: Optional existing conversation ID
            use_history: Whether to use conversation history (requires conversation_service)
            
        Returns:
            Parsed Pydantic model response
            
        Raises:
            ValueError: If prompt is empty or response cannot be parsed
            Exception: If API call fails
        """
        if not prompt or not prompt.strip():
            raise ValueError("Prompt cannot be empty")
        
        # Build messages list
        messages = []
        
        # Add system prompt if available
        if self.system_prompt:
            messages.append(SystemMessage(content=self.system_prompt))
        
        # Load conversation history if requested
        if use_history and self.conversation_service and conversation_id:
            history = await self.conversation_service.get_conversation_messages(conversation_id)
            for msg in history:
                if msg.role == "system":
                    messages.append(SystemMessage(content=msg.content))
                elif msg.role == "assistant":
                    messages.append(AIMessage(content=msg.content))
                else:
                    messages.append(HumanMessage(content=msg.content))
        
        # Add current user message
        messages.append(HumanMessage(content=prompt))
        
        try:
            # Call WatsonX asynchronously
            response = await self.chat_model.ainvoke(messages)
            
            # Extract content from response
            if hasattr(response, 'content'):
                response_text = str(response.content)
            else:
                response_text = str(response)
            
            # Parse response into Pydantic model
            parsed_response = self.parse_response(response_text)
            
            # Get the text to save to conversation history
            # If the parsed response has a response_text attribute (like TripSeedAgentResponse),
            # use that instead of the raw JSON
            message_content = response_text
            if hasattr(parsed_response, 'response_text'):
                message_content = parsed_response.response_text
            
            # Save to conversation history if enabled
            if use_history and self.conversation_service:
                if conversation_id:
                    # Add messages to existing conversation
                    # Use original_user_message if provided, otherwise use prompt
                    user_message_to_save = original_user_message if original_user_message else prompt
                    await self.conversation_service.add_message(
                        conversation_id=conversation_id,
                        role="user",
                        content=user_message_to_save
                    )
                    await self.conversation_service.add_message(
                        conversation_id=conversation_id,
                        role="assistant",
                        content=message_content
                    )
                elif user_id:
                    # Create new conversation
                    conv = await self.conversation_service.create_conversation(
                        user_id=user_id,
                        trip_id=trip_id
                    )
                    # Use original_user_message if provided, otherwise use prompt
                    user_message_to_save = original_user_message if original_user_message else prompt
                    await self.conversation_service.add_message(
                        conversation_id=conv.id,
                        role="user",
                        content=user_message_to_save
                    )
                    await self.conversation_service.add_message(
                        conversation_id=conv.id,
                        role="assistant",
                        content=message_content
                    )
            
            return parsed_response
            
        except Exception as e:
            raise Exception(f"Failed to process prompt with WatsonX: {str(e)}") from e
    
    async def process_simple(self, prompt: str) -> T:
        """
        Process a prompt without conversation history.
        
        Args:
            prompt: User's input prompt
            
        Returns:
            Parsed Pydantic model response
        """
        return await self.process(prompt, use_history=False)


"""
Trip Seed Agent Service for collecting trip planning information through conversation.

This agent maintains conversation history and TripSeed state to naturally collect
required trip information (num_days, trip_mode, budget_band) and optional fields.
"""
import json
import re
from typing import Optional
from pydantic import BaseModel, Field
from services.core.agent.base_agent_service import BaseAgentService
from services.core.agent.conversation_service import ConversationService
from core.models.trips.trip_mode import TripMode
from core.models.trips.budget_band import BudgetBand
from core.models.trips.companions import Companions
from prompts.trip_seed_agent import get_trip_seed_agent_prompt


class TripSeedExtractedData(BaseModel):
    """Extracted trip seed data from user conversation."""
    num_days: Optional[int] = Field(None, description="Number of days for the trip")
    trip_mode: Optional[TripMode] = Field(None, description="Type of trip: local_hub or road_trip")
    budget_band: Optional[BudgetBand] = Field(None, description="Budget level: relaxed, comfortable, or splurge")
    start_location_text: Optional[str] = Field(None, description="Starting location as text")
    start_latitude: Optional[float] = Field(None, description="Starting latitude coordinate")
    start_longitude: Optional[float] = Field(None, description="Starting longitude coordinate")
    companions: Optional[Companions] = Field(None, description="Who's traveling: solo, couple, family, or friends")


class TripSeedAgentResponse(BaseModel):
    """Complete response from Trip Seed Agent including conversational text and extracted data."""
    response_text: str = Field(..., description="The friendly, conversational response to the user")
    extracted_data: TripSeedExtractedData = Field(..., description="Structured data extracted from the conversation")
    is_complete: bool = Field(..., description="Whether all required fields (num_days, trip_mode, budget_band) are now filled")
    missing_fields: list[str] = Field(default_factory=list, description="List of required field names that still need to be collected")


class TripSeedAgentService(BaseAgentService[TripSeedAgentResponse]):
    """
    Trip Seed Agent Service for collecting trip planning information.
    
    This agent:
    - Maintains conversation history awareness
    - Tracks TripSeed state (what's filled vs. missing)
    - Extracts structured data from natural conversation
    - Returns both conversational response and extracted data
    """
    
    def __init__(
        self,
        model_id: Optional[str] = None,
        api_key: Optional[str] = None,
        project_id: Optional[str] = None,
        url: Optional[str] = None,
        conversation_service: Optional[ConversationService] = None,
        trip_seed_state: Optional[dict] = None,
        **kwargs
    ):
        """
        Initialize the Trip Seed Agent.
        
        Args:
            trip_seed_state: Optional dict with current TripSeed state to include in prompt
        """
        # Load system prompt from Python function (can include state)
        system_prompt = get_trip_seed_agent_prompt(trip_seed_state=trip_seed_state)
        
        # Override default params for more conversational responses
        default_params = {
            "max_new_tokens": 300,  # Longer responses for conversation
            "temperature": 0.7,  # More creative/warm responses
            "top_p": 0.9,
            **kwargs.get("params", {})
        }
        kwargs["params"] = default_params
        
        super().__init__(
            model_id=model_id,
            api_key=api_key,
            project_id=project_id,
            url=url,
            system_prompt=system_prompt,
            conversation_service=conversation_service,
            **kwargs
        )
    
    def _normalize_budget_band(self, value: str | None) -> str | None:
        """Normalize budget band values to enum values with fallback."""
        if value is None:
            return None
        
        value_lower = value.lower().strip()
        
        # Map common variations to enum values
        budget_mappings = {
            "relaxed": "relaxed",
            "budget": "relaxed",
            "budget_friendly": "relaxed",
            "budget-friendly": "relaxed",
            "budget conscious": "relaxed",
            "budget-conscious": "relaxed",
            "cheap": "relaxed",
            "affordable": "relaxed",
            "economy": "relaxed",
            "comfortable": "comfortable",
            "mid-range": "comfortable",
            "mid range": "comfortable",
            "moderate": "comfortable",
            "balanced": "comfortable",
            "splurge": "splurge",
            "premium": "splurge",
            "luxury": "splurge",
            "high-end": "splurge",
            "high end": "splurge",
            "expensive": "splurge",
        }
        
        normalized = budget_mappings.get(value_lower, value_lower)
        
        # Validate it's a valid enum value, fallback to "comfortable" if not
        valid_values = {"relaxed", "comfortable", "splurge"}
        if normalized not in valid_values:
            return "comfortable"  # Safe fallback
        
        return normalized
    
    def _normalize_trip_mode(self, value: str | None) -> str | None:
        """Normalize trip mode values to enum values with fallback."""
        if value is None:
            return None
        
        value_lower = value.lower().strip()
        
        # Map common variations to enum values
        mode_mappings = {
            "local_hub": "local_hub",
            "local hub": "local_hub",
            "localhub": "local_hub",
            "hub": "local_hub",
            "single location": "local_hub",
            "one place": "local_hub",
            "road_trip": "road_trip",
            "roadtrip": "road_trip",
            "road trip": "road_trip",
            "traveling": "road_trip",
            "multiple locations": "road_trip",
        }
        
        normalized = mode_mappings.get(value_lower, value_lower)
        
        # Validate it's a valid enum value, fallback to "local_hub" if not
        valid_values = {"local_hub", "road_trip"}
        if normalized not in valid_values:
            return "local_hub"  # Safe fallback
        
        return normalized
    
    def _normalize_companions(self, value: str | None) -> str | None:
        """Normalize companions values to enum values with fallback."""
        if value is None:
            return None
        
        value_lower = value.lower().strip()
        
        # Map common variations to enum values
        companions_mappings = {
            "solo": "solo",
            "alone": "solo",
            "just me": "solo",
            "by myself": "solo",
            "couple": "couple",
            "partner": "couple",
            "with my partner": "couple",
            "my partner": "couple",
            "family": "family",
            "with family": "family",
            "my family": "family",
            "friends": "friends",
            "with friends": "friends",
            "my friends": "friends",
        }
        
        normalized = companions_mappings.get(value_lower, value_lower)
        
        # Validate it's a valid enum value, fallback to "solo" if not
        valid_values = {"solo", "couple", "family", "friends"}
        if normalized not in valid_values:
            return "solo"  # Safe fallback
        
        return normalized
    
    def parse_response(self, response_text: str) -> TripSeedAgentResponse:
        """
        Parse the raw response into TripSeedAgentResponse.
        
        Expected format: JSON object with:
        - response_text: string (the conversational response)
        - extracted_data: object (the structured data)
        - is_complete: boolean
        - missing_fields: array of strings
        
        Args:
            response_text: Raw text response from WatsonX
            
        Returns:
            Parsed TripSeedAgentResponse instance
            
        Raises:
            ValueError: If response cannot be parsed
        """
        def normalize_data(data: dict) -> dict:
            """Normalize enum values in extracted_data."""
            if "extracted_data" in data and isinstance(data["extracted_data"], dict):
                extracted = data["extracted_data"].copy()
                
                # Normalize budget_band
                if "budget_band" in extracted and extracted["budget_band"]:
                    extracted["budget_band"] = self._normalize_budget_band(extracted["budget_band"])
                
                # Normalize trip_mode
                if "trip_mode" in extracted and extracted["trip_mode"]:
                    extracted["trip_mode"] = self._normalize_trip_mode(extracted["trip_mode"])
                
                # Normalize companions
                if "companions" in extracted and extracted["companions"]:
                    extracted["companions"] = self._normalize_companions(extracted["companions"])
                
                data["extracted_data"] = extracted
            return data
        
        # Try to parse as JSON first
        try:
            data = json.loads(response_text)
            data = normalize_data(data)
            return TripSeedAgentResponse(**data)
        except json.JSONDecodeError:
            pass
        except Exception as e:
            # If normalization or validation fails, try other parsing methods
            pass
        
        # Try to extract JSON from markdown code blocks
        json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', response_text, re.DOTALL)
        if json_match:
            try:
                data = json.loads(json_match.group(1))
                data = normalize_data(data)
                return TripSeedAgentResponse(**data)
            except json.JSONDecodeError:
                pass
            except Exception as e:
                pass
        
        # Try to find JSON object in text
        json_match = re.search(r'(\{.*?\})', response_text, re.DOTALL)
        if json_match:
            try:
                data = json.loads(json_match.group(1))
                data = normalize_data(data)
                return TripSeedAgentResponse(**data)
            except json.JSONDecodeError:
                pass
            except Exception as e:
                pass
        
        # If all parsing fails, raise an error
        raise ValueError(
            f"Could not parse response as TripSeedAgentResponse: {response_text[:200]}"
        )
    
    async def process_with_trip_seed_state(
        self,
        user_message: str,
        conversation_id: int,
        trip_seed_state: dict,
        user_id: Optional[int] = None,
    ) -> TripSeedAgentResponse:
        """
        Process a user message with full TripSeed state context.
        
        This is the main method for the Trip Seed Agent. It:
        1. Updates system prompt with current TripSeed state
        2. Loads conversation history
        3. Processes with LLM
        4. Validates completion status
        5. Returns response with extracted data
        
        Args:
            user_message: The user's current message
            conversation_id: ID of the conversation
            trip_seed_state: Dict with current TripSeed field values (can include None for missing)
            user_id: Optional user ID for validation
            
        Returns:
            TripSeedAgentResponse with conversational response and extracted data
        """
        # Update system prompt with current state (dynamically injected)
        self.system_prompt = get_trip_seed_agent_prompt(trip_seed_state=trip_seed_state)
        
        # Create enhanced prompt that includes user message
        enhanced_prompt = f"""User Message: {user_message}

Please respond with a JSON object containing:
1. "response_text": Your warm, friendly conversational response
2. "extracted_data": Any new trip information you extracted (only include fields that were mentioned)
3. "is_complete": true if all required fields (num_days, trip_mode, budget_band) are now filled, false otherwise
4. "missing_fields": List of required field names still needed (e.g., ["budget_band"])
"""
        
        # Process with conversation history
        # Pass original_user_message so it saves the actual user message, not the enhanced prompt
        response = await self.process(
            prompt=enhanced_prompt,
            user_id=user_id,
            conversation_id=conversation_id,
            use_history=True,
            original_user_message=user_message,
        )
        
        # Validate and update is_complete based on actual state
        response.is_complete = self._check_completion(
            trip_seed_state,
            response.extracted_data
        )
        
        # Update missing_fields based on actual state
        response.missing_fields = self._get_missing_fields(
            trip_seed_state,
            response.extracted_data
        )
        
        return response
    
    def _check_completion(
        self,
        current_state: dict,
        extracted_data: TripSeedExtractedData
    ) -> bool:
        """Check if all required fields are now complete."""
        # Check current state + new extracted data
        num_days = extracted_data.num_days if extracted_data.num_days is not None else current_state.get("num_days")
        trip_mode = extracted_data.trip_mode if extracted_data.trip_mode is not None else current_state.get("trip_mode")
        budget_band = extracted_data.budget_band if extracted_data.budget_band is not None else current_state.get("budget_band")
        
        return (
            num_days is not None and
            trip_mode is not None and
            budget_band is not None
        )
    
    def _get_missing_fields(
        self,
        current_state: dict,
        extracted_data: TripSeedExtractedData
    ) -> list[str]:
        """Get list of required fields that are still missing."""
        missing = []
        
        # Check if each required field is filled (either in current state or extracted)
        num_days = extracted_data.num_days if extracted_data.num_days is not None else current_state.get("num_days")
        trip_mode = extracted_data.trip_mode if extracted_data.trip_mode is not None else current_state.get("trip_mode")
        budget_band = extracted_data.budget_band if extracted_data.budget_band is not None else current_state.get("budget_band")
        
        if num_days is None:
            missing.append("num_days")
        if trip_mode is None:
            missing.append("trip_mode")
        if budget_band is None:
            missing.append("budget_band")
        
        return missing


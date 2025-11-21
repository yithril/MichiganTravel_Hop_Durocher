# Trip Seed Agent Design

## Overview

The Trip Seed Agent is a conversational AI agent that guides users through collecting the necessary information to create a trip plan. The agent maintains a warm, friendly tone while systematically gathering required data points through natural conversation.

## Core Concept

The agent operates in a **stateful conversation** where:
1. It maintains awareness of the **conversation history** (all previous messages)
2. It tracks the current **TripSeed object** state (what fields are filled vs. missing)
3. It responds contextually based on both the conversation and the TripSeed state
4. Once all **required fields** are collected, it transitions the TripSeed status to `COMPLETE`
5. After completion, the system transitions to **trip creation** phase

## User-Specific & Resume Capability

### Data Ownership
- All conversations and trip seeds are **tied to a specific user** via `Conversation.user_id`
- Users can have **multiple conversations** (multiple trip planning sessions)
- Each conversation can have one or more `TripSeed` objects (though typically one active one)

### Resume Functionality
Users can **resume where they left off**:

1. **Incomplete TripSeed (DRAFT status)**
   - When user returns, system finds their active `TripSeed` with `status=DRAFT`
   - Loads full conversation history
   - Loads current `TripSeed` state
   - Agent greets: "Welcome back! We were planning your [details] trip. We still need [missing fields]..."
   - Conversation continues seamlessly

2. **Multiple Active Conversations**
   - User can have multiple `TripSeed` objects in `DRAFT` status
   - User can choose which conversation to resume
   - Each conversation maintains its own history and state

3. **Completed Trips**
   - `TripSeed` with `status=COMPLETE` or `FINALIZED` are read-only
   - User can view completed trips
   - User can start a new conversation for a new trip

### Data Relationships
```
User (id: 1)
  └── Conversation (id: 5, user_id: 1)
        ├── Messages (all chat history, ordered by sequence_index)
        └── TripSeed (id: 3, conversation_id: 5, status: DRAFT)
              └── [trip data fields]
```

All data is scoped to the authenticated user, ensuring privacy and proper data isolation.

## Data Model: TripSeed

### Required Fields (Must Collect)
- `num_days` (int) - Number of days for the trip
- `trip_mode` (enum: `LOCAL_HUB` | `ROAD_TRIP`) - Type of trip
- `budget_band` (enum: `RELAXED` | `COMFORTABLE` | `SPLURGE`) - Budget level

### Optional but Important Fields
- `start_location_text` (string, nullable) - Starting location as text
- `start_latitude` / `start_longitude` (decimal, nullable) - Starting coordinates
- `companions` (enum: `SOLO` | `COUPLE` | `FAMILY` | `FRIENDS`, nullable) - Who's traveling

### Status Field
- `status` (enum: `DRAFT` | `COMPLETE` | `FINALIZED`)
  - Starts as `DRAFT` when TripSeed is created
  - Transitions to `COMPLETE` when all required fields are filled
  - Transitions to `FINALIZED` when trip is created

## Agent Inputs

### 1. User Message
- **Type**: `string`
- **Description**: The current user's message/input
- **Example**: "I want to plan a 3-day road trip from Detroit"

### 2. Conversation History
- **Type**: `List[Message]` (from Conversation model)
- **Description**: All previous messages in the conversation (user + assistant)
- **Structure**:
  - `role`: "user" | "assistant" | "system"
  - `content`: string
  - `created_at`: timestamp
- **Purpose**: Provides context for natural conversation flow

### 3. Current TripSeed State
- **Type**: `TripSeed` object (or partial state)
- **Description**: The current state of the TripSeed being filled
- **Fields to track**:
  - `id`: TripSeed ID
  - `num_days`: int | null
  - `trip_mode`: TripMode | null
  - `budget_band`: BudgetBand | null
  - `start_location_text`: string | null
  - `start_latitude`: decimal | null
  - `start_longitude`: decimal | null
  - `companions`: Companions | null
  - `status`: TripSeedStatus
- **Purpose**: Agent knows what's already collected and what's missing

### 4. Conversation ID
- **Type**: `int`
- **Description**: ID of the conversation this interaction belongs to
- **Purpose**: Links messages to conversation for history tracking

## Agent Outputs

### 1. Agent Response (Text)
- **Type**: `string`
- **Description**: The friendly, conversational response to the user
- **Characteristics**:
  - Warm and welcoming tone
  - Natural language (not robotic)
  - Contextually aware (references previous conversation)
  - Asks follow-up questions when needed
  - Acknowledges information received
- **Example**: "That sounds wonderful! A 3-day road trip from Detroit - I love it! Are you thinking of exploring Michigan's Upper Peninsula, or heading somewhere else?"

### 2. Extracted Data (Structured)
- **Type**: `PartialTripSeedData` (Pydantic model)
- **Description**: Structured data extracted from the user's message
- **Fields** (all optional, only include what was extracted):
  ```python
  {
    "num_days": int | None,
    "trip_mode": TripMode | None,
    "budget_band": BudgetBand | None,
    "start_location_text": str | None,
    "start_latitude": float | None,
    "start_longitude": float | None,
    "companions": Companions | None
  }
  ```
- **Purpose**: Update TripSeed object with new information

### 3. Completion Status
- **Type**: `boolean`
- **Description**: Whether all required fields are now complete
- **Logic**: 
  - `True` if `num_days`, `trip_mode`, and `budget_band` are all filled
  - `False` otherwise
- **Purpose**: Triggers status transition to `COMPLETE` and trip creation phase

### 4. Missing Fields (Optional)
- **Type**: `List[str]`
- **Description**: List of field names that still need to be collected
- **Purpose**: Helps agent prioritize what to ask next

## Agent Behavior & Logic Flow

### Initialization (New Conversation)
1. User requests to start planning a trip
2. System creates new `Conversation` for the user (user_id from auth)
3. System creates new `TripSeed` with `status=DRAFT` linked to conversation
4. Agent greets user warmly: "Hello! I'm excited to help you plan your perfect Michigan adventure!"

### Initialization (Resume Existing Conversation)
1. User requests to continue planning (or system auto-detects active TripSeed)
2. System finds user's `TripSeed` with `status=DRAFT` (or user selects specific conversation)
3. System loads associated `Conversation` and all message history
4. System loads current `TripSeed` state (what's filled, what's missing)
5. Agent greets contextually: "Welcome back! We were planning your [trip details]. We still need [missing fields]..."
6. Conversation continues from where they left off

### Each Turn (User Message → Agent Response)

1. **Receive User Message**
   - Store user message in conversation history

2. **Load Context**
   - Retrieve full conversation history
   - Load current TripSeed state
   - Identify which required fields are missing

3. **Process with LLM**
   - Send to LLM:
     - System prompt (agent personality + instructions)
     - Full conversation history
     - Current TripSeed state (what's filled, what's missing)
     - Current user message
   - LLM generates:
     - Natural response text
     - Structured extraction of any new data points

4. **Extract & Update**
   - Parse LLM response for structured data
   - Update TripSeed with new information
   - Check if all required fields are now complete

5. **Generate Response**
   - If complete: Congratulate user, mention trip creation next
   - If incomplete: Continue conversation, ask about missing fields
   - Maintain warm, friendly tone throughout

6. **Save State**
   - Save assistant response to conversation history
   - Save updated TripSeed to database
   - If complete, update status to `COMPLETE`

### Transition to Trip Creation
- When TripSeed status becomes `COMPLETE`:
  - Agent acknowledges completion
  - System triggers trip creation process
  - TripSeed can be linked to the created Trip

## System Prompt Structure

The agent's system prompt should include:

1. **Personality & Tone**
   - Warm, friendly, enthusiastic about travel
   - Conversational, not robotic
   - Patient and understanding

2. **Role & Goal**
   - You are a travel planning assistant
   - Goal: Collect required trip information through natural conversation
   - Make the process enjoyable, not like filling out a form

3. **Current State Awareness**
   - What information you already have
   - What information you still need
   - Current TripSeed status

4. **Response Format**
   - Generate natural conversational response
   - Extract structured data in JSON format
   - Ask follow-up questions naturally (don't rapid-fire questions)

5. **Field Definitions**
   - `num_days`: Number of days for the trip
   - `trip_mode`: 
     - `LOCAL_HUB`: Staying in one location, exploring nearby
     - `ROAD_TRIP`: Traveling between multiple locations
   - `budget_band`:
     - `RELAXED`: Budget-conscious, looking for deals
     - `COMFORTABLE`: Mid-range, balanced spending
     - `SPLURGE`: Premium experiences, willing to spend more
   - `companions`: Who's traveling (optional but helpful)

6. **Completion Criteria**
   - All required fields must be filled before completion
   - Once complete, acknowledge and prepare for trip creation

## Example Conversation Flow

```
User: "Hi, I want to plan a trip!"

Agent: "Hello! I'm so excited to help you plan your perfect Michigan adventure! 
        Tell me, what kind of trip are you dreaming of? Are you thinking of 
        exploring one area in depth, or hitting the road to see multiple places?"

User: "I want to do a road trip, maybe 4 or 5 days"

Agent: "A road trip sounds fantastic! I love the freedom of exploring multiple 
        places. So you're thinking 4-5 days - that's a great length for a 
        Michigan road trip! Do you have a starting point in mind? Where would 
        you like to begin your journey?"

[... conversation continues ...]

Agent: "Perfect! So we have a 4-day road trip starting from Detroit. One more 
        thing - what's your budget comfort level? Are you looking to keep things 
        budget-friendly, go for a comfortable mid-range experience, or really 
        splurge on premium accommodations and activities?"

User: "I'd say comfortable, not too cheap but not breaking the bank"

Agent: "Got it! Comfortable is a great sweet spot - you'll have nice 
        accommodations and experiences without going overboard. 

        Wonderful! I have everything I need to start planning your trip. 
        Let me create your personalized Michigan road trip itinerary now!"
        
[Status: DRAFT → COMPLETE]
[Trip creation process begins]
```

## Implementation Considerations

### State Management
- TripSeed is the source of truth for collected data
- Always load current TripSeed state before processing
- Update atomically (save TripSeed after each turn)

### Error Handling
- If LLM fails to extract data, agent should acknowledge and ask clarifying questions
- If user provides conflicting information, agent should gently clarify
- If required fields can't be determined, agent should ask directly (but naturally)

### Performance
- Conversation history should be limited (e.g., last 20-30 messages) to avoid token limits
- Consider summarizing older conversation context if needed

### User Experience
- Don't ask all questions at once - make it feel like a conversation
- Acknowledge information as it's provided
- Show enthusiasm and personality
- If user seems frustrated, be empathetic and adjust approach

## Integration Points

### With Conversation Service
- Uses `ConversationService` to manage message history
- Links TripSeed to Conversation via foreign key

### With Trip Creation
- Once TripSeed is `COMPLETE`, triggers trip generation
- TripSeed can be linked to created Trip
- Status may transition to `FINALIZED` after trip creation

### With Location Services (Future)
- May need geocoding service to convert `start_location_text` to coordinates
- Could validate locations against known Michigan cities/attractions

## Success Criteria

The agent is successful when:
1. ✅ Collects all required fields (`num_days`, `trip_mode`, `budget_band`)
2. ✅ Maintains warm, friendly conversation throughout
3. ✅ Doesn't feel like filling out a form
4. ✅ Handles partial information gracefully
5. ✅ Transitions smoothly to trip creation when complete
6. ✅ Preserves conversation history for context


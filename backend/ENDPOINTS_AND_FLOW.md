# API Endpoints and User Flow

## Current Endpoints

### 1. `POST /api/trip-seed/message`
**Purpose**: Start or continue a trip planning conversation with the AI agent.

**Flow**:
- **Start new conversation**: `conversation_id = null`
  - Creates new `Conversation` (user_id, agent_name="trip_seed_agent")
  - Creates new `TripSeed` (status=DRAFT)
  - Returns `conversation_id` for future messages

- **Continue conversation**: `conversation_id = <id>`
  - Retrieves existing `Conversation`
  - Retrieves existing `TripSeed` (status=DRAFT or COMPLETE)
  - Loads conversation history
  - Processes message with agent
  - Updates `TripSeed` with extracted data
  - When all required fields filled → status becomes COMPLETE

**Service**: `TripSeedService.process_message()`
- Uses `ConversationService` for conversation management
- Uses `TripSeedAgentService` for AI agent interaction
- Updates `TripSeed` state as conversation progresses

**Response**: 
- `response_text`: Agent's conversational response
- `conversation_id`: ID to continue conversation
- `trip_seed_state`: Current state (what's filled, what's missing)
- `is_complete`: Whether all required fields are collected

---

### 2. `GET /api/trips`
**Purpose**: View all trips and active trip planning conversations.

**Returns**:
- **`trips`**: List of completed/saved trips (`Trip` objects)
  - These are trips that have been fully designed (with TripDays)
  - Ordered by most recent first

- **`active_trip_seeds`**: List of in-progress conversations
  - `TripSeed` objects with status DRAFT or COMPLETE
  - These are conversations that haven't been turned into trips yet
  - Includes: conversation_id, current state, is_complete, missing_fields

**Service**: `TripService.get_user_trips_and_active_seeds()`
- Queries `Trip` table for user's completed trips
- Queries `TripSeed` table for active conversations (via Conversation join)
- Converts to DTOs

---

## Complete User Flow

### Phase 1: Conversation with AI (✅ IMPLEMENTED)
1. User calls `POST /api/trip-seed/message` with `conversation_id=null`
   - Starts new conversation
   - AI asks about trip preferences

2. User and AI exchange messages via `POST /api/trip-seed/message`
   - User provides: num_days, trip_mode, budget_band, etc.
   - AI extracts data and asks follow-up questions
   - `TripSeed` status: DRAFT → COMPLETE (when all required fields filled)

3. User can resume conversation
   - Call `GET /api/trips` to see active conversations
   - Use `conversation_id` from active_trip_seeds
   - Continue via `POST /api/trip-seed/message`

### Phase 2: Design Trip Days (❌ NOT IMPLEMENTED YET)
4. After `TripSeed` is COMPLETE, user designs each day
   - Need endpoint: `POST /api/trips` (create Trip from TripSeed)
   - Need endpoints for TripDay management
   - Creates `Trip` object with `TripDay` objects
   - `TripSeed` status: COMPLETE → FINALIZED
   - Links `TripSeed.trip_id` to created `Trip`

### Phase 3: View Trips (✅ PARTIALLY IMPLEMENTED)
5. User can view completed trips
   - `GET /api/trips` returns trips array
   - These are trips that have been fully designed

---

## Data Model Relationships

```
User
  └── Conversation (user_id)
        └── TripSeed (conversation_id, status: DRAFT/COMPLETE/FINALIZED)
              └── Trip (trip_id, nullable) [created after trip design]
                    └── TripDay (trip_id) [NOT IMPLEMENTED YET]
```

**Status Flow**:
- `DRAFT`: Conversation in progress, collecting data
- `COMPLETE`: All required fields collected, ready to design trip
- `FINALIZED`: Trip has been created from TripSeed

---

## Missing Endpoints (To Be Built)

1. **Create Trip from TripSeed**
   - `POST /api/trips` 
   - Takes `trip_seed_id`
   - Creates `Trip` from `TripSeed` data
   - Updates `TripSeed.status = FINALIZED`
   - Links `TripSeed.trip_id`

2. **Trip Day Management**
   - `GET /api/trips/{trip_id}/days` - Get all days for a trip
   - `POST /api/trips/{trip_id}/days` - Create/add a day
   - `PUT /api/trips/{trip_id}/days/{day_id}` - Update a day
   - `DELETE /api/trips/{trip_id}/days/{day_id}` - Delete a day

3. **Trip Day Stop Management** (if needed)
   - Endpoints for managing stops within each day

---

## Service Architecture

```
Controllers (API Layer)
  ├── trip_seed_controller.py
  │     └── POST /api/trip-seed/message
  │           └── TripSeedService
  │                 ├── ConversationService
  │                 └── TripSeedAgentService
  │
  └── trip_controller.py
        └── GET /api/trips
              └── TripService
                    └── TripSeedService (for state conversion)
```

---

## Current State Summary

✅ **Working**:
- Start conversation
- Continue conversation (pick up where left off)
- View active conversations (in-progress)
- View completed trips (that have been designed)

❌ **Not Yet Built**:
- Create Trip from completed TripSeed
- Design trip days
- Manage trip itinerary

The conversation flow is complete. The trip design phase (creating TripDays) is the next step.


# Backend Gaps - What's Missing

## ✅ What's Complete

### Conversation Phase
- ✅ `POST /api/trip-seed/message` - Start/continue conversation
- ✅ `TripSeedService` - Manages conversation and TripSeed state
- ✅ `TripSeedAgentService` - AI agent for collecting trip info
- ✅ Conversation history tracking
- ✅ TripSeed status: DRAFT → COMPLETE

### Viewing Phase
- ✅ `GET /api/trips` - View trips and active conversations
- ✅ `TripService.get_user_trips_and_active_seeds()` - Fetches trips and active seeds

---

## ❌ What's Missing

### 1. Create Trip from TripSeed
**Gap**: After conversation completes (TripSeed status=COMPLETE), there's no way to create a Trip.

**Missing**:
- **Endpoint**: `POST /api/trips` (create Trip from TripSeed)
- **Service Method**: `TripService.create_trip_from_seed(trip_seed_id, name)`
- **DTO**: `CreateTripRequest` (trip_seed_id, name)

**What it should do**:
1. Get TripSeed (status must be COMPLETE)
2. Create Trip object with data from TripSeed
3. Update TripSeed.status = FINALIZED
4. Link TripSeed.trip_id to new Trip
5. Return Trip object

**Files to create/modify**:
- `backend/services/trip_service.py` - Add `create_trip_from_seed()` method
- `backend/controllers/trip_controller.py` - Add `POST /api/trips` endpoint
- `backend/dtos/trip_dto.py` - Add `CreateTripRequest` DTO

---

### 2. Trip Day Management
**Gap**: No way to create, read, update, or delete TripDays for a trip.

**Missing Endpoints**:
- `GET /api/trips/{trip_id}/days` - Get all days for a trip
- `POST /api/trips/{trip_id}/days` - Create a new day
- `PUT /api/trips/{trip_id}/days/{day_id}` - Update a day
- `DELETE /api/trips/{trip_id}/days/{day_id}` - Delete a day

**Missing Service**:
- `TripDayService` - CRUD operations for TripDays
  - `get_trip_days(trip_id)` - Get all days
  - `create_trip_day(trip_id, day_index, base_city_id, notes)` - Create day
  - `update_trip_day(day_id, base_city_id, notes)` - Update day
  - `delete_trip_day(day_id)` - Delete day

**Missing DTOs**:
- `TripDayResponse` - Response DTO for a day
- `CreateTripDayRequest` - Request DTO for creating a day
- `UpdateTripDayRequest` - Request DTO for updating a day

**Files to create**:
- `backend/services/trip_day_service.py` - New service
- `backend/controllers/trip_day_controller.py` - New controller
- `backend/dtos/trip_day_dto.py` - New DTOs

---

### 3. Trip Stop Management
**Gap**: No way to manage stops (activities) within each day.

**Missing Endpoints**:
- `GET /api/trips/{trip_id}/days/{day_id}/stops` - Get all stops for a day
- `POST /api/trips/{trip_id}/days/{day_id}/stops` - Add a stop
- `PUT /api/trips/{trip_id}/days/{day_id}/stops/{stop_id}` - Update a stop
- `DELETE /api/trips/{trip_id}/days/{day_id}/stops/{stop_id}` - Delete a stop
- `PATCH /api/trips/{trip_id}/days/{day_id}/stops/reorder` - Reorder stops

**Missing Service**:
- `TripStopService` - CRUD operations for TripStops
  - `get_trip_stops(day_id)` - Get all stops for a day
  - `create_trip_stop(day_id, attraction_id, label, slot, order_index)` - Add stop
  - `update_trip_stop(stop_id, attraction_id, label, slot, order_index)` - Update stop
  - `delete_trip_stop(stop_id)` - Delete stop
  - `reorder_stops(day_id, stop_orders)` - Reorder stops

**Missing DTOs**:
- `TripStopResponse` - Response DTO for a stop
- `CreateTripStopRequest` - Request DTO for creating a stop
- `UpdateTripStopRequest` - Request DTO for updating a stop
- `ReorderStopsRequest` - Request DTO for reordering

**Files to create**:
- `backend/services/trip_stop_service.py` - New service
- `backend/controllers/trip_stop_controller.py` - New controller
- `backend/dtos/trip_stop_dto.py` - New DTOs

---

### 4. Get Single Trip Details
**Gap**: Can list trips, but can't get full details of a single trip.

**Missing**:
- `GET /api/trips/{trip_id}` - Get full trip with days and stops
- Service method to fetch trip with all related data (prefetch days and stops)

**Files to modify**:
- `backend/services/trip_service.py` - Add `get_trip_details(trip_id)` method
- `backend/controllers/trip_controller.py` - Add `GET /api/trips/{trip_id}` endpoint
- `backend/dtos/trip_dto.py` - Add `TripDetailsResponse` with nested days and stops

---

## Summary: Missing Components

### Services (3 new, 2 to extend)
1. ❌ `TripService.create_trip_from_seed()` - Create Trip from TripSeed
2. ❌ `TripService.get_trip_details()` - Get full trip with days/stops
3. ❌ `TripDayService` - Complete service for day management
4. ❌ `TripStopService` - Complete service for stop management

### Controllers (2 new, 1 to extend)
1. ❌ `POST /api/trips` - Create trip from seed (in trip_controller.py)
2. ❌ `GET /api/trips/{trip_id}` - Get trip details (in trip_controller.py)
3. ❌ `trip_day_controller.py` - All day endpoints
4. ❌ `trip_stop_controller.py` - All stop endpoints

### DTOs (3 new files)
1. ❌ `trip_day_dto.py` - TripDay DTOs
2. ❌ `trip_stop_dto.py` - TripStop DTOs
3. ❌ Extend `trip_dto.py` - Add CreateTripRequest, TripDetailsResponse

---

## Complete Flow (What Should Happen)

1. ✅ User chats with AI → TripSeed becomes COMPLETE
2. ❌ User creates Trip from TripSeed → Trip created, TripSeed.status = FINALIZED
3. ❌ User designs days → Creates TripDays (1, 2, 3, ... for num_days)
4. ❌ User adds stops to each day → Creates TripStops (morning, afternoon, evening)
5. ✅ User views trips → Can see completed trips

**Current State**: Steps 1 and 5 work. Steps 2, 3, and 4 are missing.


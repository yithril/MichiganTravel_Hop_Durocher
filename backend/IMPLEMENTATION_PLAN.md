# Pure Michigan Models - Implementation Plan

This document outlines the implementation plan for the Pure Michigan Trip Planner database models.

## Overview

Implementing database models for the Pure Michigan Trip Planner application, organized by domain and following the specifications in `readmes/pure_michigan_models_and_api_spec (1).md`.

## Model Organization

Models will be organized by domain:

- **`core/models/places/`** - Location and attraction models
- **`core/models/trips/`** - Trip planning and itinerary models
- **`core/models/user.py`** - User model (already exists, no changes needed)
- **`core/models/conversation.py`** - Conversation and Message models (already exists, needs `sequence_index` added)

## Implementation Details

### 1. Places Domain (`core/models/places/`)

#### 1.1 Vibe Model
- Fields: `id`, `code` (unique string), `label`, `description` (nullable)
- Relations: CityVibe, AttractionVibe, TripSeedVibe, TripVibe

#### 1.2 City Model
- Fields: `id`, `name`, `state` (default "MI"), `region` (nullable), `latitude` (DecimalField 10,8), `longitude` (DecimalField 10,8), `slug` (unique), `hidden_gem_score` (DecimalField 4,2, 0-10)
- Relations: attractions, vibes (via CityVibe), trip_days (as base_city)

#### 1.3 Attraction Model
- Fields: `id`, `city_id` (FK), `name`, `type` (string), `description` (nullable), `latitude` (DecimalField 10,8), `longitude` (DecimalField 10,8), `url` (nullable), `mini_site_slug` (nullable, unique), `price_level` (nullable: "$", "$$", "$$$"), `hidden_gem_score` (DecimalField 4,2, 0-10), `ai_discovered` (bool), `confidence` (DecimalField 3,2, 0-1), `seasonality` (nullable string)
- Relations: city, vibes (via AttractionVibe), trip_stops

#### 1.4 CityVibe (Join Table)
- Fields: `city_id` (FK), `vibe_id` (FK), `strength` (DecimalField 3,2, 0-1)
- Unique constraint: (city_id, vibe_id)

#### 1.5 AttractionVibe (Join Table)
- Fields: `attraction_id` (FK), `vibe_id` (FK), `strength` (DecimalField 3,2, 0-1)
- Unique constraint: (attraction_id, vibe_id)

### 2. Trips Domain (`core/models/trips/`)

#### 2.1 TripSeed Model
- Fields: `id`, `conversation_id` (FK to Conversation), `trip_id` (FK to Trip, nullable, set when finalized), `start_location_text` (nullable), `start_latitude` (nullable DecimalField 10,8), `start_longitude` (nullable DecimalField 10,8), `num_days` (int), `trip_mode` (enum: "local_hub" | "road_trip"), `budget_band` (enum: "relaxed" | "comfortable" | "splurge"), `companions` (nullable enum: "solo" | "couple" | "family" | "friends"), `status` (enum: draft/complete/finalized), timestamps
- Relations: conversation, trip, vibes (via TripSeedVibe)

#### 2.2 TripSeedVibe (Join Table)
- Fields: `trip_seed_id` (FK), `vibe_id` (FK), `strength` (DecimalField 3,2, 0-1)
- Unique constraint: (trip_seed_id, vibe_id)

#### 2.3 Trip Model
- Fields: `id`, `user_id` (FK), `name` (required string), `start_location_text` (nullable), `start_latitude` (nullable DecimalField 10,8), `start_longitude` (nullable DecimalField 10,8), `num_days` (int), `trip_mode` (enum), `budget_band` (enum), `companions` (nullable enum), timestamps
- Relations: user, days, planning_session (via TripSeed), vibes (via TripVibe)

#### 2.4 TripVibe (Join Table)
- Fields: `trip_id` (FK), `vibe_id` (FK), `strength` (DecimalField 3,2, 0-1)
- Unique constraint: (trip_id, vibe_id)

#### 2.5 TripDay Model
- Fields: `id`, `trip_id` (FK), `day_index` (int, 1-based), `base_city_id` (nullable FK to City), `notes` (nullable), timestamps
- Relations: trip, base_city, stops

#### 2.6 TripStop Model
- Fields: `id`, `trip_day_id` (FK), `attraction_id` (nullable FK), `label` (nullable string for free-text), `slot` (enum: "morning" | "afternoon" | "evening" | "flex"), `order_index` (int), timestamps
- Relations: trip_day, attraction

### 3. Enums to Create

Create Python Enums for:
- `TripMode`: "local_hub", "road_trip"
- `BudgetBand`: "relaxed", "comfortable", "splurge"
- `Companions`: "solo", "couple", "family", "friends"
- `TripStopSlot`: "morning", "afternoon", "evening", "flex"
- `TripSeedStatus`: "draft", "complete", "finalized"

### 4. Updates to Existing Models

#### 4.1 Message Model (`core/models/conversation.py`)
- Add `sequence_index` field (int) for explicit message ordering

#### 4.2 User Model (`core/models/user.py`)
- No changes needed (keeping `full_name` as required)

## File Structure

```
backend/
  core/
    models/
      places/
        __init__.py
        vibe.py
        city.py
        attraction.py
        city_vibe.py
        attraction_vibe.py
      trips/
        __init__.py
        trip_seed.py
        trip_seed_vibe.py
        trip.py
        trip_vibe.py
        trip_day.py
        trip_stop.py
      __init__.py (update to export all models)
      user.py (existing)
      conversation.py (existing, update Message)
      base.py (existing)
```

## Implementation Steps

1. Create enum definitions (in appropriate model files or shared enums module)
2. Create places domain models (Vibe, City, Attraction, CityVibe, AttractionVibe)
3. Create trips domain models (TripSeed, TripSeedVibe, Trip, TripVibe, TripDay, TripStop)
4. Update Message model to add `sequence_index`
5. Update `core/models/__init__.py` to export all new models
6. Update `core/tortoise_config.py` to ensure models are included in migrations
7. Run migrations to create database tables

## Notes

- All models extend `BaseModel` (provides `id`, `created_at`, `updated_at`)
- DecimalField precision: lat/lng (10,8), hidden_gem_score (4,2), confidence/strength (3,2)
- Indexing and advanced constraints deferred (hackathon scope)
- Trip.name is required (not nullable)
- All vibe relationships use separate join tables with strength field


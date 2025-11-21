from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "vibes" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "code" VARCHAR(100) NOT NULL UNIQUE,
    "label" VARCHAR(255) NOT NULL,
    "description" TEXT
);
COMMENT ON TABLE "vibes" IS 'Vibe model for high-level categorization.';
        CREATE TABLE IF NOT EXISTS "cities" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "name" VARCHAR(255) NOT NULL,
    "state" VARCHAR(2) NOT NULL  DEFAULT 'MI',
    "region" VARCHAR(100),
    "latitude" DECIMAL(10,8) NOT NULL,
    "longitude" DECIMAL(10,8) NOT NULL,
    "slug" VARCHAR(255) NOT NULL UNIQUE,
    "hidden_gem_score" DECIMAL(4,2)
);
COMMENT ON TABLE "cities" IS 'City model representing a town/hub for trips.';
        CREATE TABLE IF NOT EXISTS "attractions" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "name" VARCHAR(255) NOT NULL,
    "type" VARCHAR(100) NOT NULL,
    "description" TEXT,
    "latitude" DECIMAL(10,8) NOT NULL,
    "longitude" DECIMAL(10,8) NOT NULL,
    "url" VARCHAR(512),
    "mini_site_slug" VARCHAR(255)  UNIQUE,
    "price_level" VARCHAR(10),
    "hidden_gem_score" DECIMAL(4,2),
    "ai_discovered" BOOL NOT NULL  DEFAULT False,
    "confidence" DECIMAL(3,2),
    "seasonality" VARCHAR(50),
    "city_id" INT NOT NULL REFERENCES "cities" ("id") ON DELETE CASCADE
);
COMMENT ON TABLE "attractions" IS 'Attraction model for things to do (cafés, trails, cider mills, etc.).';
        CREATE TABLE IF NOT EXISTS "city_vibes" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "strength" DECIMAL(3,2) NOT NULL,
    "city_id" INT NOT NULL REFERENCES "cities" ("id") ON DELETE CASCADE,
    "vibe_id" INT NOT NULL REFERENCES "vibes" ("id") ON DELETE CASCADE,
    CONSTRAINT "uid_city_vibes_city_id_dfef02" UNIQUE ("city_id", "vibe_id")
);
COMMENT ON TABLE "city_vibes" IS 'Join table associating City with Vibes.';
        CREATE TABLE IF NOT EXISTS "attraction_vibes" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "strength" DECIMAL(3,2) NOT NULL,
    "attraction_id" INT NOT NULL REFERENCES "attractions" ("id") ON DELETE CASCADE,
    "vibe_id" INT NOT NULL REFERENCES "vibes" ("id") ON DELETE CASCADE,
    CONSTRAINT "uid_attraction__attract_e7d854" UNIQUE ("attraction_id", "vibe_id")
);
COMMENT ON TABLE "attraction_vibes" IS 'Join table associating Attraction with Vibes.';
        CREATE TABLE IF NOT EXISTS "conversations" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "user_id" INT NOT NULL,
    "trip_id" INT,
    "agent_name" VARCHAR(100)
);
CREATE INDEX IF NOT EXISTS "idx_conversatio_user_id_4a0fbf" ON "conversations" ("user_id");
CREATE INDEX IF NOT EXISTS "idx_conversatio_trip_id_03a6fc" ON "conversations" ("trip_id");
CREATE INDEX IF NOT EXISTS "idx_conversatio_user_id_1c4e59" ON "conversations" ("user_id", "trip_id");
COMMENT ON TABLE "conversations" IS 'Conversation model for tracking agent chat sessions.';
        CREATE TABLE IF NOT EXISTS "images" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "user_id" INT NOT NULL,
    "trip_id" INT NOT NULL,
    "trip_day_id" INT NOT NULL,
    "filename" VARCHAR(255) NOT NULL,
    "s3_key" VARCHAR(512) NOT NULL UNIQUE,
    "url" VARCHAR(1024) NOT NULL,
    "file_size" INT NOT NULL,
    "content_type" VARCHAR(100) NOT NULL
);
CREATE INDEX IF NOT EXISTS "idx_images_user_id_7585a7" ON "images" ("user_id");
CREATE INDEX IF NOT EXISTS "idx_images_trip_id_63b956" ON "images" ("trip_id");
CREATE INDEX IF NOT EXISTS "idx_images_trip_da_ad03ca" ON "images" ("trip_day_id");
CREATE INDEX IF NOT EXISTS "idx_images_s3_key_63a6b8" ON "images" ("s3_key");
CREATE INDEX IF NOT EXISTS "idx_images_user_id_e3ba4c" ON "images" ("user_id", "trip_id", "trip_day_id");
COMMENT ON TABLE "images" IS 'Image model with metadata for user trip photos.';
        CREATE TABLE IF NOT EXISTS "messages" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "role" VARCHAR(20) NOT NULL,
    "content" TEXT NOT NULL,
    "sequence_index" INT NOT NULL,
    "conversation_id" INT NOT NULL REFERENCES "conversations" ("id") ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS "idx_messages_convers_a2523a" ON "messages" ("conversation_id", "created_at");
CREATE INDEX IF NOT EXISTS "idx_messages_convers_c6993e" ON "messages" ("conversation_id", "sequence_index");
COMMENT ON TABLE "messages" IS 'Message model for storing individual messages in conversations.';
        CREATE TABLE IF NOT EXISTS "trips" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "name" VARCHAR(255) NOT NULL,
    "start_location_text" VARCHAR(255),
    "start_latitude" DECIMAL(10,8),
    "start_longitude" DECIMAL(10,8),
    "num_days" INT NOT NULL,
    "trip_mode" VARCHAR(9) NOT NULL,
    "budget_band" VARCHAR(11) NOT NULL,
    "companions" VARCHAR(7),
    "user_id" INT NOT NULL REFERENCES "users" ("id") ON DELETE CASCADE
);
COMMENT ON COLUMN "trips"."trip_mode" IS 'LOCAL_HUB: local_hub\nROAD_TRIP: road_trip';
COMMENT ON COLUMN "trips"."budget_band" IS 'RELAXED: relaxed\nCOMFORTABLE: comfortable\nSPLURGE: splurge';
COMMENT ON COLUMN "trips"."companions" IS 'SOLO: solo\nCOUPLE: couple\nFAMILY: family\nFRIENDS: friends';
COMMENT ON TABLE "trips" IS 'Trip model representing a completed/saved trip itinerary.';
        CREATE TABLE IF NOT EXISTS "trip_days" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "day_index" INT NOT NULL,
    "notes" TEXT,
    "base_city_id" INT REFERENCES "cities" ("id") ON DELETE SET NULL,
    "trip_id" INT NOT NULL REFERENCES "trips" ("id") ON DELETE CASCADE
);
COMMENT ON TABLE "trip_days" IS 'TripDay model representing one day of a trip.';
        CREATE TABLE IF NOT EXISTS "trip_seeds" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "start_location_text" VARCHAR(255),
    "start_latitude" DECIMAL(10,8),
    "start_longitude" DECIMAL(10,8),
    "num_days" INT NOT NULL,
    "trip_mode" VARCHAR(9) NOT NULL,
    "budget_band" VARCHAR(11) NOT NULL,
    "companions" VARCHAR(7),
    "status" VARCHAR(9) NOT NULL  DEFAULT 'draft',
    "conversation_id" INT NOT NULL REFERENCES "conversations" ("id") ON DELETE CASCADE,
    "trip_id" INT REFERENCES "trips" ("id") ON DELETE SET NULL
);
COMMENT ON COLUMN "trip_seeds"."trip_mode" IS 'LOCAL_HUB: local_hub\nROAD_TRIP: road_trip';
COMMENT ON COLUMN "trip_seeds"."budget_band" IS 'RELAXED: relaxed\nCOMFORTABLE: comfortable\nSPLURGE: splurge';
COMMENT ON COLUMN "trip_seeds"."companions" IS 'SOLO: solo\nCOUPLE: couple\nFAMILY: family\nFRIENDS: friends';
COMMENT ON COLUMN "trip_seeds"."status" IS 'DRAFT: draft\nCOMPLETE: complete\nFINALIZED: finalized';
COMMENT ON TABLE "trip_seeds" IS 'TripSeed model for storing trip planning data from AI conversations.';
        CREATE TABLE IF NOT EXISTS "trip_seed_vibes" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "strength" DECIMAL(3,2) NOT NULL,
    "trip_seed_id" INT NOT NULL REFERENCES "trip_seeds" ("id") ON DELETE CASCADE,
    "vibe_id" INT NOT NULL REFERENCES "vibes" ("id") ON DELETE CASCADE,
    CONSTRAINT "uid_trip_seed_v_trip_se_87421c" UNIQUE ("trip_seed_id", "vibe_id")
);
COMMENT ON TABLE "trip_seed_vibes" IS 'Join table associating TripSeed with Vibes.';
        CREATE TABLE IF NOT EXISTS "trip_stops" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "label" VARCHAR(255),
    "slot" VARCHAR(9) NOT NULL,
    "order_index" INT NOT NULL,
    "attraction_id" INT REFERENCES "attractions" ("id") ON DELETE SET NULL,
    "trip_day_id" INT NOT NULL REFERENCES "trip_days" ("id") ON DELETE CASCADE
);
COMMENT ON COLUMN "trip_stops"."slot" IS 'MORNING: morning\nAFTERNOON: afternoon\nEVENING: evening\nFLEX: flex';
COMMENT ON TABLE "trip_stops" IS 'TripStop model representing an activity/stop within a day.';
        CREATE TABLE IF NOT EXISTS "trip_vibes" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "strength" DECIMAL(3,2) NOT NULL,
    "trip_id" INT NOT NULL REFERENCES "trips" ("id") ON DELETE CASCADE,
    "vibe_id" INT NOT NULL REFERENCES "vibes" ("id") ON DELETE CASCADE,
    CONSTRAINT "uid_trip_vibes_trip_id_423194" UNIQUE ("trip_id", "vibe_id")
);
COMMENT ON TABLE "trip_vibes" IS 'Join table associating Trip with Vibes.';"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP TABLE IF EXISTS "attractions";
        DROP TABLE IF EXISTS "attraction_vibes";
        DROP TABLE IF EXISTS "cities";
        DROP TABLE IF EXISTS "city_vibes";
        DROP TABLE IF EXISTS "conversations";
        DROP TABLE IF EXISTS "images";
        DROP TABLE IF EXISTS "messages";
        DROP TABLE IF EXISTS "trips";
        DROP TABLE IF EXISTS "trip_days";
        DROP TABLE IF EXISTS "trip_seeds";
        DROP TABLE IF EXISTS "trip_seed_vibes";
        DROP TABLE IF EXISTS "trip_stops";
        DROP TABLE IF EXISTS "trip_vibes";
        DROP TABLE IF EXISTS "vibes";"""

"""
Seed script to create past trips with cover images for user_id=1 and Alpena location data.

Run this script after migrations to populate the database with sample past trips and Alpena attractions.
"""
import asyncio
import sys
import re
from pathlib import Path

# Add parent directory to path to import modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from tortoise import Tortoise
from core.models.user import User
from core.models.trips.trip import Trip
from core.models.trips.trip_mode import TripMode
from core.models.trips.budget_band import BudgetBand
from core.models.trips.companions import Companions
from core.models.trips.trip_status import TripStatus
from core.models.places.city import City
from core.models.places.attraction import Attraction
from core.models.places.vibe import Vibe
from core.models.places.attraction_vibe import AttractionVibe
from core.config import settings


# Past trips data with corresponding images
PAST_TRIPS = [
    {
        "name": "Summer Road Trip Through Michigan",
        "start_location_text": "Detroit, MI",
        "start_latitude": 42.3314,
        "start_longitude": -83.0458,
        "num_days": 5,
        "trip_mode": TripMode.ROAD_TRIP,
        "budget_band": BudgetBand.COMFORTABLE,
        "companions": Companions.FRIENDS,
        "cover_image_url": "/past_trips/pexels-anon-213834-702343.jpg",
    },
    {
        "name": "Lakeside Adventure",
        "start_location_text": "Traverse City, MI",
        "start_latitude": 44.7631,
        "start_longitude": -85.6206,
        "num_days": 3,
        "trip_mode": TripMode.LOCAL_HUB,
        "budget_band": BudgetBand.RELAXED,
        "companions": Companions.COUPLE,
        "cover_image_url": "/past_trips/pexels-chaitaastic-2892243.jpg",
    },
    {
        "name": "Urban Exploration",
        "start_location_text": "Grand Rapids, MI",
        "start_latitude": 42.9634,
        "start_longitude": -85.6681,
        "num_days": 4,
        "trip_mode": TripMode.LOCAL_HUB,
        "budget_band": BudgetBand.SPLURGE,
        "companions": Companions.FAMILY,
        "cover_image_url": "/past_trips/pexels-element5-1194757.jpg",
    },
    {
        "name": "Mountain Getaway",
        "start_location_text": "Marquette, MI",
        "start_latitude": 46.5435,
        "start_longitude": -87.3954,
        "num_days": 6,
        "trip_mode": TripMode.ROAD_TRIP,
        "budget_band": BudgetBand.COMFORTABLE,
        "companions": Companions.SOLO,
        "cover_image_url": "/past_trips/pexels-hao-chen-394286-32058672.jpg",
    },
    {
        "name": "Coastal Journey",
        "start_location_text": "Mackinaw City, MI",
        "start_latitude": 45.7775,
        "start_longitude": -84.7278,
        "num_days": 7,
        "trip_mode": TripMode.ROAD_TRIP,
        "budget_band": BudgetBand.RELAXED,
        "companions": Companions.FRIENDS,
        "cover_image_url": "/past_trips/pexels-pixabay-161963.jpg",
    },
]


async def seed_past_trips():
    """Seed past trips for user_id=1."""
    # Initialize database connection
    await Tortoise.init(
        db_url=settings.database_url,
        modules={"models": ["core.models", "aerich.models"]}
    )
    
    try:
        # Get or create user with id=1
        user = await User.filter(id=1).first()
        if not user:
            print("User with id=1 not found. Creating default user...")
            user = await User.create(
                id=1,
                email="user@example.com",
                password_hash="dummy_hash",  # Not used for seeding
                full_name="Demo User",
            )
            print(f"Created user: {user.email}")
        else:
            print(f"Using existing user: {user.email}")
        
        # Check if past trips already exist
        existing_trips = await Trip.filter(user_id=1, status=TripStatus.COMPLETED).count()
        if existing_trips > 0:
            print(f"Found {existing_trips} existing past trips. Skipping seed.")
            return
        
        # Create past trips
        print(f"\nCreating {len(PAST_TRIPS)} past trips...")
        for trip_data in PAST_TRIPS:
            trip = await Trip.create(
                user_id=user.id,
                status=TripStatus.COMPLETED,
                **trip_data
            )
            print(f"  ✓ Created trip: {trip.name}")
        
        print(f"\n✅ Successfully seeded {len(PAST_TRIPS)} past trips!")
        
    finally:
        # Close database connection
        await Tortoise.close_connections()


# Alpena data
ALPENA_DATA = {
    "town": {
        "name": "Alpena",
        "state": "MI",
        "latitude": 45.0617,
        "longitude": -83.4327,
    },
    "attractions": [
        {
            "name": "Rockport State Recreation Area",
            "description": "A quiet, rugged park with fossil beds, old quarry land, and Lake Huron shoreline. Undeveloped and perfect for explorers.",
            "latitude": 45.1454,
            "longitude": -83.3817,
            "type": "park",
            "vibes": ["Adventurous", "Geological", "Quiet Escape", "Outdoorsy"],
            "image_url": "/alpena/recreation_area.jpg",
        },
        {
            "name": "Great Lakes Maritime Heritage Center",
            "description": "A free NOAA museum featuring interactive maritime exhibits, shipwreck history, and diving displays.",
            "latitude": 45.0631,
            "longitude": -83.4303,
            "type": "museum",
            "vibes": ["Educational", "Family-Friendly", "Nautical", "Interactive"],
            "image_url": "/alpena/maritime.webp",
        },
        {
            "name": "Alpena Shipwreck Tours",
            "description": "Glass-bottom boat tours revealing Lake Huron shipwrecks up close. Unique and rarely crowded.",
            "latitude": 45.0675,
            "longitude": -83.4262,
            "type": "tour",
            "vibes": ["Scenic", "Unique Experience", "Historical", "Adventurous"],
            "image_url": "/alpena/shipwreck.jpg",
        },
        {
            "name": "Island Park & Wildlife Sanctuary",
            "description": "A peaceful nature area with walking trails, wildlife viewing, small bridges, and quiet fishing spots.",
            "latitude": 45.0576,
            "longitude": -83.4308,
            "type": "park",
            "vibes": ["Peaceful", "Nature-Lover", "Photogenic", "Serene"],
            "image_url": "/alpena/island_park.jpg",
        },
        {
            "name": "Starlite Beach",
            "description": "A low-key local beach with shallow waters, a playground, and great summer sunsets.",
            "latitude": 45.0612,
            "longitude": -83.4239,
            "type": "beach",
            "vibes": ["Family-Friendly", "Relaxing", "Low-Key", "Sunset Spot"],
            "image_url": "/alpena/starlight.webp",
        },
    ],
}


def slugify(text: str) -> str:
    """Convert text to URL-friendly slug."""
    text = text.lower()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[-\s]+', '-', text)
    return text.strip('-')


async def get_or_create_vibe(label: str) -> Vibe:
    """Get or create a vibe by label."""
    # Convert label to code format
    code = slugify(label)
    
    vibe = await Vibe.filter(code=code).first()
    if not vibe:
        vibe = await Vibe.create(
            code=code,
            label=label,
        )
        print(f"  Created vibe: {label}")
    return vibe


async def seed_alpena():
    """Seed Alpena city and attractions."""
    # Initialize database connection
    await Tortoise.init(
        db_url=settings.database_url,
        modules={"models": ["core.models", "aerich.models"]}
    )
    
    try:
        town_data = ALPENA_DATA["town"]
        
        # Check if Alpena already exists (by slug to ensure uniqueness)
        city_slug = slugify(town_data["name"])
        city = await City.filter(slug=city_slug).first()
        if city:
            print(f"Alpena (slug: {city_slug}) already exists with ID: {city.id}")
            print(f"📍 Use city_id={city.id} when creating trip days for Alpena")
        else:
            # Create city - all required fields: name, state, latitude, longitude, slug
            city = await City.create(
                name=town_data["name"],
                state=town_data["state"],
                latitude=town_data["latitude"],  # DecimalField accepts float
                longitude=town_data["longitude"],  # DecimalField accepts float
                slug=city_slug,
            )
            print(f"Created city: {city.name} (slug: {city.slug}, id: {city.id})")
            print(f"📍 Use city_id={city.id} when creating trip days for Alpena")
        
        # Create attractions
        print(f"\nCreating {len(ALPENA_DATA['attractions'])} attractions...")
        for attr_data in ALPENA_DATA["attractions"]:
            # Create attraction - required fields: city_id, name, type, latitude, longitude
            attraction = await Attraction.create(
                city_id=city.id,  # ForeignKey - use city_id
                name=attr_data["name"],
                type=attr_data["type"],
                description=attr_data["description"],  # Optional but provided
                latitude=attr_data["latitude"],  # DecimalField accepts float
                longitude=attr_data["longitude"],  # DecimalField accepts float
                image_url=attr_data.get("image_url"),  # Optional, nullable
            )
            print(f"  ✓ Created attraction: {attraction.name}")
            
            # Create/get vibes and link to attraction
            for vibe_label in attr_data.get("vibes", []):
                vibe = await get_or_create_vibe(vibe_label)
                # Check if link already exists (unique_together constraint)
                existing_link = await AttractionVibe.filter(
                    attraction_id=attraction.id,
                    vibe_id=vibe.id
                ).first()
                if not existing_link:
                    # AttractionVibe required fields: attraction_id, vibe_id, strength
                    await AttractionVibe.create(
                        attraction_id=attraction.id,  # ForeignKey
                        vibe_id=vibe.id,  # ForeignKey
                        strength=1.0,  # DecimalField(max_digits=3, decimal_places=2) - 1.0 is valid
                    )
        
        print(f"\n✅ Successfully seeded Alpena with {len(ALPENA_DATA['attractions'])} attractions!")
        
    finally:
        # Close database connection
        await Tortoise.close_connections()


async def seed_all():
    """Seed both past trips and Alpena data."""
    await seed_past_trips()
    await seed_alpena()


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "alpena":
        asyncio.run(seed_alpena())
    elif len(sys.argv) > 1 and sys.argv[1] == "all":
        asyncio.run(seed_all())
    else:
        asyncio.run(seed_past_trips())


"""
Service for managing attractions.

This service handles querying attractions filtered by vibes and location.
"""
from typing import List, Optional
from core.models.places.attraction import Attraction
from core.models.places.attraction_vibe import AttractionVibe
from core.models.trips.trip import Trip
from core.models.trips.trip_vibe import TripVibe
from dtos.attraction_dto import AttractionResponse, AttractionVibeInfo, AttractionsListResponse


class AttractionService:
    """Service for managing attractions."""
    
    async def get_attractions_by_trip_vibes(
        self,
        user_id: int,
        trip_id: int,
        limit: Optional[int] = None,
    ) -> AttractionsListResponse:
        """
        Get attractions that match the vibes of a trip.
        
        Args:
            user_id: ID of the user (to verify trip ownership)
            trip_id: ID of the trip (to get vibes from)
            limit: Optional limit on number of results
            
        Returns:
            AttractionsListResponse with matching attractions
            
        Raises:
            ValueError: If trip not found or doesn't belong to user
        """
        # Verify trip belongs to user
        trip = await Trip.filter(id=trip_id, user_id=user_id).first()
        if not trip:
            raise ValueError(f"Trip {trip_id} not found or doesn't belong to user")
        
        # Get vibes for this trip
        trip_vibes = await TripVibe.filter(trip_id=trip_id).all()
        vibe_ids = [tv.vibe_id for tv in trip_vibes]
        
        if not vibe_ids:
            # No vibes on trip, return empty list
            return AttractionsListResponse(
                attractions=[],
                total=0,
                trip_id=trip_id,
                matching_vibe_ids=[],
            )
        
        # Get attractions that have at least one matching vibe
        # We'll find attractions that have any of the trip's vibes
        # and order by total vibe strength match
        attraction_vibes = await AttractionVibe.filter(
            vibe_id__in=vibe_ids
        ).prefetch_related('attraction__city', 'vibe').all()
        
        # Group by attraction and calculate match score
        attraction_scores = {}  # attraction_id -> (attraction, total_strength, vibes)
        
        for av in attraction_vibes:
            attraction = av.attraction
            if attraction.id not in attraction_scores:
                attraction_scores[attraction.id] = {
                    'attraction': attraction,
                    'total_strength': 0.0,
                    'vibes': []
                }
            
            # Add to total strength (weighted by trip vibe strength)
            trip_vibe = next((tv for tv in trip_vibes if tv.vibe_id == av.vibe_id), None)
            if trip_vibe:
                # Weight by both trip vibe strength and attraction vibe strength
                match_strength = float(av.strength) * float(trip_vibe.strength)
            else:
                match_strength = float(av.strength)
            
            attraction_scores[attraction.id]['total_strength'] += match_strength
            attraction_scores[attraction.id]['vibes'].append({
                'vibe_id': av.vibe_id,
                'vibe_code': av.vibe.code,
                'vibe_label': av.vibe.label,
                'strength': float(av.strength),
            })
        
        # Sort by total strength (best matches first)
        sorted_attractions = sorted(
            attraction_scores.values(),
            key=lambda x: x['total_strength'],
            reverse=True
        )
        
        # Apply limit if provided
        if limit:
            sorted_attractions = sorted_attractions[:limit]
        
        # Build response DTOs
        attraction_responses = []
        for item in sorted_attractions:
            attraction = item['attraction']
            vibe_infos = [
                AttractionVibeInfo(
                    vibe_id=v['vibe_id'],
                    vibe_code=v['vibe_code'],
                    vibe_label=v['vibe_label'],
                    strength=v['strength'],
                )
                for v in item['vibes']
            ]
            
            attraction_responses.append(
                AttractionResponse(
                    id=attraction.id,
                    name=attraction.name,
                    type=attraction.type,
                    description=attraction.description,
                    city_id=attraction.city_id,
                    city_name=attraction.city.name,
                    latitude=float(attraction.latitude),
                    longitude=float(attraction.longitude),
                    url=attraction.url,
                    price_level=attraction.price_level,
                    hidden_gem_score=float(attraction.hidden_gem_score) if attraction.hidden_gem_score else None,
                    seasonality=attraction.seasonality,
                    vibes=vibe_infos,
                    created_at=attraction.created_at.isoformat(),
                    updated_at=attraction.updated_at.isoformat(),
                )
            )
        
        return AttractionsListResponse(
            attractions=attraction_responses,
            total=len(attraction_responses),
            trip_id=trip_id,
            matching_vibe_ids=vibe_ids,
        )
    
    async def get_attractions_by_vibes(
        self,
        vibe_ids: List[int],
        limit: Optional[int] = None,
    ) -> AttractionsListResponse:
        """
        Get attractions that match specific vibes.
        
        Args:
            vibe_ids: List of vibe IDs to match
            limit: Optional limit on number of results
            
        Returns:
            AttractionsListResponse with matching attractions
        """
        if not vibe_ids:
            return AttractionsListResponse(
                attractions=[],
                total=0,
                matching_vibe_ids=[],
            )
        
        # Get attractions that have at least one matching vibe
        attraction_vibes = await AttractionVibe.filter(
            vibe_id__in=vibe_ids
        ).prefetch_related('attraction__city', 'vibe').all()
        
        # Group by attraction and calculate match score
        attraction_scores = {}  # attraction_id -> (attraction, total_strength, vibes)
        
        for av in attraction_vibes:
            attraction = av.attraction
            if attraction.id not in attraction_scores:
                attraction_scores[attraction.id] = {
                    'attraction': attraction,
                    'total_strength': 0.0,
                    'vibes': []
                }
            
            attraction_scores[attraction.id]['total_strength'] += float(av.strength)
            attraction_scores[attraction.id]['vibes'].append({
                'vibe_id': av.vibe_id,
                'vibe_code': av.vibe.code,
                'vibe_label': av.vibe.label,
                'strength': float(av.strength),
            })
        
        # Sort by total strength (best matches first)
        sorted_attractions = sorted(
            attraction_scores.values(),
            key=lambda x: x['total_strength'],
            reverse=True
        )
        
        # Apply limit if provided
        if limit:
            sorted_attractions = sorted_attractions[:limit]
        
        # Build response DTOs
        attraction_responses = []
        for item in sorted_attractions:
            attraction = item['attraction']
            vibe_infos = [
                AttractionVibeInfo(
                    vibe_id=v['vibe_id'],
                    vibe_code=v['vibe_code'],
                    vibe_label=v['vibe_label'],
                    strength=v['strength'],
                )
                for v in item['vibes']
            ]
            
            attraction_responses.append(
                AttractionResponse(
                    id=attraction.id,
                    name=attraction.name,
                    type=attraction.type,
                    description=attraction.description,
                    city_id=attraction.city_id,
                    city_name=attraction.city.name,
                    latitude=float(attraction.latitude),
                    longitude=float(attraction.longitude),
                    url=attraction.url,
                    price_level=attraction.price_level,
                    hidden_gem_score=float(attraction.hidden_gem_score) if attraction.hidden_gem_score else None,
                    seasonality=attraction.seasonality,
                    vibes=vibe_infos,
                    created_at=attraction.created_at.isoformat(),
                    updated_at=attraction.updated_at.isoformat(),
                )
            )
        
        return AttractionsListResponse(
            attractions=attraction_responses,
            total=len(attraction_responses),
            matching_vibe_ids=vibe_ids,
        )


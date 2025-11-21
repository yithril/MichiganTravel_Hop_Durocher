'use client'

import React, { useState, useEffect } from 'react'
import { api, TripResponse, TripDetailsResponse } from '@/lib/api'
import { MichiganLoader } from './MichiganLoader'
import { TripPlanner } from './trip-planner/TripPlanner'

export function PastTripsView() {
  const [trips, setTrips] = useState<TripResponse[]>([])
  const [selectedTrip, setSelectedTrip] = useState<TripDetailsResponse | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [isLoadingTripDetails, setIsLoadingTripDetails] = useState(false)

  useEffect(() => {
    loadTrips()
  }, [])

  const loadTrips = async () => {
    try {
      setIsLoading(true)
      const data = await api.trips.getAll()
      setTrips(data.trips)
    } catch (error) {
      console.error('Failed to load trips:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const handleTripClick = async (tripId: number) => {
    try {
      setIsLoadingTripDetails(true)
      const details = await api.trips.getDetails(tripId)
      setSelectedTrip(details)
    } catch (error) {
      console.error('Failed to load trip details:', error)
      alert('Failed to load trip details. Please try again.')
    } finally {
      setIsLoadingTripDetails(false)
    }
  }

  const formatDate = (dateString: string) => {
    const date = new Date(dateString)
    return date.toLocaleDateString([], {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    })
  }

  const getStatusBadgeColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'completed':
        return {
          backgroundColor: 'var(--color-primary)',
          color: 'var(--color-primary-foreground)',
        }
      case 'planned':
        return {
          backgroundColor: 'var(--color-muted)',
          color: 'var(--color-muted-foreground)',
        }
      default:
        return {
          backgroundColor: 'var(--color-secondary)',
          color: 'var(--color-secondary-foreground)',
        }
    }
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-full" style={{ backgroundColor: 'var(--color-background)' }}>
        <div className="text-center">
          <MichiganLoader size={100} />
          <p 
            className="mt-4 text-sm"
            style={{ color: 'var(--color-muted-foreground)' }}
          >
            Loading your trips...
          </p>
        </div>
      </div>
    )
  }

  // If a trip is selected, show the trip planner
  if (selectedTrip) {
    return (
      <div className="flex flex-col h-full overflow-hidden">
        <div 
          className="p-4 border-b flex items-center justify-between"
          style={{ 
            borderColor: 'var(--color-border)',
            backgroundColor: 'var(--color-card)',
          }}
        >
          <div>
            <button
              onClick={() => setSelectedTrip(null)}
              className="px-4 py-2 rounded-md text-sm transition-all"
              style={{
                backgroundColor: 'var(--color-muted)',
                color: 'var(--color-muted-foreground)',
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.opacity = '0.8'
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.opacity = '1'
              }}
            >
              ← Back to Trips
            </button>
          </div>
          <h2 
            className="text-xl font-semibold"
            style={{ color: 'var(--color-foreground)' }}
          >
            {selectedTrip.name}
          </h2>
        </div>
        <div className="flex-1 overflow-hidden">
          <TripPlanner tripId={selectedTrip.id} />
        </div>
      </div>
    )
  }

  // Show trips list
  return (
    <div 
      className="h-full overflow-y-auto p-6"
      style={{ backgroundColor: 'var(--color-background)' }}
    >
      <div className="mb-6">
        <h1 
          className="text-3xl font-bold mb-2"
          style={{ color: 'var(--color-foreground)' }}
        >
          Past Trips
        </h1>
        <p 
          className="text-sm"
          style={{ color: 'var(--color-muted-foreground)' }}
        >
          View and manage your planned trips
        </p>
      </div>

      {trips.length === 0 ? (
        <div 
          className="p-8 rounded-lg text-center"
          style={{ 
            backgroundColor: 'var(--color-card)',
            border: `1px solid var(--color-border)`,
          }}
        >
          <p 
            className="text-lg mb-2"
            style={{ color: 'var(--color-foreground)' }}
          >
            No trips yet
          </p>
          <p 
            className="text-sm"
            style={{ color: 'var(--color-muted-foreground)' }}
          >
            Start planning your first trip to see it here!
          </p>
        </div>
      ) : (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {trips.map((trip) => (
            <button
              key={trip.id}
              onClick={() => handleTripClick(trip.id)}
              disabled={isLoadingTripDetails}
              className="text-left p-6 rounded-lg transition-all hover:opacity-80 disabled:opacity-50 disabled:cursor-not-allowed"
              style={{
                backgroundColor: 'var(--color-card)',
                border: `1px solid var(--color-border)`,
              }}
            >
              <div className="font-semibold text-lg mb-2" style={{ color: 'var(--color-foreground)' }}>
                {trip.name}
              </div>
              <div className="space-y-2 text-sm">
                {trip.start_location_text && (
                  <div className="flex items-center gap-2" style={{ color: 'var(--color-muted-foreground)' }}>
                    <span>📍</span>
                    <span>{trip.start_location_text}</span>
                  </div>
                )}
                <div className="flex items-center gap-2" style={{ color: 'var(--color-muted-foreground)' }}>
                  <span>📅</span>
                  <span>{trip.num_days} {trip.num_days === 1 ? 'day' : 'days'}</span>
                </div>
                <div 
                  className="text-xs px-2 py-1 rounded-full inline-block capitalize"
                  style={getStatusBadgeColor(trip.status)}
                >
                  {trip.status}
                </div>
                <div 
                  className="text-xs"
                  style={{ color: 'var(--color-muted-foreground)' }}
                >
                  Created {formatDate(trip.created_at)}
                </div>
              </div>
            </button>
          ))}
        </div>
      )}
    </div>
  )
}


'use client'

import React, { useState } from 'react'
import { TripResponse } from '@/lib/api'

interface PastTripsProps {
  trips: TripResponse[]
  onTripClick?: (tripId: number) => void
}

export function PastTrips({ trips, onTripClick }: PastTripsProps) {
  const [isExpanded, setIsExpanded] = useState(false)

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

  if (trips.length === 0) {
    return null
  }

  return (
    <div 
      className="border-b"
      style={{ 
        borderColor: 'var(--color-border)',
        backgroundColor: 'var(--color-card)',
      }}
    >
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-full flex items-center justify-between p-4 hover:opacity-80 transition-opacity"
        style={{ color: 'var(--color-foreground)' }}
      >
        <div className="flex items-center gap-2">
          <h3 className="text-lg font-semibold">Past Trips</h3>
          <span 
            className="text-sm px-2 py-0.5 rounded-full"
            style={{
              backgroundColor: 'var(--color-muted)',
              color: 'var(--color-muted-foreground)',
            }}
          >
            {trips.length}
          </span>
        </div>
        <svg
          className={`w-5 h-5 transition-transform ${isExpanded ? 'rotate-180' : ''}`}
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M19 9l-7 7-7-7"
          />
        </svg>
      </button>

      {isExpanded && (
        <div className="border-t" style={{ borderColor: 'var(--color-border)' }}>
          <div className="p-4">
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 max-h-96 overflow-y-auto">
              {trips.map((trip) => (
                <button
                  key={trip.id}
                  onClick={() => onTripClick?.(trip.id)}
                  className="group flex flex-col overflow-hidden rounded-lg transition-all hover:scale-[1.02] hover:shadow-lg text-left"
                  style={{
                    backgroundColor: 'var(--color-card)',
                    border: `1px solid var(--color-border)`,
                  }}
                >
                  {/* Card Image */}
                  <div className="relative w-full h-48 overflow-hidden">
                    <img
                      src={trip.cover_image_url || '/img/michigan_default.png'}
                      alt={trip.name}
                      className="w-full h-full object-cover transition-transform group-hover:scale-110"
                      onError={(e) => {
                        console.error('Failed to load image:', trip.cover_image_url || '/img/michigan_default.png')
                        // Fallback to default if even that fails
                        e.currentTarget.src = '/img/michigan_default.png'
                      }}
                    />
                  </div>
                  
                  {/* Card Body */}
                  <div className="p-4 flex-1 flex flex-col">
                    <div className="font-semibold text-base mb-2" style={{ color: 'var(--color-foreground)' }}>
                      {trip.name}
                    </div>
                    <div className="flex items-center gap-2 flex-wrap text-sm mb-2">
                      {trip.start_location_text && (
                        <span style={{ color: 'var(--color-muted-foreground)' }}>
                          📍 {trip.start_location_text}
                        </span>
                      )}
                      <span style={{ color: 'var(--color-muted-foreground)' }}>
                        {trip.num_days} {trip.num_days === 1 ? 'day' : 'days'}
                      </span>
                    </div>
                    <div className="flex items-center gap-2 flex-wrap mt-auto">
                      <span 
                        className="text-xs px-2 py-1 rounded-full capitalize"
                        style={getStatusBadgeColor(trip.status)}
                      >
                        {trip.status}
                      </span>
                      {trip.trip_mode && (
                        <span 
                          className="text-xs px-2 py-1 rounded"
                          style={{
                            backgroundColor: 'var(--color-muted)',
                            color: 'var(--color-muted-foreground)',
                          }}
                        >
                          {trip.trip_mode.replace('_', ' ')}
                        </span>
                      )}
                    </div>
                    <div 
                      className="text-xs mt-2"
                      style={{ color: 'var(--color-muted-foreground)' }}
                    >
                      Created {formatDate(trip.created_at)}
                    </div>
                  </div>
                </button>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}


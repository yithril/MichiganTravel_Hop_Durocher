'use client'

import React from 'react'
import { useTripPlanner } from './TripPlannerContext'

export function LocationHeader() {
  const { tripDetails } = useTripPlanner()

  if (!tripDetails?.start_location_text) {
    return null
  }

  return (
    <div 
      className="p-4 border-b"
      style={{ 
        borderColor: 'var(--color-border)',
        backgroundColor: 'var(--color-card)',
      }}
    >
      <div className="flex items-center gap-2">
        <span 
          className="text-lg"
          style={{ color: 'var(--color-primary)' }}
        >
          📍
        </span>
        <h2 
          className="text-lg font-semibold"
          style={{ color: 'var(--color-foreground)' }}
        >
          {tripDetails.start_location_text}
        </h2>
      </div>
    </div>
  )
}


'use client'

import React from 'react'
import { useTripPlanner } from './TripPlannerContext'

export function ActivityIndicators() {
  const { availableActivities, selectedActivityIndex, selectActivity } = useTripPlanner()

  if (availableActivities.length === 0) {
    return null
  }

  return (
    <div className="flex items-center justify-center gap-2 p-4">
      {availableActivities.map((_, index) => (
        <button
          key={index}
          onClick={() => selectActivity(index)}
          className="transition-all"
          style={{
            width: index === selectedActivityIndex ? '12px' : '8px',
            height: index === selectedActivityIndex ? '12px' : '8px',
            borderRadius: '50%',
            backgroundColor:
              index === selectedActivityIndex
                ? 'var(--color-primary)'
                : 'var(--color-muted)',
            opacity: index === selectedActivityIndex ? 1 : 0.5,
          }}
          aria-label={`Go to activity ${index + 1}`}
        />
      ))}
    </div>
  )
}


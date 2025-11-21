'use client'

import React from 'react'
import { useTripPlanner } from './TripPlannerContext'

export function ActivityDescription() {
  const { availableActivities, selectedActivityIndex } = useTripPlanner()

  const currentActivity = availableActivities[selectedActivityIndex]

  if (!currentActivity) {
    return (
      <div 
        className="p-4 h-32 overflow-y-auto rounded-md"
        style={{ 
          backgroundColor: 'var(--color-card)',
          border: `1px solid var(--color-border)`,
        }}
      >
        <p 
          className="text-sm"
          style={{ color: 'var(--color-muted-foreground)' }}
        >
          No activities available
        </p>
      </div>
    )
  }

  return (
    <div 
      className="p-4 h-32 overflow-y-auto rounded-md"
      style={{ 
        backgroundColor: 'var(--color-card)',
        border: `1px solid var(--color-border)`,
      }}
    >
      <h3 
        className="text-lg font-semibold mb-2"
        style={{ color: 'var(--color-foreground)' }}
      >
        {currentActivity.name}
      </h3>
      {currentActivity.description && (
        <p 
          className="text-sm whitespace-pre-wrap"
          style={{ color: 'var(--color-muted-foreground)' }}
        >
          {currentActivity.description}
        </p>
      )}
      <div className="flex items-center gap-2 mt-2 text-xs" style={{ color: 'var(--color-muted-foreground)' }}>
        {currentActivity.type && (
          <span className="px-2 py-1 rounded" style={{ backgroundColor: 'var(--color-muted)' }}>
            {currentActivity.type}
          </span>
        )}
        {currentActivity.price_level && (
          <span>{currentActivity.price_level}</span>
        )}
        {currentActivity.city_name && (
          <span>📍 {currentActivity.city_name}</span>
        )}
      </div>
    </div>
  )
}


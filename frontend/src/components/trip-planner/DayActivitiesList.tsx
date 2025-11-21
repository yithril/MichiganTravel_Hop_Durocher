'use client'

import React from 'react'
import { useTripPlanner } from './TripPlannerContext'

export function DayActivitiesList() {
  const { tripDetails, selectedDayIndex, removeActivityFromDay } = useTripPlanner()

  const selectedDay = tripDetails?.days.find((day) => day.day_index === selectedDayIndex)

  if (!selectedDay) {
    return (
      <div 
        className="p-4 rounded-md"
        style={{ 
          backgroundColor: 'var(--color-card)',
          border: `1px solid var(--color-border)`,
        }}
      >
        <p 
          className="text-sm"
          style={{ color: 'var(--color-muted-foreground)' }}
        >
          No activities for this day yet.
        </p>
      </div>
    )
  }

  const stops = selectedDay.stops || []

  const getSlotLabel = (slot: string) => {
    switch (slot.toLowerCase()) {
      case 'morning':
        return '🌅 Morning'
      case 'afternoon':
        return '☀️ Afternoon'
      case 'evening':
        return '🌙 Evening'
      case 'flex':
        return '🕐 Flexible'
      default:
        return slot
    }
  }

  if (stops.length === 0) {
    return (
      <div 
        className="p-4 rounded-md"
        style={{ 
          backgroundColor: 'var(--color-card)',
          border: `1px solid var(--color-border)`,
        }}
      >
        <p 
          className="text-sm text-center"
          style={{ color: 'var(--color-muted-foreground)' }}
        >
          No activities added yet. Browse activities and click "Add Activity" to plan your day!
        </p>
      </div>
    )
  }

  // Sort stops by slot and order_index
  const sortedStops = [...stops].sort((a, b) => {
    const slotOrder = { morning: 0, afternoon: 1, evening: 2, flex: 3 }
    const slotDiff = (slotOrder[a.slot as keyof typeof slotOrder] || 99) - (slotOrder[b.slot as keyof typeof slotOrder] || 99)
    if (slotDiff !== 0) return slotDiff
    return a.order_index - b.order_index
  })

  const handleRemove = async (stopId: number) => {
    if (confirm('Are you sure you want to remove this activity?')) {
      try {
        await removeActivityFromDay(stopId)
      } catch (error) {
        console.error('Failed to remove activity:', error)
      }
    }
  }

  return (
    <div className="space-y-2 flex-1 overflow-y-auto">
      <h3 
        className="font-semibold mb-2 px-2"
        style={{ color: 'var(--color-foreground)' }}
      >
        Day {selectedDayIndex} Activities
      </h3>
      {sortedStops.map((stop) => (
        <div
          key={stop.id}
          className="p-3 rounded-md transition-all"
          style={{
            backgroundColor: 'var(--color-card)',
            border: `1px solid var(--color-border)`,
          }}
        >
          <div className="flex items-start justify-between gap-2">
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2 mb-1">
                <span className="text-sm font-medium" style={{ color: 'var(--color-foreground)' }}>
                  {getSlotLabel(stop.slot)}
                </span>
                {stop.order_index > 0 && (
                  <span 
                    className="text-xs px-2 py-0.5 rounded"
                    style={{ 
                      backgroundColor: 'var(--color-muted)',
                      color: 'var(--color-muted-foreground)',
                    }}
                  >
                    #{stop.order_index + 1}
                  </span>
                )}
              </div>
              <div 
                className="font-medium text-sm mb-1"
                style={{ color: 'var(--color-foreground)' }}
              >
                {stop.attraction_name || stop.label || 'Unnamed Activity'}
              </div>
              {stop.attraction_type && (
                <div 
                  className="text-xs"
                  style={{ color: 'var(--color-muted-foreground)' }}
                >
                  {stop.attraction_type}
                </div>
              )}
            </div>
            <button
              onClick={() => handleRemove(stop.id)}
              className="px-2 py-1 rounded text-sm transition-all"
              style={{
                backgroundColor: 'var(--color-destructive)',
                color: 'var(--color-destructive-foreground)',
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.opacity = '0.9'
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.opacity = '1'
              }}
              aria-label="Remove activity"
            >
              ×
            </button>
          </div>
        </div>
      ))}
    </div>
  )
}


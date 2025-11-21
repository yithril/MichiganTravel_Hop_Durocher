'use client'

import React from 'react'
import { useTripPlanner } from './TripPlannerContext'

export function DaySelector() {
  const { tripDetails, selectedDayIndex, selectDay } = useTripPlanner()

  if (!tripDetails) {
    return null
  }

  return (
    <div 
      className="flex gap-2 p-4 border-b overflow-x-auto"
      style={{ 
        borderColor: 'var(--color-border)',
        backgroundColor: 'var(--color-card)',
      }}
    >
      {Array.from({ length: tripDetails.num_days }, (_, index) => {
        const dayIndex = index + 1
        const isSelected = dayIndex === selectedDayIndex
        const day = tripDetails.days.find((d) => d.day_index === dayIndex)

        return (
          <button
            key={dayIndex}
            onClick={() => selectDay(dayIndex)}
            className="px-4 py-2 rounded-md font-medium transition-all whitespace-nowrap"
            style={{
              backgroundColor: isSelected
                ? 'var(--color-primary)'
                : 'var(--color-background)',
              color: isSelected
                ? 'var(--color-primary-foreground)'
                : 'var(--color-foreground)',
              border: `1px solid var(--color-border)`,
            }}
            onMouseEnter={(e) => {
              if (!isSelected) {
                e.currentTarget.style.backgroundColor = 'var(--color-muted)'
              }
            }}
            onMouseLeave={(e) => {
              if (!isSelected) {
                e.currentTarget.style.backgroundColor = 'var(--color-background)'
              }
            }}
          >
            Day {dayIndex}
            {day && day.base_city_name && (
              <span className="text-xs ml-2 opacity-75">
                ({day.base_city_name})
              </span>
            )}
          </button>
        )
      })}
    </div>
  )
}


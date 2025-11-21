'use client'

import React, { useState } from 'react'
import { useTripPlanner } from './TripPlannerContext'
import { SlotSelector } from './SlotSelector'

export function AddActivityButton() {
  const {
    availableActivities,
    selectedActivityIndex,
    tripDetails,
    selectedDayIndex,
    addActivityToDay,
  } = useTripPlanner()

  const [isSlotSelectorOpen, setIsSlotSelectorOpen] = useState(false)
  const [isAdding, setIsAdding] = useState(false)

  const currentActivity = availableActivities[selectedActivityIndex]
  const selectedDay = tripDetails?.days.find((day) => day.day_index === selectedDayIndex)

  // Check if activity is already added to this day
  const isAlreadyAdded = selectedDay?.stops.some(
    (stop) => stop.attraction_id === currentActivity?.id
  ) || false

  const handleAddClick = () => {
    if (!currentActivity || !selectedDay) return
    setIsSlotSelectorOpen(true)
  }

  const handleSlotSelect = async (slot: string) => {
    if (!currentActivity) return

    try {
      setIsAdding(true)
      await addActivityToDay(currentActivity.id, slot)
      setIsSlotSelectorOpen(false)
    } catch (error) {
      console.error('Failed to add activity:', error)
      // Error is handled in context
    } finally {
      setIsAdding(false)
    }
  }

  if (!currentActivity || !selectedDay) {
    return null
  }

  return (
    <>
      <button
        onClick={handleAddClick}
        disabled={isAlreadyAdded || isAdding}
        className="w-full px-6 py-3 rounded-md font-medium transition-all disabled:opacity-50 disabled:cursor-not-allowed"
        style={{
          backgroundColor: 'var(--color-primary)',
          color: 'var(--color-primary-foreground)',
        }}
        onMouseEnter={(e) => {
          if (!e.currentTarget.disabled) {
            e.currentTarget.style.opacity = '0.9'
          }
        }}
        onMouseLeave={(e) => {
          e.currentTarget.style.opacity = '1'
        }}
      >
        {isAdding ? (
          <span className="flex items-center justify-center gap-2">
            <span className="inline-block w-4 h-4 border-2 border-current border-t-transparent rounded-full animate-spin" />
            Adding...
          </span>
        ) : isAlreadyAdded ? (
          'Already Added'
        ) : (
          '+ Add Activity to Day'
        )}
      </button>
      <SlotSelector
        isOpen={isSlotSelectorOpen}
        onSelect={handleSlotSelect}
        onCancel={() => setIsSlotSelectorOpen(false)}
      />
    </>
  )
}


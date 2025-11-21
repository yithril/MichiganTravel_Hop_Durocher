'use client'

import React, { useState, useEffect } from 'react'
import { useTripPlanner } from './TripPlannerContext'
import { SlotSelector } from './SlotSelector'

export function AddActivityToDayButton() {
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

  // Check if activity is already added to the selected day
  const selectedDay = tripDetails?.days.find((day) => day.day_index === selectedDayIndex)
  const isAlreadyAdded = selectedDay?.stops?.some(
    (stop) => stop.attraction_id === currentActivity?.id
  ) || false

  // Check if the selected day index is valid (within num_days range)
  // Day doesn't need to exist in the database yet - we'll create it when adding an activity
  const isDayValid = tripDetails && selectedDayIndex >= 1 && selectedDayIndex <= tripDetails.num_days

  // Debug logging
  useEffect(() => {
    if (tripDetails) {
      console.log('AddActivityToDayButton state:', {
        selectedDayIndex,
        isDayValid,
        num_days: tripDetails.num_days,
        selectedDay: selectedDay ? { id: selectedDay.id, day_index: selectedDay.day_index } : null,
        existing_days_count: tripDetails.days.length,
        currentActivity: currentActivity ? { id: currentActivity.id, name: currentActivity.name } : null,
      })
    }
  }, [selectedDayIndex, isDayValid, selectedDay, tripDetails, currentActivity])

  const handleAddClick = () => {
    if (!currentActivity || !isDayValid) return
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
    } finally {
      setIsAdding(false)
    }
  }

  if (!currentActivity) {
    return null
  }

  return (
    <>
      <div className="mt-4">
        <button
          onClick={handleAddClick}
          disabled={!isDayValid || isAlreadyAdded || isAdding}
          className="w-full px-6 py-3 rounded-md font-medium transition-all disabled:opacity-50 disabled:cursor-not-allowed"
          style={{
            backgroundColor: isAlreadyAdded ? 'var(--color-muted)' : 'var(--color-primary)',
            color: isAlreadyAdded ? 'var(--color-muted-foreground)' : 'var(--color-primary-foreground)',
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
          ) : !isDayValid ? (
            'Select a day to add activity'
          ) : isAlreadyAdded ? (
            '✓ Already Added to This Day'
          ) : (
            '+ Add Activity to Day'
          )}
        </button>
      </div>
      <SlotSelector
        isOpen={isSlotSelectorOpen}
        onSelect={handleSlotSelect}
        onCancel={() => setIsSlotSelectorOpen(false)}
      />
    </>
  )
}


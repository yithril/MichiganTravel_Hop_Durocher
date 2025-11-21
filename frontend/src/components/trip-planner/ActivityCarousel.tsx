'use client'

import React from 'react'
import { useTripPlanner } from './TripPlannerContext'
import { MichiganLoader } from '../MichiganLoader'

export function ActivityCarousel() {
  const {
    availableActivities,
    selectedActivityIndex,
    nextActivity,
    previousActivity,
    loading,
  } = useTripPlanner()

  const currentActivity = availableActivities[selectedActivityIndex]

  const handlePrevious = () => {
    previousActivity()
  }

  const handleNext = () => {
    nextActivity()
  }

  if (loading) {
    return (
      <div 
        className="flex items-center justify-center h-full"
        style={{ backgroundColor: 'var(--color-background)' }}
      >
        <MichiganLoader size={100} />
      </div>
    )
  }

  if (availableActivities.length === 0) {
    return (
      <div 
        className="flex items-center justify-center h-full rounded-lg"
        style={{ 
          backgroundColor: 'var(--color-card)',
          border: `1px solid var(--color-border)`,
        }}
      >
        <p 
          className="text-center"
          style={{ color: 'var(--color-muted-foreground)' }}
        >
          No activities available. Try refreshing or check back later.
        </p>
      </div>
    )
  }

  // Use image_url from activity, fallback to default Michigan image
  const imageUrl = currentActivity?.image_url || '/img/michigan_default.png'
  
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

  return (
    <div className="flex flex-col h-full min-h-0">
      <div 
        className="relative flex-1 min-h-0 overflow-hidden rounded-lg"
        style={{ 
          backgroundColor: 'var(--color-card)',
          border: `1px solid var(--color-border)`,
        }}
      >
        {/* Left Arrow - Centered vertically */}
        {availableActivities.length > 1 && (
          <button
            onClick={handlePrevious}
            className="absolute left-4 z-10 w-12 h-12 rounded-full flex items-center justify-center transition-all shadow-lg hover:shadow-xl"
            style={{
              top: '50%',
              transform: 'translateY(-50%)',
              backgroundColor: 'rgba(255, 255, 255, 0.9)',
              color: 'var(--color-primary)',
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.opacity = '1'
              e.currentTarget.style.transform = 'translateY(-50%) scale(1.1)'
              e.currentTarget.style.backgroundColor = 'rgba(255, 255, 255, 1)'
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.opacity = '1'
              e.currentTarget.style.transform = 'translateY(-50%)'
              e.currentTarget.style.backgroundColor = 'rgba(255, 255, 255, 0.9)'
            }}
            aria-label="Previous activity"
          >
            <svg
              className="w-6 h-6"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M15 19l-7-7 7-7"
              />
            </svg>
          </button>
        )}

        {/* Image */}
        <div className="w-full h-full flex items-center justify-center overflow-hidden">
          <img
            src={imageUrl}
            alt={currentActivity?.name || 'Activity'}
            className="w-full h-full object-cover"
            onError={(e) => {
              // Fallback to default Michigan image if image fails to load
              const target = e.target as HTMLImageElement
              if (target.src !== `${window.location.origin}/img/michigan_default.png`) {
                target.src = '/img/michigan_default.png'
              }
            }}
          />
        </div>

        {/* Right Arrow - Centered vertically */}
        {availableActivities.length > 1 && (
          <button
            onClick={handleNext}
            className="absolute right-4 z-10 w-12 h-12 rounded-full flex items-center justify-center transition-all shadow-lg hover:shadow-xl"
            style={{
              top: '50%',
              transform: 'translateY(-50%)',
              backgroundColor: 'rgba(255, 255, 255, 0.9)',
              color: 'var(--color-primary)',
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.opacity = '1'
              e.currentTarget.style.transform = 'translateY(-50%) scale(1.1)'
              e.currentTarget.style.backgroundColor = 'rgba(255, 255, 255, 1)'
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.opacity = '1'
              e.currentTarget.style.transform = 'translateY(-50%)'
              e.currentTarget.style.backgroundColor = 'rgba(255, 255, 255, 0.9)'
            }}
            aria-label="Next activity"
          >
            <svg
              className="w-6 h-6"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M9 5l7 7-7 7"
              />
            </svg>
          </button>
        )}
      </div>
    </div>
  )
}


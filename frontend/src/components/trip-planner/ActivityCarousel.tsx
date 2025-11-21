'use client'

import React from 'react'
import { useTripPlanner } from './TripPlannerContext'
import { MichiganLoader } from '../MichiganLoader'

export function ActivityCarousel() {
  const { availableActivities, selectedActivityIndex, nextActivity, previousActivity, loading } = useTripPlanner()

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

  // Placeholder image - in production, you'd use actual attraction images
  const imageUrl = currentActivity?.url || 'https://via.placeholder.com/800x600?text=Activity+Image'

  return (
    <div 
      className="relative flex-1 overflow-hidden rounded-lg"
      style={{ 
        backgroundColor: 'var(--color-card)',
        border: `1px solid var(--color-border)`,
      }}
    >
      {/* Left Arrow */}
      <button
        onClick={handlePrevious}
        disabled={availableActivities.length === 0}
        className="absolute left-4 top-1/2 -translate-y-1/2 z-10 w-12 h-12 rounded-full flex items-center justify-center transition-all disabled:opacity-50 disabled:cursor-not-allowed"
        style={{
          backgroundColor: 'var(--color-primary)',
          color: 'var(--color-primary-foreground)',
        }}
        onMouseEnter={(e) => {
          if (!e.currentTarget.disabled) {
            e.currentTarget.style.opacity = '0.9'
            e.currentTarget.style.transform = 'translateY(-50%) scale(1.1)'
          }
        }}
        onMouseLeave={(e) => {
          e.currentTarget.style.opacity = '1'
          e.currentTarget.style.transform = 'translateY(-50%) scale(1)'
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

      {/* Image */}
      <div className="w-full h-full flex items-center justify-center">
        <img
          src={imageUrl}
          alt={currentActivity?.name || 'Activity'}
          className="w-full h-full object-cover"
          onError={(e) => {
            // Fallback to placeholder if image fails to load
            const target = e.target as HTMLImageElement
            target.src = `https://via.placeholder.com/800x600?text=${encodeURIComponent(currentActivity?.name || 'Activity')}`
          }}
        />
      </div>

      {/* Right Arrow */}
      <button
        onClick={handleNext}
        disabled={availableActivities.length === 0}
        className="absolute right-4 top-1/2 -translate-y-1/2 z-10 w-12 h-12 rounded-full flex items-center justify-center transition-all disabled:opacity-50 disabled:cursor-not-allowed"
        style={{
          backgroundColor: 'var(--color-primary)',
          color: 'var(--color-primary-foreground)',
        }}
        onMouseEnter={(e) => {
          if (!e.currentTarget.disabled) {
            e.currentTarget.style.opacity = '0.9'
            e.currentTarget.style.transform = 'translateY(-50%) scale(1.1)'
          }
        }}
        onMouseLeave={(e) => {
          e.currentTarget.style.opacity = '1'
          e.currentTarget.style.transform = 'translateY(-50%) scale(1)'
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
    </div>
  )
}


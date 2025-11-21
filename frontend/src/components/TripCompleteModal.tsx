'use client'

import React from 'react'
import { TripSeedStateResponse } from '@/lib/api'

interface TripCompleteModalProps {
  tripSeedState: TripSeedStateResponse
  onCreateTrip: () => void
  onClose: () => void
  isLoading?: boolean
}

export function TripCompleteModal({
  tripSeedState,
  onCreateTrip,
  onClose,
  isLoading = false,
}: TripCompleteModalProps) {
  // Check if trip is actually complete (frontend decides)
  const isComplete = 
    tripSeedState.num_days !== null &&
    tripSeedState.trip_mode !== null &&
    tripSeedState.budget_band !== null

  if (!isComplete) {
    return null
  }

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center"
      style={{ backgroundColor: 'rgba(0, 0, 0, 0.5)' }}
      onClick={onClose}
    >
      <div
        className="p-8 rounded-lg shadow-xl max-w-md w-full mx-4"
        style={{
          backgroundColor: 'var(--color-card)',
          border: '1px solid var(--color-border)',
        }}
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex flex-col items-center gap-4 text-center">
          <div
            className="text-4xl mb-2"
            style={{ color: 'var(--color-primary)' }}
          >
            ✨
          </div>
          <h2
            className="text-2xl font-bold"
            style={{ color: 'var(--color-foreground)' }}
          >
            Your trip plan is ready!
          </h2>
          <p
            className="text-sm"
            style={{ color: 'var(--color-muted-foreground)' }}
          >
            All the details are set. Let's create your trip and start planning the itinerary.
          </p>
          <div className="flex gap-3 w-full mt-4">
            <button
              onClick={onClose}
              disabled={isLoading}
              className="flex-1 px-4 py-2 rounded-md text-sm font-medium transition-all disabled:opacity-50 disabled:cursor-not-allowed"
              style={{
                backgroundColor: 'var(--color-muted)',
                color: 'var(--color-foreground)',
              }}
            >
              Not yet
            </button>
            <button
              onClick={onCreateTrip}
              disabled={isLoading}
              className="flex-1 px-4 py-2 rounded-md text-sm font-semibold transition-all disabled:opacity-50 disabled:cursor-not-allowed"
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
              {isLoading ? (
                <span className="flex items-center justify-center gap-2">
                  <span className="inline-block w-4 h-4 border-2 border-current border-t-transparent rounded-full animate-spin" />
                  Creating...
                </span>
              ) : (
                "Let's make new memories..."
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}


'use client'

import React from 'react'
import { TripSeedStateResponse } from '@/lib/api'

interface TripSeedReadyButtonProps {
  tripSeedState: TripSeedStateResponse
  onCreateTrip: () => void
  isLoading?: boolean
}

export function TripSeedReadyButton({
  tripSeedState,
  onCreateTrip,
  isLoading = false,
}: TripSeedReadyButtonProps) {
  return (
    <div 
      className="p-6 rounded-lg shadow-lg max-w-sm"
      style={{ 
        border: '1px solid var(--color-border)',
        backgroundColor: 'var(--color-card)',
      }}
    >
      <div className="flex flex-col items-center gap-3">
        <div className="text-center">
          <div 
            className="text-2xl mb-2"
            style={{ color: 'var(--color-primary)' }}
          >
            ✨
          </div>
          <p 
            className="text-sm font-medium mb-1"
            style={{ color: 'var(--color-foreground)' }}
          >
            Your trip plan is ready!
          </p>
          <p 
            className="text-xs"
            style={{ color: 'var(--color-muted-foreground)' }}
          >
            All the details are set. Let's create your trip and start planning the itinerary.
          </p>
        </div>
        <button
          onClick={onCreateTrip}
          disabled={isLoading}
          className="px-8 py-3 rounded-md font-semibold text-base transition-all disabled:opacity-50 disabled:cursor-not-allowed"
          style={{
            backgroundColor: 'var(--color-primary)',
            color: 'var(--color-primary-foreground)',
          }}
          onMouseEnter={(e) => {
            if (!e.currentTarget.disabled) {
              e.currentTarget.style.opacity = '0.9'
              e.currentTarget.style.transform = 'scale(1.02)'
            }
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.opacity = '1'
            e.currentTarget.style.transform = 'scale(1)'
          }}
        >
          {isLoading ? (
            <span className="flex items-center gap-2">
              <span className="inline-block w-4 h-4 border-2 border-current border-t-transparent rounded-full animate-spin" />
              Creating...
            </span>
          ) : (
            "Let's make new memories..."
          )}
        </button>
      </div>
    </div>
  )
}


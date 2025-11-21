'use client'

import React, { useState } from 'react'
import { useTripPlanner } from './TripPlannerContext'
import { useRouter } from 'next/navigation'
import { api } from '@/lib/api'

export function CompleteButton() {
  const { tripDetails, refreshTripDetails } = useTripPlanner()
  const router = useRouter()
  const [isCompleting, setIsCompleting] = useState(false)

  if (!tripDetails) {
    return null
  }

  // Check if all days have at least one activity
  const allDaysHaveActivities = tripDetails.days.every(
    (day) => day.stops && day.stops.length > 0
  )

  // Don't show button if not ready
  if (!allDaysHaveActivities) {
    return null
  }

  const handleComplete = async () => {
    if (!tripDetails || !allDaysHaveActivities) return

    try {
      setIsCompleting(true)
      await api.trips.finalize(tripDetails.id)
      
      // Navigate back to dashboard
      router.push('/dashboard')
    } catch (error) {
      console.error('Failed to finalize trip:', error)
      alert(error instanceof Error ? error.message : 'Failed to finalize trip')
      setIsCompleting(false)
    }
  }

  return (
    <div className="p-4 border-t" style={{ borderColor: 'var(--color-border)' }}>
      <button
        onClick={handleComplete}
        disabled={isCompleting}
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
        {isCompleting ? (
          <span className="flex items-center justify-center gap-2">
            <span className="inline-block w-4 h-4 border-2 border-current border-t-transparent rounded-full animate-spin" />
            Finalizing...
          </span>
        ) : (
          '✓ Complete Trip'
        )}
      </button>
    </div>
  )
}


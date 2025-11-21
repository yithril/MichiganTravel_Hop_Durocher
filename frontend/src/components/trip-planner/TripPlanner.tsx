'use client'

import React from 'react'
import { TripPlannerProvider, useTripPlanner } from './TripPlannerContext'
import { LocationHeader } from './LocationHeader'
import { ActivityCarousel } from './ActivityCarousel'
import { AddActivityToDayButton } from './AddActivityToDayButton'
import { ActivityDescription } from './ActivityDescription'
import { ActivityIndicators } from './ActivityIndicators'
import { DaySelector } from './DaySelector'
import { DayActivitiesList } from './DayActivitiesList'
import { AddActivityButton } from './AddActivityButton'
import { CompleteButton } from './CompleteButton'
import { BudgetDisplay } from './BudgetDisplay'
import { MichiganLoader } from '../MichiganLoader'

interface TripPlannerProps {
  tripId: number
}

function TripPlannerContent() {
  const { loading, error, tripDetails } = useTripPlanner()

  if (loading) {
    return (
      <div 
        className="flex items-center justify-center h-full"
        style={{ backgroundColor: 'var(--color-background)' }}
      >
        <div className="text-center">
          <MichiganLoader size={100} />
          <p 
            className="mt-4 text-sm"
            style={{ color: 'var(--color-muted-foreground)' }}
          >
            Loading trip planner...
          </p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div 
        className="flex items-center justify-center h-full p-4"
        style={{ backgroundColor: 'var(--color-background)' }}
      >
        <div 
          className="p-6 rounded-lg max-w-md w-full text-center"
          style={{
            backgroundColor: 'var(--color-card)',
            border: `1px solid var(--color-border)`,
          }}
        >
          <p 
            className="text-lg font-semibold mb-2"
            style={{ color: 'var(--color-destructive)' }}
          >
            Error
          </p>
          <p 
            className="text-sm"
            style={{ color: 'var(--color-muted-foreground)' }}
          >
            {error}
          </p>
        </div>
      </div>
    )
  }

  if (!tripDetails) {
    return (
      <div 
        className="flex items-center justify-center h-full p-4"
        style={{ backgroundColor: 'var(--color-background)' }}
      >
        <p 
          className="text-sm"
          style={{ color: 'var(--color-muted-foreground)' }}
        >
          Trip not found
        </p>
      </div>
    )
  }

  return (
    <div 
      className="flex flex-col h-full"
      style={{ backgroundColor: 'var(--color-background)' }}
    >
      {/* Location Header */}
      <LocationHeader />

      {/* Main Content Area */}
      <div className="flex flex-1 overflow-hidden">
        {/* Left Side - Activity Carousel */}
        <div 
          className="flex flex-col flex-1 overflow-hidden"
          style={{ borderRight: `1px solid var(--color-border)` }}
        >
          <div className="flex-1 min-h-0 overflow-hidden p-4 flex flex-col">
            <ActivityCarousel />
            <AddActivityToDayButton />
          </div>
          
          <div className="p-4 space-y-4 border-t" style={{ borderColor: 'var(--color-border)' }}>
            <ActivityDescription />
            <ActivityIndicators />
          </div>
        </div>

        {/* Right Side - Day Selector and Activities */}
        <div 
          className="flex flex-col w-96 overflow-hidden"
          style={{ 
            backgroundColor: 'var(--color-card)',
            borderLeft: `1px solid var(--color-border)`,
          }}
        >
          {/* Budget Display */}
          <div className="p-4 border-b" style={{ borderColor: 'var(--color-border)' }}>
            <BudgetDisplay />
          </div>

          {/* Day Selector */}
          <DaySelector />

          {/* Activities List */}
          <div className="flex-1 overflow-y-auto p-4 space-y-4">
            <DayActivitiesList />
          </div>

          {/* Add Activity Button */}
          <div 
            className="p-4 border-t"
            style={{ borderColor: 'var(--color-border)' }}
          >
            <AddActivityButton />
          </div>

          {/* Complete Button - Only shows when all days have activities */}
          <CompleteButton />
        </div>
      </div>
    </div>
  )
}

export function TripPlanner({ tripId }: TripPlannerProps) {
  return (
    <TripPlannerProvider tripId={tripId}>
      <TripPlannerContent />
    </TripPlannerProvider>
  )
}


'use client'

import React from 'react'
import { useTripPlanner } from './TripPlannerContext'

export function BudgetDisplay() {
  const { tripDetails } = useTripPlanner()

  if (!tripDetails?.budget_band) {
    return null
  }

  const getBudgetLabel = (budgetBand: string) => {
    switch (budgetBand.toLowerCase()) {
      case 'budget':
        return '$ Budget'
      case 'moderate':
        return '$$ Moderate'
      case 'luxury':
        return '$$$ Luxury'
      default:
        return budgetBand
    }
  }

  return (
    <div 
      className="px-4 py-2 rounded-md"
      style={{ 
        backgroundColor: 'var(--color-muted)',
        color: 'var(--color-muted-foreground)',
      }}
    >
      <div className="flex items-center gap-2">
        <span className="text-sm font-medium">Budget:</span>
        <span className="text-sm">{getBudgetLabel(tripDetails.budget_band)}</span>
      </div>
    </div>
  )
}


'use client'

import React, { createContext, useContext, useState, useCallback, useEffect } from 'react'
import {
  api,
  TripDetailsResponse,
  AttractionResponse,
  TripDayResponse,
  TripStopResponse,
  CreateTripStopRequest,
} from '@/lib/api'

interface TripPlannerContextValue {
  // State
  tripDetails: TripDetailsResponse | null
  availableActivities: AttractionResponse[]
  selectedDayIndex: number
  selectedActivityIndex: number
  loading: boolean
  error: string | null

  // Actions
  loadTripDetails: (tripId: number) => Promise<void>
  loadAvailableActivities: (tripId: number) => Promise<void>
  selectDay: (dayIndex: number) => void
  selectActivity: (activityIndex: number) => void
  nextActivity: () => void
  previousActivity: () => void
  addActivityToDay: (activityId: number, slot: string) => Promise<void>
  removeActivityFromDay: (stopId: number) => Promise<void>
  refreshTripDetails: () => Promise<void>
}

const TripPlannerContext = createContext<TripPlannerContextValue | undefined>(undefined)

interface TripPlannerProviderProps {
  children: React.ReactNode
  tripId: number
}

export function TripPlannerProvider({ children, tripId }: TripPlannerProviderProps) {
  const [tripDetails, setTripDetails] = useState<TripDetailsResponse | null>(null)
  const [availableActivities, setAvailableActivities] = useState<AttractionResponse[]>([])
  const [selectedDayIndex, setSelectedDayIndex] = useState<number>(1)
  const [selectedActivityIndex, setSelectedActivityIndex] = useState<number>(0)
  const [loading, setLoading] = useState<boolean>(true)
  const [error, setError] = useState<string | null>(null)

  const loadTripDetails = useCallback(async (tripId: number) => {
    try {
      setLoading(true)
      setError(null)
      const details = await api.trips.getDetails(tripId)
      setTripDetails(details)
      
      // Always ensure first day is selected when trip details load
      if (details && details.num_days >= 1) {
        // Always select day 1 by default (even if it doesn't exist in the database yet)
        setSelectedDayIndex(1)
        console.log(`Trip details loaded: num_days=${details.num_days}, existing_days=${details.days?.length || 0}, setting selectedDayIndex to 1`)
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to load trip details'
      setError(errorMessage)
      console.error('Failed to load trip details:', err)
    } finally {
      setLoading(false)
    }
  }, [])

  const loadAvailableActivities = useCallback(async (tripId: number) => {
    try {
      setError(null)
      const response = await api.attractions.getByTripId(tripId, 50)
      setAvailableActivities(response.attractions)
      // Reset selected activity index if needed
      if (response.attractions.length > 0 && selectedActivityIndex >= response.attractions.length) {
        setSelectedActivityIndex(0)
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to load activities'
      setError(errorMessage)
      console.error('Failed to load activities:', err)
    }
  }, [selectedActivityIndex])

  const selectDay = useCallback((dayIndex: number) => {
    console.log(`selectDay called with dayIndex: ${dayIndex}, tripDetails:`, tripDetails)
    if (tripDetails && dayIndex >= 1 && dayIndex <= tripDetails.num_days) {
      console.log(`Setting selectedDayIndex to ${dayIndex}`)
      setSelectedDayIndex(dayIndex)
    } else {
      console.warn(`Cannot select day ${dayIndex}: tripDetails=${!!tripDetails}, num_days=${tripDetails?.num_days}`)
    }
  }, [tripDetails])

  const selectActivity = useCallback((activityIndex: number) => {
    if (activityIndex >= 0 && activityIndex < availableActivities.length) {
      setSelectedActivityIndex(activityIndex)
    }
  }, [availableActivities.length])

  const nextActivity = useCallback(() => {
    if (availableActivities.length > 0) {
      setSelectedActivityIndex((prev) => (prev + 1) % availableActivities.length)
    }
  }, [availableActivities.length])

  const previousActivity = useCallback(() => {
    if (availableActivities.length > 0) {
      setSelectedActivityIndex((prev) => (prev - 1 + availableActivities.length) % availableActivities.length)
    }
  }, [availableActivities.length])

  const refreshTripDetails = useCallback(async () => {
    if (tripId) {
      await loadTripDetails(tripId)
    }
  }, [tripId, loadTripDetails])

  const addActivityToDay = useCallback(async (activityId: number, slot: string) => {
    if (!tripDetails) return

    let selectedDay = tripDetails.days.find((day) => day.day_index === selectedDayIndex)
    
    // If day doesn't exist, create it first
    if (!selectedDay) {
      try {
        console.log(`Creating day ${selectedDayIndex} for trip ${tripDetails.id}`)
        // Get Alpena city ID for default (we'll look it up or use null)
        const alpenaCityId = null // Will be set by backend if null
        selectedDay = await api.tripDays.create(tripDetails.id, selectedDayIndex, alpenaCityId)
        
        // Refresh trip details to get the new day
        await refreshTripDetails()
        
        // Find the day again after refresh
        const refreshedDetails = await api.trips.getDetails(tripDetails.id)
        selectedDay = refreshedDetails.days.find((day) => day.day_index === selectedDayIndex)
        
        if (!selectedDay) {
          setError('Failed to create day')
          return
        }
      } catch (err) {
        const errorMessage = err instanceof Error ? err.message : 'Failed to create day'
        setError(errorMessage)
        console.error('Failed to create day:', err)
        throw err
      }
    }

    try {
      setError(null)
      
      // Get current stops for the day to determine next order_index
      const currentStops = selectedDay.stops || []
      const maxOrderIndex = currentStops.length > 0
        ? Math.max(...currentStops.map((stop) => stop.order_index))
        : -1
      const nextOrderIndex = maxOrderIndex + 1

      const request: CreateTripStopRequest = {
        attraction_id: activityId,
        slot,
        order_index: nextOrderIndex,
      }

      await api.tripStops.create(tripDetails.id, selectedDay.id, request)
      
      // Refresh trip details after adding
      await refreshTripDetails()
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to add activity'
      setError(errorMessage)
      console.error('Failed to add activity:', err)
      throw err
    }
  }, [tripDetails, selectedDayIndex, refreshTripDetails])

  const removeActivityFromDay = useCallback(async (stopId: number) => {
    if (!tripDetails) return

    const selectedDay = tripDetails.days.find((day) => day.day_index === selectedDayIndex)
    if (!selectedDay) {
      setError('Selected day not found')
      return
    }

    try {
      setError(null)
      await api.tripStops.delete(tripDetails.id, selectedDay.id, stopId)
      
      // Refresh trip details after removing
      await refreshTripDetails()
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to remove activity'
      setError(errorMessage)
      console.error('Failed to remove activity:', err)
      throw err
    }
  }, [tripDetails, selectedDayIndex, refreshTripDetails])

  // Load trip details and activities on mount
  useEffect(() => {
    if (tripId) {
      loadTripDetails(tripId).then(() => {
        loadAvailableActivities(tripId)
      })
    }
  }, [tripId, loadTripDetails, loadAvailableActivities])

  const value: TripPlannerContextValue = {
    tripDetails,
    availableActivities,
    selectedDayIndex,
    selectedActivityIndex,
    loading,
    error,
    loadTripDetails,
    loadAvailableActivities,
    selectDay,
    selectActivity,
    nextActivity,
    previousActivity,
    addActivityToDay,
    removeActivityFromDay,
    refreshTripDetails,
  }

  return (
    <TripPlannerContext.Provider value={value}>
      {children}
    </TripPlannerContext.Provider>
  )
}

export function useTripPlanner() {
  const context = useContext(TripPlannerContext)
  if (context === undefined) {
    throw new Error('useTripPlanner must be used within a TripPlannerProvider')
  }
  return context
}


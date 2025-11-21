'use client'

import React, { useState, useEffect, useCallback } from 'react'
import { useRouter } from 'next/navigation'
import { api, MessageResponse, TripResponse, ActiveTripSeedResponse, TripSeedStateResponse } from '@/lib/api'
import { TripChat } from './TripChat'
import { ConversationSidebar } from './ConversationSidebar'
import { PastTrips } from './PastTrips'
import { TripCompleteModal } from './TripCompleteModal'
import { MichiganLoader } from './MichiganLoader'

type TabType = 'past-trips' | 'chat'

export function Dashboard() {
  const router = useRouter()
  const [activeTab, setActiveTab] = useState<TabType>('past-trips') // Default to past trips
  const [trips, setTrips] = useState<TripResponse[]>([])
  const [activeTripSeeds, setActiveTripSeeds] = useState<ActiveTripSeedResponse[]>([])
  const [messages, setMessages] = useState<MessageResponse[]>([])
  const [currentConversationId, setCurrentConversationId] = useState<number | null>(null)
  const [tripSeedState, setTripSeedState] = useState<TripSeedStateResponse | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [isLoadingConversations, setIsLoadingConversations] = useState(true)
  const [isCreatingTrip, setIsCreatingTrip] = useState(false)
  const [showCompleteModal, setShowCompleteModal] = useState(false)

  // Load trips and active trip seeds on mount
  useEffect(() => {
    loadTripsAndConversations()
  }, [])

  // Load conversation messages when conversation ID changes
  useEffect(() => {
    if (currentConversationId) {
      loadConversationMessages(currentConversationId)
    } else {
      setMessages([])
      setTripSeedState(null)
    }
  }, [currentConversationId])

  const loadTripsAndConversations = async () => {
    try {
      setIsLoadingConversations(true)
      
      // Start loading data and minimum display time in parallel
      const [data] = await Promise.all([
        api.trips.getAll(),
        // Minimum 2 second display time for the cool loader effect
        new Promise(resolve => setTimeout(resolve, 2000))
      ])
      
      setTrips(data.trips)
      setActiveTripSeeds(data.active_trip_seeds)
      
      // If there's an active conversation, select the most recent one
      if (data.active_trip_seeds.length > 0 && !currentConversationId) {
        const mostRecent = data.active_trip_seeds[0]
        setCurrentConversationId(mostRecent.conversation_id)
      }
    } catch (error) {
      console.error('Failed to load trips and conversations:', error)
    } finally {
      setIsLoadingConversations(false)
    }
  }

  const loadConversationMessages = async (conversationId: number) => {
    try {
      // Try to get conversation from API
      // If endpoint doesn't exist, we'll work with messages we track locally
      try {
        const conversation = await api.conversations.getById(conversationId)
        setMessages(conversation.messages)
        
        // Find the corresponding trip seed state
        const tripSeed = activeTripSeeds.find(
          (seed) => seed.conversation_id === conversationId
        )
        if (tripSeed) {
          setTripSeedState({
            trip_seed_id: tripSeed.trip_seed_id,
            conversation_id: tripSeed.conversation_id,
            num_days: tripSeed.num_days,
            trip_mode: tripSeed.trip_mode,
            budget_band: tripSeed.budget_band,
            start_location_text: tripSeed.start_location_text,
            companions: tripSeed.companions,
            status: tripSeed.status,
            is_complete: tripSeed.is_complete,
            missing_fields: tripSeed.missing_fields,
          })
        }
      } catch (error) {
        // Endpoint might not exist, so we'll track messages locally
        console.warn('Conversation endpoint not available, using local state')
        // Messages will be tracked in sendMessage
      }
    } catch (error) {
      console.error('Failed to load conversation messages:', error)
    }
  }

  const sendMessage = async (message: string) => {
    if (!message.trim() || isLoading) return

    try {
      setIsLoading(true)
      
      // Add user message to UI immediately
      const userMessage: MessageResponse = {
        id: Date.now(), // Temporary ID
        role: 'user',
        content: message,
        created_at: new Date().toISOString(),
      }
      setMessages((prev) => [...prev, userMessage])

      // Send message to API
      const response = await api.tripSeed.sendMessage({
        message,
        conversation_id: currentConversationId || undefined,
      })

      // Update conversation ID if this is a new conversation
      if (response.conversation_id !== currentConversationId) {
        setCurrentConversationId(response.conversation_id)
      }

      // Add AI response to messages
      const aiMessage: MessageResponse = {
        id: Date.now() + 1, // Temporary ID
        role: 'assistant',
        content: response.response_text,
        created_at: new Date().toISOString(),
      }
      setMessages((prev) => [...prev, aiMessage])

      // Update trip seed state
      setTripSeedState(response.trip_seed_state)
      
      // Check if trip is complete - use backend's is_complete flag and verify no missing fields
      const tripState = response.trip_seed_state
      const isComplete = tripState.is_complete && tripState.missing_fields.length === 0
      
      // Debug logging
      console.log('🔍 Trip completion check:', {
        is_complete: tripState.is_complete,
        missing_fields: tripState.missing_fields,
        num_days: tripState.num_days,
        trip_mode: tripState.trip_mode,
        budget_band: tripState.budget_band,
        start_location_text: tripState.start_location_text,
        companions: tripState.companions,
        calculated_complete: isComplete,
      })
      
      if (isComplete) {
        console.log('✅ Trip is complete, showing modal')
        setShowCompleteModal(true)
      } else {
        console.log('❌ Trip is NOT complete yet:', {
          reason: tripState.missing_fields.length > 0 
            ? `Missing fields: ${tripState.missing_fields.join(', ')}`
            : 'is_complete is false'
        })
      }

      // Refresh conversations list to get updated state
      await loadTripsAndConversations()
    } catch (error) {
      console.error('Failed to send message:', error)
      // Remove the user message on error
      setMessages((prev) => prev.slice(0, -1))
      alert('Failed to send message. Please try again.')
    } finally {
      setIsLoading(false)
    }
  }

  const handleSelectConversation = useCallback((conversationId: number) => {
    setCurrentConversationId(conversationId)
  }, [])

  const handleNewConversation = useCallback(() => {
    setCurrentConversationId(null)
    setMessages([])
    setTripSeedState(null)
  }, [])

  const handleDeleteConversation = async (conversationId: number) => {
    try {
      await api.conversations.delete(conversationId)
      
      // If we deleted the active conversation, clear it
      if (conversationId === currentConversationId) {
        handleNewConversation()
      }
      
      // Refresh the conversations list
      await loadTripsAndConversations()
    } catch (error) {
      console.error('Failed to delete conversation:', error)
      alert('Failed to delete conversation. Please try again.')
    }
  }

  const handleCreateTrip = async () => {
    if (!tripSeedState) return

    const tripName = prompt('Enter a name for your trip:')
    if (!tripName) return

    try {
      setIsCreatingTrip(true)
      const newTrip = await api.trips.createFromSeed({
        trip_seed_id: tripSeedState.trip_seed_id,
        name: tripName,
      })
      
      setShowCompleteModal(false)
      // Refresh trips list
      await loadTripsAndConversations()
      
      // Clear current conversation
      handleNewConversation()
      
      // Navigate to trip planning page
      router.push(`/trip/${newTrip.id}`)
    } catch (error) {
      console.error('Failed to create trip:', error)
      alert('Failed to create trip. Please try again.')
    } finally {
      setIsCreatingTrip(false)
    }
  }

  const handleTripClick = (tripId: number) => {
    // Navigate to trip planning page
    router.push(`/trip/${tripId}`)
  }

  if (isLoadingConversations) {
    return (
      <div className="flex items-center justify-center h-screen" style={{ backgroundColor: 'var(--color-background)' }}>
        <div className="text-center">
          <MichiganLoader size={100} />
          <p 
            className="mt-4 text-sm"
            style={{ color: 'var(--color-muted-foreground)' }}
          >
            Loading your trips...
          </p>
        </div>
      </div>
    )
  }

  return (
    <div 
      className="flex h-screen flex-col"
      style={{ backgroundColor: 'var(--color-background)' }}
    >
      {/* Tabs */}
      <div 
        className="flex border-b"
        style={{ 
          borderColor: 'var(--color-border)',
          backgroundColor: 'var(--color-card)',
        }}
      >
        <button
          onClick={() => setActiveTab('past-trips')}
          className="px-6 py-3 font-medium text-sm transition-colors relative"
          style={{
            color: activeTab === 'past-trips' ? 'var(--color-foreground)' : 'var(--color-muted-foreground)',
            backgroundColor: activeTab === 'past-trips' ? 'var(--color-background)' : 'transparent',
          }}
        >
          Past Trips
          {activeTab === 'past-trips' && (
            <div 
              className="absolute bottom-0 left-0 right-0 h-0.5"
              style={{ backgroundColor: 'var(--color-primary)' }}
            />
          )}
        </button>
        <button
          onClick={() => setActiveTab('chat')}
          className="px-6 py-3 font-medium text-sm transition-colors relative"
          style={{
            color: activeTab === 'chat' ? 'var(--color-foreground)' : 'var(--color-muted-foreground)',
            backgroundColor: activeTab === 'chat' ? 'var(--color-background)' : 'transparent',
          }}
        >
          Chat
          {activeTab === 'chat' && (
            <div 
              className="absolute bottom-0 left-0 right-0 h-0.5"
              style={{ backgroundColor: 'var(--color-primary)' }}
            />
          )}
        </button>
      </div>

      {/* Tab Content */}
      <div className="flex flex-1 overflow-hidden">
        {activeTab === 'past-trips' ? (
          <div className="flex-1 overflow-y-auto p-6">
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
              {trips.map((trip) => (
                <button
                  key={trip.id}
                  onClick={() => handleTripClick(trip.id)}
                  className="group flex flex-col overflow-hidden rounded-lg transition-all hover:scale-[1.02] hover:shadow-lg text-left"
                  style={{
                    backgroundColor: 'var(--color-card)',
                    border: `1px solid var(--color-border)`,
                  }}
                >
                  {/* Card Image */}
                  <div className="relative w-full h-48 overflow-hidden">
                    <img
                      src={trip.cover_image_url || '/img/michigan_default.png'}
                      alt={trip.name}
                      className="w-full h-full object-cover transition-transform group-hover:scale-110"
                      onError={(e) => {
                        console.error('Failed to load image:', trip.cover_image_url || '/img/michigan_default.png')
                        // Fallback to default if even that fails
                        e.currentTarget.src = '/img/michigan_default.png'
                      }}
                    />
                  </div>
                  
                  {/* Card Body */}
                  <div className="p-4 flex-1 flex flex-col">
                    <div className="font-semibold text-base mb-2" style={{ color: 'var(--color-foreground)' }}>
                      {trip.name}
                    </div>
                    <div className="flex items-center gap-2 flex-wrap text-sm mb-2">
                      {trip.start_location_text && (
                        <span style={{ color: 'var(--color-muted-foreground)' }}>
                          📍 {trip.start_location_text}
                        </span>
                      )}
                      <span style={{ color: 'var(--color-muted-foreground)' }}>
                        {trip.num_days} {trip.num_days === 1 ? 'day' : 'days'}
                      </span>
                    </div>
                    <div className="flex items-center gap-2 flex-wrap mt-auto">
                      <span 
                        className="text-xs px-2 py-1 rounded-full capitalize"
                        style={{
                          backgroundColor: trip.status === 'completed' 
                            ? 'var(--color-primary)' 
                            : 'var(--color-muted)',
                          color: trip.status === 'completed'
                            ? 'var(--color-primary-foreground)'
                            : 'var(--color-muted-foreground)',
                        }}
                      >
                        {trip.status}
                      </span>
                      {trip.trip_mode && (
                        <span 
                          className="text-xs px-2 py-1 rounded"
                          style={{
                            backgroundColor: 'var(--color-muted)',
                            color: 'var(--color-muted-foreground)',
                          }}
                        >
                          {trip.trip_mode.replace('_', ' ')}
                        </span>
                      )}
                    </div>
                  </div>
                </button>
              ))}
            </div>
            {trips.length === 0 && (
              <div className="text-center py-12">
                <p style={{ color: 'var(--color-muted-foreground)' }}>
                  No past trips yet. Start planning your first trip!
                </p>
              </div>
            )}
          </div>
        ) : (
          /* Chat Tab */
          <div className="flex flex-1 overflow-hidden relative">
            {/* Chat Area */}
            <div className="flex-1 flex flex-col overflow-hidden">
              <TripChat
                conversationId={currentConversationId}
                messages={messages}
                isLoading={isLoading}
                tripSeedState={tripSeedState}
                onSendMessage={sendMessage}
                onNewConversation={handleNewConversation}
              />
            </div>

            {/* Complete Modal */}
            {tripSeedState && showCompleteModal && (
              <TripCompleteModal
                tripSeedState={tripSeedState}
                onCreateTrip={handleCreateTrip}
                onClose={() => setShowCompleteModal(false)}
                isLoading={isCreatingTrip}
              />
            )}

            {/* Conversation Sidebar */}
            <ConversationSidebar
              conversations={activeTripSeeds}
              activeConversationId={currentConversationId}
              onSelectConversation={handleSelectConversation}
              onNewConversation={handleNewConversation}
              onDeleteConversation={handleDeleteConversation}
            />
          </div>
        )}
      </div>
    </div>
  )
}


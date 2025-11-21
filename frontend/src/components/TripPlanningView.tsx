'use client'

import React, { useState, useEffect, useCallback } from 'react'
import { useRouter } from 'next/navigation'
import { api, MessageResponse, TripResponse, ActiveTripSeedResponse, TripSeedStateResponse } from '@/lib/api'
import { TripChat } from './TripChat'
import { ConversationSidebar } from './ConversationSidebar'
import { TripCompleteModal } from './TripCompleteModal'
import { MichiganLoader } from './MichiganLoader'

export function TripPlanningView() {
  const router = useRouter()
  const [activeTripSeeds, setActiveTripSeeds] = useState<ActiveTripSeedResponse[]>([])
  const [messages, setMessages] = useState<MessageResponse[]>([])
  const [currentConversationId, setCurrentConversationId] = useState<number | null>(null)
  const [tripSeedState, setTripSeedState] = useState<TripSeedStateResponse | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [isLoadingConversations, setIsLoadingConversations] = useState(true)
  const [isCreatingTrip, setIsCreatingTrip] = useState(false)
  const [showCompleteModal, setShowCompleteModal] = useState(false)

  // Load active trip seeds on mount
  useEffect(() => {
    loadActiveTripSeeds()
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

  const loadActiveTripSeeds = async () => {
    try {
      setIsLoadingConversations(true)
      const data = await api.trips.getAll()
      setActiveTripSeeds(data.active_trip_seeds)
      
      // If there's an active conversation, select the most recent one
      if (data.active_trip_seeds.length > 0 && !currentConversationId) {
        const mostRecent = data.active_trip_seeds[0]
        setCurrentConversationId(mostRecent.conversation_id)
      }
    } catch (error) {
      console.error('Failed to load conversations:', error)
    } finally {
      setIsLoadingConversations(false)
    }
  }

  const loadConversationMessages = async (conversationId: number) => {
    try {
      try {
        const conversation = await api.conversations.getById(conversationId)
        setMessages(conversation.messages)
        
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
        console.warn('Conversation endpoint not available, using local state')
      }
    } catch (error) {
      console.error('Failed to load conversation messages:', error)
    }
  }

  const sendMessage = async (message: string) => {
    if (!message.trim() || isLoading) return

    try {
      setIsLoading(true)
      
      const userMessage: MessageResponse = {
        id: Date.now(),
        role: 'user',
        content: message,
        created_at: new Date().toISOString(),
      }
      setMessages((prev) => [...prev, userMessage])

      const response = await api.tripSeed.sendMessage({
        message,
        conversation_id: currentConversationId || undefined,
      })

      if (response.conversation_id !== currentConversationId) {
        setCurrentConversationId(response.conversation_id)
      }

      const aiMessage: MessageResponse = {
        id: Date.now() + 1,
        role: 'assistant',
        content: response.response_text,
        created_at: new Date().toISOString(),
      }
      setMessages((prev) => [...prev, aiMessage])

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
      
      await loadActiveTripSeeds()
    } catch (error) {
      console.error('Failed to send message:', error)
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
      await loadActiveTripSeeds()
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
      await loadActiveTripSeeds()
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

  if (isLoadingConversations) {
    return (
      <div className="flex items-center justify-center h-full" style={{ backgroundColor: 'var(--color-background)' }}>
        <div className="text-center">
          <MichiganLoader size={100} />
          <p 
            className="mt-4 text-sm"
            style={{ color: 'var(--color-muted-foreground)' }}
          >
            Loading...
          </p>
        </div>
      </div>
    )
  }

  return (
    <div 
      className="flex h-full overflow-hidden relative"
      style={{ backgroundColor: 'var(--color-background)' }}
    >
      {/* Chat Area */}
      <div className="flex-1 flex flex-col overflow-hidden">
        <TripChat
          conversationId={currentConversationId}
          messages={messages}
          isLoading={isLoading}
          tripSeedState={tripSeedState}
          onSendMessage={sendMessage}
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
  )
}


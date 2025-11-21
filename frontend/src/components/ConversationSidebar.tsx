'use client'

import React from 'react'
import { ActiveTripSeedResponse } from '@/lib/api'

interface ConversationSidebarProps {
  conversations: ActiveTripSeedResponse[]
  activeConversationId?: number | null
  onSelectConversation: (conversationId: number) => void
  onNewConversation: () => void
}

export function ConversationSidebar({
  conversations,
  activeConversationId,
  onSelectConversation,
  onNewConversation,
}: ConversationSidebarProps) {
  const formatDate = (dateString: string) => {
    const date = new Date(dateString)
    const now = new Date()
    const diffTime = Math.abs(now.getTime() - date.getTime())
    const diffDays = Math.floor(diffTime / (1000 * 60 * 60 * 24))

    if (diffDays === 0) {
      return 'Today'
    } else if (diffDays === 1) {
      return 'Yesterday'
    } else if (diffDays < 7) {
      return `${diffDays} days ago`
    } else {
      return date.toLocaleDateString([], { month: 'short', day: 'numeric' })
    }
  }

  const getConversationPreview = (conversation: ActiveTripSeedResponse) => {
    if (conversation.start_location_text) {
      return conversation.start_location_text
    }
    if (conversation.num_days) {
      return `${conversation.num_days} day trip`
    }
    return 'New conversation'
  }

  return (
    <div 
      className="flex flex-col h-full border-l"
      style={{ 
        borderColor: 'var(--color-border)',
        backgroundColor: 'var(--color-card)',
        width: '300px',
        minWidth: '300px',
      }}
    >
      {/* Sidebar Header */}
      <div 
        className="border-b p-4"
        style={{ borderColor: 'var(--color-border)' }}
      >
        <h3 
          className="text-lg font-semibold mb-2"
          style={{ color: 'var(--color-foreground)' }}
        >
          Conversations
        </h3>
        <button
          onClick={onNewConversation}
          className="w-full px-4 py-2 text-sm rounded-md transition-colors font-medium"
          style={{
            backgroundColor: 'var(--color-primary)',
            color: 'var(--color-primary-foreground)',
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.opacity = '0.9'
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.opacity = '1'
          }}
        >
          + New Chat
        </button>
      </div>

      {/* Conversations List */}
      <div className="flex-1 overflow-y-auto">
        {conversations.length === 0 ? (
          <div className="p-4 text-center">
            <p 
              className="text-sm"
              style={{ color: 'var(--color-muted-foreground)' }}
            >
              No previous conversations. Start a new chat to begin planning!
            </p>
          </div>
        ) : (
          <div className="p-2 space-y-1">
            {conversations.map((conversation) => {
              const isActive = conversation.conversation_id === activeConversationId
              return (
                <button
                  key={conversation.conversation_id}
                  onClick={() => onSelectConversation(conversation.conversation_id)}
                  className="w-full text-left p-3 rounded-md transition-colors"
                  style={{
                    backgroundColor: isActive
                      ? 'var(--color-primary)'
                      : 'transparent',
                    color: isActive
                      ? 'var(--color-primary-foreground)'
                      : 'var(--color-foreground)',
                  }}
                  onMouseEnter={(e) => {
                    if (!isActive) {
                      e.currentTarget.style.backgroundColor = 'var(--color-muted)'
                      e.currentTarget.style.opacity = '0.8'
                    }
                  }}
                  onMouseLeave={(e) => {
                    if (!isActive) {
                      e.currentTarget.style.backgroundColor = 'transparent'
                      e.currentTarget.style.opacity = '1'
                    }
                  }}
                >
                  <div className="flex items-start justify-between gap-2">
                    <div className="flex-1 min-w-0">
                      <div className="font-medium text-sm truncate">
                        {getConversationPreview(conversation)}
                      </div>
                      <div 
                        className="text-xs mt-1 truncate"
                        style={{
                          color: isActive
                            ? 'var(--color-primary-foreground)'
                            : 'var(--color-muted-foreground)',
                          opacity: 0.8,
                        }}
                      >
                        {formatDate(conversation.updated_at)}
                      </div>
                      {conversation.is_complete && (
                        <div 
                          className="text-xs mt-1 font-medium"
                          style={{
                            color: isActive
                              ? 'var(--color-primary-foreground)'
                              : 'var(--color-primary)',
                          }}
                        >
                          ✓ Ready
                        </div>
                      )}
                    </div>
                  </div>
                </button>
              )
            })}
          </div>
        )}
      </div>
    </div>
  )
}


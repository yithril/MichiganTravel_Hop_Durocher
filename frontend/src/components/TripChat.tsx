'use client'

import React, { useState, useEffect, useRef } from 'react'
import { MessageResponse, TripSeedStateResponse } from '@/lib/api'
import { MichiganLoader } from './MichiganLoader'

interface TripChatProps {
  conversationId?: number | null
  messages: MessageResponse[]
  isLoading?: boolean
  tripSeedState?: TripSeedStateResponse | null
  onSendMessage: (message: string) => void
}

export function TripChat({
  conversationId,
  messages,
  isLoading = false,
  tripSeedState,
  onSendMessage,
}: TripChatProps) {
  const [inputValue, setInputValue] = useState('')
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLTextAreaElement>(null)

  // Auto-scroll to bottom when messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, isLoading])

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (inputValue.trim() && !isLoading) {
      onSendMessage(inputValue.trim())
      setInputValue('')
      // Reset textarea height
      if (inputRef.current) {
        inputRef.current.style.height = 'auto'
      }
    }
  }

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSubmit(e)
    }
  }

  const handleInputChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setInputValue(e.target.value)
    // Auto-resize textarea
    e.target.style.height = 'auto'
    e.target.style.height = `${Math.min(e.target.scrollHeight, 120)}px`
  }

  return (
    <div className="flex flex-col h-full" style={{ backgroundColor: 'var(--color-background)' }}>
      {/* Chat Header */}
      <div 
        className="border-b p-4"
        style={{ 
          borderColor: 'var(--color-border)',
          backgroundColor: 'var(--color-card)'
        }}
      >
        <div>
          <h2 className="text-lg font-semibold" style={{ color: 'var(--color-foreground)' }}>
            Plan Your Trip
          </h2>
          <p className="text-sm" style={{ color: 'var(--color-muted-foreground)' }}>
            Chat with our AI to plan your perfect Michigan adventure
          </p>
        </div>
      </div>

      {/* Messages Container */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 && !isLoading && (
          <div className="flex flex-col items-center justify-center h-full text-center">
            <div className="mb-4">
              <div 
                className="text-6xl mb-2"
                style={{ color: 'var(--color-primary)' }}
              >
                🗺️
              </div>
            </div>
            <h3 
              className="text-xl font-semibold mb-2"
              style={{ color: 'var(--color-foreground)' }}
            >
              Start Planning Your Trip
            </h3>
            <p 
              className="text-sm max-w-md"
              style={{ color: 'var(--color-muted-foreground)' }}
            >
              Tell me about your dream trip! Where would you like to go? How many days? What's your travel style?
            </p>
          </div>
        )}

        {messages.map((message) => (
          <div
            key={message.id}
            className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`max-w-[80%] rounded-lg px-4 py-2 ${
                message.role === 'user'
                  ? 'rounded-br-none'
                  : 'rounded-bl-none'
              }`}
              style={{
                backgroundColor:
                  message.role === 'user'
                    ? 'var(--color-primary)'
                    : 'var(--color-card)',
                color:
                  message.role === 'user'
                    ? 'var(--color-primary-foreground)'
                    : 'var(--color-card-foreground)',
                border: `1px solid var(--color-border)`,
              }}
            >
              <div className="text-sm whitespace-pre-wrap break-words">
                {message.content}
              </div>
              <div
                className="text-xs mt-1 opacity-70"
                style={{
                  color:
                    message.role === 'user'
                      ? 'var(--color-primary-foreground)'
                      : 'var(--color-muted-foreground)',
                }}
              >
                {new Date(message.created_at).toLocaleTimeString([], {
                  hour: '2-digit',
                  minute: '2-digit',
                })}
              </div>
            </div>
          </div>
        ))}

        {isLoading && (
          <div className="flex justify-start">
            <div
              className="rounded-lg rounded-bl-none px-4 py-2"
              style={{
                backgroundColor: 'var(--color-card)',
                border: `1px solid var(--color-border)`,
              }}
            >
              <div className="flex items-center gap-2">
                <MichiganLoader size={24} />
                <span 
                  className="text-sm"
                  style={{ color: 'var(--color-muted-foreground)' }}
                >
                  Planning your trip...
                </span>
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div 
        className="border-t p-4"
        style={{ 
          borderColor: 'var(--color-border)',
          backgroundColor: 'var(--color-card)'
        }}
      >
        <form onSubmit={handleSubmit} className="flex gap-2">
          <textarea
            ref={inputRef}
            value={inputValue}
            onChange={handleInputChange}
            onKeyDown={handleKeyDown}
            placeholder="Type your message... (Press Enter to send, Shift+Enter for new line)"
            disabled={isLoading}
            rows={1}
            className="flex-1 resize-none rounded-md px-4 py-2 text-sm focus:outline-none focus:ring-2 transition-all"
            style={{
              backgroundColor: 'var(--color-background)',
              color: 'var(--color-foreground)',
              border: `1px solid var(--color-input)`,
              minHeight: '40px',
              maxHeight: '120px',
            }}
            onFocus={(e) => {
              e.target.style.borderColor = 'var(--color-ring)'
            }}
            onBlur={(e) => {
              e.target.style.borderColor = 'var(--color-input)'
            }}
          />
          <button
            type="submit"
            disabled={!inputValue.trim() || isLoading}
            className="px-6 py-2 rounded-md text-sm font-medium transition-all disabled:opacity-50 disabled:cursor-not-allowed"
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
            Send
          </button>
        </form>
      </div>
    </div>
  )
}


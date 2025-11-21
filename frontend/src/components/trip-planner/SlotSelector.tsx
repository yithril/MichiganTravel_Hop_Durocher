'use client'

import React, { useState } from 'react'

interface SlotSelectorProps {
  onSelect: (slot: string) => void
  onCancel: () => void
  isOpen: boolean
}

const SLOT_OPTIONS = [
  { value: 'morning', label: '🌅 Morning' },
  { value: 'afternoon', label: '☀️ Afternoon' },
  { value: 'evening', label: '🌙 Evening' },
  { value: 'flex', label: '🕐 Flexible' },
]

export function SlotSelector({ onSelect, onCancel, isOpen }: SlotSelectorProps) {
  const [selectedSlot, setSelectedSlot] = useState<string>('')

  if (!isOpen) {
    return null
  }

  const handleConfirm = () => {
    if (selectedSlot) {
      onSelect(selectedSlot)
      setSelectedSlot('')
    }
  }

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center"
      style={{ backgroundColor: 'rgba(0, 0, 0, 0.5)' }}
      onClick={onCancel}
    >
      <div
        className="rounded-lg p-6 max-w-md w-full mx-4"
        style={{
          backgroundColor: 'var(--color-card)',
          border: `1px solid var(--color-border)`,
        }}
        onClick={(e) => e.stopPropagation()}
      >
        <h3
          className="text-lg font-semibold mb-4"
          style={{ color: 'var(--color-foreground)' }}
        >
          Select Time Slot
        </h3>
        <div className="space-y-2 mb-6">
          {SLOT_OPTIONS.map((option) => (
            <button
              key={option.value}
              onClick={() => setSelectedSlot(option.value)}
              className="w-full text-left px-4 py-3 rounded-md transition-all"
              style={{
                backgroundColor:
                  selectedSlot === option.value
                    ? 'var(--color-primary)'
                    : 'var(--color-background)',
                color:
                  selectedSlot === option.value
                    ? 'var(--color-primary-foreground)'
                    : 'var(--color-foreground)',
                border: `1px solid var(--color-border)`,
              }}
            >
              {option.label}
            </button>
          ))}
        </div>
        <div className="flex gap-2 justify-end">
          <button
            onClick={onCancel}
            className="px-4 py-2 rounded-md transition-all"
            style={{
              backgroundColor: 'var(--color-muted)',
              color: 'var(--color-muted-foreground)',
            }}
          >
            Cancel
          </button>
          <button
            onClick={handleConfirm}
            disabled={!selectedSlot}
            className="px-4 py-2 rounded-md transition-all disabled:opacity-50 disabled:cursor-not-allowed"
            style={{
              backgroundColor: 'var(--color-primary)',
              color: 'var(--color-primary-foreground)',
            }}
          >
            Add Activity
          </button>
        </div>
      </div>
    </div>
  )
}


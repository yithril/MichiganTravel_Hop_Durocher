'use client'

import React, { useState } from 'react'

type DashboardView = 'plan-trip' | 'past-trips'

interface DashboardLayoutProps {
  children: React.ReactNode
  currentView: DashboardView
  onViewChange: (view: DashboardView) => void
}

export function DashboardLayout({ children, currentView, onViewChange }: DashboardLayoutProps) {
  return (
    <div 
      className="flex h-screen"
      style={{ backgroundColor: 'var(--color-background)' }}
    >
      {/* Sidebar */}
      <div 
        className="w-64 border-r flex flex-col"
        style={{ 
          borderColor: 'var(--color-border)',
          backgroundColor: 'var(--color-card)',
        }}
      >
        {/* Sidebar Header */}
        <div 
          className="p-4 border-b"
          style={{ borderColor: 'var(--color-border)' }}
        >
          <h2 
            className="text-lg font-semibold"
            style={{ color: 'var(--color-foreground)' }}
          >
            Dashboard
          </h2>
        </div>

        {/* Sidebar Menu */}
        <nav className="flex-1 p-4 space-y-2">
          <button
            onClick={() => onViewChange('plan-trip')}
            className={`w-full text-left px-4 py-3 rounded-md transition-all font-medium ${
              currentView === 'plan-trip' ? '' : ''
            }`}
            style={{
              backgroundColor: currentView === 'plan-trip'
                ? 'var(--color-primary)'
                : 'transparent',
              color: currentView === 'plan-trip'
                ? 'var(--color-primary-foreground)'
                : 'var(--color-foreground)',
            }}
            onMouseEnter={(e) => {
              if (currentView !== 'plan-trip') {
                e.currentTarget.style.backgroundColor = 'var(--color-muted)'
                e.currentTarget.style.opacity = '0.8'
              }
            }}
            onMouseLeave={(e) => {
              if (currentView !== 'plan-trip') {
                e.currentTarget.style.backgroundColor = 'transparent'
                e.currentTarget.style.opacity = '1'
              }
            }}
          >
            <div className="flex items-center gap-2">
              <span className="text-lg">🗺️</span>
              <span>Start a New Trip</span>
            </div>
          </button>

          <button
            onClick={() => onViewChange('past-trips')}
            className={`w-full text-left px-4 py-3 rounded-md transition-all font-medium ${
              currentView === 'past-trips' ? '' : ''
            }`}
            style={{
              backgroundColor: currentView === 'past-trips'
                ? 'var(--color-primary)'
                : 'transparent',
              color: currentView === 'past-trips'
                ? 'var(--color-primary-foreground)'
                : 'var(--color-foreground)',
            }}
            onMouseEnter={(e) => {
              if (currentView !== 'past-trips') {
                e.currentTarget.style.backgroundColor = 'var(--color-muted)'
                e.currentTarget.style.opacity = '0.8'
              }
            }}
            onMouseLeave={(e) => {
              if (currentView !== 'past-trips') {
                e.currentTarget.style.backgroundColor = 'transparent'
                e.currentTarget.style.opacity = '1'
              }
            }}
          >
            <div className="flex items-center gap-2">
              <span className="text-lg">📅</span>
              <span>Past Trips</span>
            </div>
          </button>
        </nav>
      </div>

      {/* Main Content Area */}
      <div className="flex-1 overflow-hidden">
        {children}
      </div>
    </div>
  )
}


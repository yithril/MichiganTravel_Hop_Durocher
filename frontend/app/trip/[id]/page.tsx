'use client'

import React, { Suspense } from 'react'
import { useParams } from 'next/navigation'
import { useSession } from 'next-auth/react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { TripPlanner } from '@/components/trip-planner/TripPlanner'
import SignOutButton from '@/components/SignOutButton'
import { MichiganLoader } from '@/components/MichiganLoader'

/**
 * Trip Planning Page
 * 
 * Displays the trip planning interface with day-by-day itinerary planning.
 * Includes top navigation menu.
 */
function TripPlanningContent() {
  const params = useParams()
  const { data: session, status } = useSession()
  const router = useRouter()
  const tripId = parseInt(params.id as string, 10)

  React.useEffect(() => {
    if (status === 'unauthenticated') {
      router.push('/login')
    }
  }, [status, router])

  if (status === 'loading' || !session) {
    return (
      <div className="flex items-center justify-center h-screen" style={{ backgroundColor: 'var(--color-background)' }}>
        <MichiganLoader />
      </div>
    )
  }

  if (isNaN(tripId)) {
    return (
      <div className="min-h-screen flex items-center justify-center" style={{ backgroundColor: 'var(--color-background)' }}>
        <div className="text-center">
          <h1 className="text-2xl font-bold mb-2" style={{ color: 'var(--color-foreground)' }}>
            Invalid Trip ID
          </h1>
          <p className="text-sm" style={{ color: 'var(--color-muted-foreground)' }}>
            The trip ID is not valid.
          </p>
        </div>
      </div>
    )
  }

  return (
    <div className="flex flex-col h-screen" style={{ backgroundColor: 'var(--color-background)' }}>
      {/* Navigation */}
      <nav 
        className="border-b"
        style={{ 
          borderColor: 'var(--color-border)',
          backgroundColor: 'var(--color-card)',
        }}
      >
        <div className="container mx-auto flex h-16 items-center justify-between px-4">
          <Link 
            href="/dashboard"
            className="flex items-center"
          >
            <img 
              src="/img/logo.png" 
              alt="Hidden Gems" 
              style={{ maxHeight: '100px', height: 'auto', width: 'auto', objectFit: 'contain' }}
            />
          </Link>
          <div className="flex items-center gap-4">
            <span 
              className="text-sm"
              style={{ color: 'var(--color-muted-foreground)' }}
            >
              {session.user?.email}
            </span>
            <SignOutButton />
          </div>
        </div>
      </nav>

      {/* Trip Planner */}
      <div className="flex-1 overflow-hidden">
        <TripPlanner tripId={tripId} />
      </div>
    </div>
  )
}

export default function TripPlanningPage() {
  return (
    <Suspense fallback={
      <div className="flex items-center justify-center h-screen" style={{ backgroundColor: 'var(--color-background)' }}>
        <MichiganLoader />
      </div>
    }>
      <TripPlanningContent />
    </Suspense>
  )
}


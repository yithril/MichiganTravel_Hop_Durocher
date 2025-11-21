'use client'

import { useEffect, useState, Suspense } from 'react'
import { useSession } from 'next-auth/react'
import { useRouter } from 'next/navigation'
import { DashboardLayout } from '@/components/DashboardLayout'
import { TripPlanningView } from '@/components/TripPlanningView'
import { PastTripsView } from '@/components/PastTripsView'
import Link from 'next/link'
import SignOutButton from './SignOutButton'
import { MichiganLoader } from '@/components/MichiganLoader'

type DashboardView = 'plan-trip' | 'past-trips'

function DashboardContent() {
  const { data: session, status } = useSession()
  const router = useRouter()
  const [currentView, setCurrentView] = useState<DashboardView>('plan-trip')

  useEffect(() => {
    if (status === 'unauthenticated') {
      router.push('/login')
    }
  }, [status, router])

  if (status === 'loading' || !session) {
    return (
      <div className="flex items-center justify-center h-screen" style={{ backgroundColor: 'var(--color-background)' }}>
        <MichiganLoader size={100} />
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
            href="/" 
            className="text-xl font-bold"
            style={{ color: 'var(--color-foreground)' }}
          >
            Michigan Adventures
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

      {/* Dashboard with Sidebar */}
      <DashboardLayout currentView={currentView} onViewChange={setCurrentView}>
        {currentView === 'plan-trip' ? (
          <TripPlanningView />
        ) : (
          <PastTripsView />
        )}
      </DashboardLayout>
    </div>
  )
}

export default function DashboardPage() {
  return (
    <Suspense fallback={
      <div className="flex items-center justify-center h-screen" style={{ backgroundColor: 'var(--color-background)' }}>
        <MichiganLoader size={100} />
      </div>
    }>
      <DashboardContent />
    </Suspense>
  )
}


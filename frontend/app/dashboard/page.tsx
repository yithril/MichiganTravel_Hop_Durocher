import { getSession } from '@/lib/get-session'
import { redirect } from 'next/navigation'
import { Dashboard } from '@/components/Dashboard'
import Link from 'next/link'
import SignOutButton from './SignOutButton'

export default async function DashboardPage() {
  const session = await getSession()

  if (!session) {
    redirect('/login')
  }

  return (
    <div className="flex min-h-screen flex-col" style={{ backgroundColor: 'var(--color-background)' }}>
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

      {/* Main Dashboard Content */}
      <Dashboard />
    </div>
  )
}


import { getSession } from '@/lib/get-session'
import { redirect } from 'next/navigation'
import Link from 'next/link'
import SignOutButton from './SignOutButton'

export default async function DashboardPage() {
  const session = await getSession()

  if (!session) {
    redirect('/login')
  }

  return (
    <div className="flex min-h-screen flex-col">
      {/* Navigation */}
      <nav className="border-b">
        <div className="container mx-auto flex h-16 items-center justify-between px-4">
          <Link href="/" className="text-xl font-bold">
            Your App
          </Link>
          <div className="flex items-center gap-4">
            <span className="text-sm text-muted-foreground">
              {session.user?.email}
            </span>
            <SignOutButton />
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="container mx-auto p-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold">Dashboard</h1>
          <p className="text-muted-foreground">
            Welcome back, {session.user?.name || session.user?.email}!
          </p>
        </div>

        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          <div className="rounded-lg border p-6">
            <h2 className="mb-2 text-xl font-semibold">User Information</h2>
            <div className="space-y-2 text-sm">
              <p>
                <span className="font-medium">Email:</span> {session.user?.email}
              </p>
              <p>
                <span className="font-medium">Name:</span> {session.user?.name || 'N/A'}
              </p>
              <p>
                <span className="font-medium">Role:</span> {session.user?.role || 'N/A'}
              </p>
            </div>
          </div>

          <div className="rounded-lg border p-6">
            <h2 className="mb-2 text-xl font-semibold">Protected View</h2>
            <p className="mb-4 text-sm text-muted-foreground">
              This is a protected page that requires authentication. You can only see this if you're logged in.
            </p>
            <p className="text-sm text-green-600 dark:text-green-400">
              ✓ Authentication is working correctly!
            </p>
          </div>

          <div className="rounded-lg border p-6">
            <h2 className="mb-2 text-xl font-semibold">Quick Actions</h2>
            <div className="space-y-2">
              <Link
                href="/"
                className="block text-sm text-primary hover:underline"
              >
                ← Back to Home
              </Link>
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}


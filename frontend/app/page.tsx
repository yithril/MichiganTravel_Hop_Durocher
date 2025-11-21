import Link from 'next/link'
import { getSession } from '@/lib/get-session'
import ParallaxHero from '@/components/ParallaxHero'

export default async function HomePage() {
  const session = await getSession()
  
  return (
    <div className="flex min-h-screen flex-col">
      {/* Navigation */}
      <nav className="fixed top-0 left-0 right-0 z-50 border-b bg-background/80 backdrop-blur-sm">
        <div className="container mx-auto flex h-16 items-center justify-between px-4">
          <Link href="/" className="text-xl font-bold font-heading">
            Hidden Gems of Michigan
          </Link>
          <div className="flex gap-4">
            {session ? (
              <>
                <span className="text-sm text-muted-foreground">
                  {session.user?.email}
                </span>
                <Link
                  href="/dashboard"
                  className="rounded bg-primary px-4 py-2 text-sm text-primary-foreground hover:bg-primary/90"
                >
                  Dashboard
                </Link>
              </>
            ) : (
              <>
                <Link
                  href="/login"
                  className="rounded bg-primary px-4 py-2 text-sm text-primary-foreground hover:bg-primary/90"
                >
                  Login
                </Link>
                <Link
                  href="/register"
                  className="rounded border border-border px-4 py-2 text-sm hover:bg-accent"
                >
                  Register
                </Link>
              </>
            )}
          </div>
        </div>
      </nav>

      {/* Parallax Hero */}
      <ParallaxHero />
    </div>
  )
}

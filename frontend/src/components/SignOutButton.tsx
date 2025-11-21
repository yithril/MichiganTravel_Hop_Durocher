'use client'

import { signOut } from 'next-auth/react'
import { useRouter } from 'next/navigation'

export function SignOutButton() {
  const router = useRouter()
  
  const handleSignOut = async () => {
    await signOut({ redirect: false })
    router.push('/')
  }
  
  return (
    <button
      onClick={handleSignOut}
      className="rounded bg-destructive px-4 py-2 text-sm text-destructive-foreground hover:bg-destructive/90 transition-colors"
      style={{
        backgroundColor: 'var(--color-destructive)',
        color: 'var(--color-destructive-foreground)',
      }}
      onMouseEnter={(e) => {
        e.currentTarget.style.opacity = '0.9'
      }}
      onMouseLeave={(e) => {
        e.currentTarget.style.opacity = '1'
      }}
    >
      Sign Out
    </button>
  )
}

export default SignOutButton


'use client'

import { signOut } from 'next-auth/react'
import { useRouter } from 'next/navigation'

export default function SignOutButton() {
  const router = useRouter()
  
  const handleSignOut = async () => {
    await signOut({ redirect: false })
    router.push('/')
  }
  
  return (
    <button
      onClick={handleSignOut}
      className="rounded bg-destructive px-4 py-2 text-sm text-destructive-foreground hover:bg-destructive/90"
    >
      Sign Out
    </button>
  )
}


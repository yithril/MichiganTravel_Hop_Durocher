'use client'

import { signOut } from 'next-auth/react'

export default function SignOutButton() {
  return (
    <button
      onClick={() => signOut({ callbackUrl: '/' })}
      className="rounded bg-destructive px-4 py-2 text-sm text-destructive-foreground hover:bg-destructive/90"
    >
      Sign Out
    </button>
  )
}


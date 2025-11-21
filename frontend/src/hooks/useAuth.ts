'use client'

import { useSession } from 'next-auth/react'
import { useRouter } from 'next/navigation'
import { useEffect } from 'react'

export function useAuth(required: boolean = false) {
  const { data: session, status } = useSession()
  const router = useRouter()

  useEffect(() => {
    if (required && status === 'unauthenticated') {
      router.push('/login')
    }
  }, [status, required, router])

  return {
    user: session?.user,
    session,
    isLoading: status === 'loading',
    isAuthenticated: status === 'authenticated',
    isUnauthenticated: status === 'unauthenticated',
  }
}

export function useRequireAuth() {
  return useAuth(true)
}


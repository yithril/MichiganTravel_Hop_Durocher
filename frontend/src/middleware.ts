import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

export async function middleware(request: NextRequest) {
  // Allow all API routes to proceed (they handle auth internally)
  if (request.nextUrl.pathname.startsWith('/api/')) {
    return NextResponse.next()
  }
  
  // Check for NextAuth session cookie
  // In NextAuth v4, the session cookie is named 'next-auth.session-token' (or 'next-auth.session-token' in production)
  const sessionToken = request.cookies.get('next-auth.session-token') || 
                      request.cookies.get('__Secure-next-auth.session-token')
  
  // Require authentication for dashboard routes
  if (request.nextUrl.pathname.startsWith('/dashboard')) {
    if (!sessionToken) {
      return NextResponse.redirect(new URL('/login', request.url))
    }
  }
  
  return NextResponse.next()
}

export const config = {
  matcher: [
    "/dashboard/:path*",
  ],
}


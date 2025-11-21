# Frontend

Next.js frontend with Tailwind CSS v4, NextAuth authentication, and theme support.

## Setup

1. **Install dependencies:**
   ```bash
   npm install
   ```

2. **Create `.env.local` file:**
   ```bash
   cp .env.local.example .env.local
   ```
   Then edit `.env.local` and set:
   - `AUTH_SECRET` - Must match backend `.env` (generate with `openssl rand -base64 32`)
   - `NEXT_PUBLIC_API_URL` - Backend API URL (default: `http://localhost:8000`)
   - `NEXTAUTH_URL` - Frontend URL (default: `http://localhost:3000`)

3. **Run the frontend:**
   ```bash
   npm run dev
   ```

The app will be available at `http://localhost:3000`

## Features

- ✅ Tailwind CSS v4 with CSS variable-based theming
- ✅ Theme provider (light/dark/system)
- ✅ NextAuth v4 authentication
- ✅ Protected routes with middleware
- ✅ Error boundaries and 404 page
- ✅ TypeScript support

## Project Structure

```
frontend/
├── app/              # Next.js App Router pages
│   ├── login/        # Login page
│   ├── register/     # Registration page
│   └── dashboard/    # Protected dashboard
├── src/
│   ├── components/   # React components
│   ├── hooks/        # Custom React hooks
│   ├── lib/          # Utilities (auth, API client)
│   └── types/        # TypeScript type definitions
└── public/           # Static assets
```

## Pages

- `/` - Home page (public)
- `/login` - Login page
- `/register` - Registration page
- `/dashboard` - Protected dashboard (requires authentication)

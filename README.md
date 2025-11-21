# Hackathon Project

FastAPI backend + Next.js frontend with authentication.

## Quick Start

### Prerequisites

- Python 3.12.x (required - Python 3.13 has compatibility issues)
- Node.js 18+
- PostgreSQL (local or Docker)
- Poetry (for Python dependency management)

### Setup

1. **Backend Setup:**
   ```bash
   cd backend
   poetry install
   cp .env.example .env
   # Edit .env with your database URL and AUTH_SECRET
   ```

2. **Frontend Setup:**
   ```bash
   cd frontend
   npm install
   cp .env.local.example .env.local
   # Edit .env.local with AUTH_SECRET (must match backend)
   ```

3. **Generate AUTH_SECRET:**
   ```bash
   openssl rand -base64 32
   ```
   Use the same value in both `backend/.env` and `frontend/.env.local`

4. **Start PostgreSQL** (locally or via Docker)

5. **Initialize Database:**
   ```bash
   cd backend
   poetry shell
   aerich init -t core.tortoise_config.TORTOISE_ORM
   aerich init-db
   aerich upgrade
   ```

6. **Start Backend:**
   ```bash
   cd backend
   poetry run dev
   ```

7. **Start Frontend:**
   ```bash
   cd frontend
   npm run dev
   ```

## Environment Variables

### Backend (`backend/.env`)
- `DATABASE_URL` - PostgreSQL connection string
- `AUTH_SECRET` - Must match frontend (generate with `openssl rand -base64 32`)
- `AUTH_URL` - Backend URL (default: `http://localhost:8000`)

### Frontend (`frontend/.env.local`)
- `AUTH_SECRET` - Must match backend exactly
- `NEXT_PUBLIC_API_URL` - Backend API URL (default: `http://localhost:8000`)
- `NEXTAUTH_URL` - Frontend URL (default: `http://localhost:3000`)

## Project Structure

```
.
├── backend/          # FastAPI backend
│   ├── core/         # Core utilities
│   ├── infrastructure/  # Database provider
│   ├── services/     # Business logic
│   ├── controllers/  # API routes
│   └── dtos/         # Data Transfer Objects
├── frontend/         # Next.js frontend
│   ├── app/          # Pages
│   └── src/          # Components, hooks, lib
└── readmes/          # Setup documentation
```

## Testing

1. **Backend Health Check:**
   ```bash
   curl http://localhost:8000/health
   ```

2. **API Documentation:**
   Open http://localhost:8000/docs

3. **Frontend:**
   Open http://localhost:3000

## Authentication Flow

1. User registers via `/register` page
2. User logs in via `/login` page
3. NextAuth creates JWT token and stores as HTTP-only cookie
4. All API requests automatically include the cookie
5. Backend validates JWT token using shared `AUTH_SECRET`

## Key Technologies

- **Backend**: FastAPI, Tortoise ORM, Aerich, Argon2, NextAuth JWT
- **Frontend**: Next.js 16, NextAuth v4, Tailwind CSS v4, TypeScript

## Documentation

See `readmes/` folder for detailed setup guides:
- `QUICKSTART.md` - Quick start guide
- `PROJECT_SCAFFOLD.md` - Setup order
- `BACKEND_SETUP.md` - Backend setup details
- `FRONTEND_SETUP.md` - Frontend setup details
- `AUTH_SETUP.md` - Authentication setup details


# Backend API

FastAPI backend with Tortoise ORM, Aerich migrations, and NextAuth authentication.

## Setup

1. **Install dependencies:**
   ```bash
   poetry install
   ```

2. **Create `.env` file:**
   ```bash
   cp .env.example .env
   ```
   Then edit `.env` and set:
   - `DATABASE_URL` - PostgreSQL connection string
   - `AUTH_SECRET` - Must match frontend `.env.local` (generate with `openssl rand -base64 32`)

3. **Start PostgreSQL database** (locally or via Docker)

4. **Initialize Aerich migrations:**
   ```bash
   poetry shell
   aerich init -t core.tortoise_config.TORTOISE_ORM
   aerich init-db
   aerich upgrade
   ```

5. **Run the backend:**
   ```bash
   poetry run dev
   ```

The API will be available at `http://localhost:8000`

## API Endpoints

- `GET /` - Root endpoint
- `GET /health` - Health check
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login user

See `http://localhost:8000/docs` for full API documentation.

## Project Structure

```
backend/
├── core/              # Core utilities (config, auth, models)
├── infrastructure/    # Database provider
├── services/          # Business logic
├── controllers/       # API route handlers
├── dtos/              # Data Transfer Objects
├── migrations/        # Aerich migration files
└── main.py           # FastAPI application entry point
```

## Architecture

- **Controllers**: Inject services, not repositories
- **Services**: Handle business logic and use models directly
- **DTOs**: Pydantic models for request/response validation
- **Models**: Tortoise ORM models representing database tables


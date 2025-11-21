"""FastAPI application entry point."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from infrastructure.database import db_provider
from controllers.auth_controller import router as auth_router
from controllers.trip_seed_controller import router as trip_seed_router
from controllers.trip_controller import router as trip_router


app = FastAPI(
    title="Hackathon API",
    description="FastAPI backend with NextAuth authentication",
    version="1.0.0",
)

# CORS middleware for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Next.js dev server
    allow_credentials=True,  # CRITICAL: Must be True for cookies to work
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(auth_router)
app.include_router(trip_seed_router)
app.include_router(trip_router)


@app.on_event("startup")
async def startup():
    """Initialize infrastructure providers on app startup."""
    await db_provider.init()
    print("Database provider initialized")


@app.on_event("shutdown")
async def shutdown():
    """Close infrastructure providers on app shutdown."""
    await db_provider.close()
    print("Database provider closed")


@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "API is running", "status": "running"}


@app.get("/health")
async def health():
    """Health check endpoint."""
    db_healthy = await db_provider.health_check()
    return {
        "status": "healthy" if db_healthy else "unhealthy",
        "database": "connected" if db_healthy else "disconnected",
    }


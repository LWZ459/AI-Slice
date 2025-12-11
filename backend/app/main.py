"""
Main FastAPI application for AI-Slice.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .core.config import settings
from .core.database import init_db

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI-enabled online restaurant order and delivery system"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup."""
    init_db()
    print(f"🚀 {settings.APP_NAME} v{settings.APP_VERSION} started!")
    print(f"📚 API documentation available at http://localhost:8000/docs")


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


# Import and include API routers
from .api import auth, orders, menu, delivery, ai, reputation, manager, wallet, chef

app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(orders.router, prefix="/api/orders", tags=["Orders"])
app.include_router(menu.router, prefix="/api/menu", tags=["Menu"])
app.include_router(chef.router, prefix="/api/chef", tags=["Chef"])
app.include_router(delivery.router, prefix="/api/delivery", tags=["Delivery"])
app.include_router(ai.router, prefix="/api/ai", tags=["AI"])
app.include_router(reputation.router, prefix="/api/reputation", tags=["Reputation"])
app.include_router(manager.router, prefix="/api/manager", tags=["Manager"])
app.include_router(wallet.router, prefix="/api", tags=["Wallet"])


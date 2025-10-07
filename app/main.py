from fastapi import FastAPI, HTTPException, Depends, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from sqlalchemy.orm import Session
from sqlalchemy import text
import os
from dotenv import load_dotenv

from app.database import init_db, get_db
from app.routers import quests, users, leaderboard, treasury, analytics, messaging, participation, bonus, wallet, auth, daily_ai_messages, payments, credits, leaderboard_realtime, global_leaderboard, ads, cron_jobs, notifications, spin_wheel
from app.core.config import settings

from create_admin import create_admin_user
# Load environment variables
load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await init_db()

    try: 
        create_admin_user()
    except: 
        print(f"Failed to auto-create admin user")
    yield
    # Shutdown
    pass

app = FastAPI(
    title="Sapien AI-Quest API",
    description="Backend API for the philosophical AI storytelling game with economy and leaderboards",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(quests.router, prefix="/api/quests", tags=["quests"])
app.include_router(users.router, prefix="/api/users", tags=["users"])
app.include_router(leaderboard.router, prefix="/api/leaderboard", tags=["leaderboard"])
app.include_router(treasury.router, prefix="/api/treasury", tags=["treasury"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["analytics"])
app.include_router(messaging.router, prefix="/api/quests", tags=["messaging"])
app.include_router(participation.router, prefix="/api/quests", tags=["participation"])
app.include_router(bonus.router, prefix="/api/daily-bonuses", tags=["daily-bonuses"])
app.include_router(wallet.router, prefix="/api/wallet", tags=["wallet"])
app.include_router(auth.router, prefix="/api/auth", tags=["authentication"])
app.include_router(daily_ai_messages.router, prefix="/api/daily-ai-messages", tags=["daily-ai-messages"])
app.include_router(payments.router, prefix="/api/payments", tags=["payments"])
app.include_router(credits.router, prefix="/api/credits", tags=["credits"])
app.include_router(leaderboard_realtime.router, prefix="/api/leaderboard", tags=["leaderboard-realtime"])
app.include_router(global_leaderboard.router, prefix="/api/global-leaderboard", tags=["global-leaderboard"])
app.include_router(ads.router, prefix="/api/ads", tags=["ads"])
app.include_router(cron_jobs.router, prefix="/api/cron", tags=["cron-jobs"])
app.include_router(notifications.router, prefix="/api/notifications", tags=["notifications"])
app.include_router(spin_wheel.router, prefix="/api/spin-wheel", tags=["spin-wheel"])

@app.get("/")
async def root():
    return {
        "message": "Sapien AI-Quest API", 
        "status": "running",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check(db: Session = Depends(get_db)):
    """Health check endpoint with database connectivity test"""
    try:
        # Test database connection
        db.execute(text("SELECT 1"))
        return {
            "status": "healthy", 
            "version": "1.0.0",
            "database": "connected",
            "ai_service": "available"
        }
    except Exception as e:
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "version": "1.0.0", 
                "database": "disconnected",
                "error": str(e)
            }
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

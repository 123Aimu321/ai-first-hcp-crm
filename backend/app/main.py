from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.agent import router as agent_router

import app.models
from app.api.hcps import router as hcps_router
from app.api.interactions import router as interactions_router
from app.config import settings
from app.database import Base, engine


Base.metadata.create_all(bind=engine)


app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    description="AI-first CRM for Healthcare Professional interactions",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(hcps_router)
app.include_router(interactions_router)
app.include_router(agent_router)

@app.get("/")
def root():
    return {
        "message": "AI-First HCP CRM API is running",
        "environment": settings.app_env,
    }


@app.get("/health")
def health_check():
    return {"status": "healthy"}
"""
Bryt Piercing Studio - Main Application
A booking and client management system for Bryt's piercing services
"""

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pathlib import Path

from routes import pages, api, admin

# Initialize FastAPI app
app = FastAPI(
    title="Bryt Piercing Studio",
    description="Booking and client management for Bryt's piercing services",
    version="1.0.0"
)

# Setup paths
BASE_DIR = Path(__file__).resolve().parent
TEMPLATES_DIR = BASE_DIR / "templates"
STATIC_DIR = BASE_DIR / "static"

# Mount static files
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# Setup templates
templates = Jinja2Templates(directory=TEMPLATES_DIR)

# Include routers
app.include_router(pages.router)
app.include_router(api.router, prefix="/api")
app.include_router(admin.router, prefix="/admin")


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    from db.database import init_db
    await init_db()


if __name__ == "__main__":
    import uvicorn
    import os
    port = int(os.environ.get("PORT", 8000))
    host = "0.0.0.0" if os.environ.get("PORT") else "127.0.0.1"
    uvicorn.run("main:app", host=host, port=port, reload=not os.environ.get("PORT"))


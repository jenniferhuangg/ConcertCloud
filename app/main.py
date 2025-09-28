# app/main.py
from __future__ import annotations
import atexit

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from apscheduler.schedulers.background import BackgroundScheduler

from .db import engine, SessionLocal
from .models import Base
from .routes_auth import router as auth_router
from .routes_events import router as events_router
from .routes_watch import router as watch_router
from .services.notify import scan_watchlists

app = FastAPI(title="ConcertCloud API")

# CORS: React dev
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5173", "http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ensure tables exist in dev (Alembic is your source of truth)
Base.metadata.create_all(bind=engine)

@app.get("/", include_in_schema=False)
def root():
    return {"ok": True}

@app.get("/healthz", include_in_schema=False)
def healthz():
    return {"status": "ok"}

# Routers
app.include_router(auth_router)
app.include_router(events_router)
app.include_router(watch_router)

# Background job: scan watchlists every 2 minutes
scheduler = BackgroundScheduler()

def _scan_job():
    db = SessionLocal()
    try:
        created = scan_watchlists(db)
        if created:
            print(f"[watch] created {created} notifications")
    finally:
        db.close()

scheduler.add_job(_scan_job, "interval", minutes=2, id="watch_scan", replace_existing=True)
scheduler.start()
atexit.register(lambda: scheduler.shutdown(wait=False))

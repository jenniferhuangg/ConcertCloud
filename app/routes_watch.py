# app/routes_watch.py
from __future__ import annotations
import os, uuid
from decimal import Decimal

from fastapi import APIRouter, Depends, Header, HTTPException, Path
from pydantic import BaseModel
from jose import jwt, JWTError
from sqlalchemy import select
from sqlalchemy.orm import Session

from .db import get_db
from .models import User, Watchlist, Notification, Listing

router = APIRouter(prefix="/watch", tags=["watchlists"])

JWT_SECRET = os.getenv("JWT_SECRET", "please-change-me")
JWT_ALG = "HS256"

def get_current_user(Authorization: str = Header(...), db: Session = Depends(get_db)) -> User:
    if not Authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing bearer token")
    token = Authorization.split()[1]
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALG])
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    uid = payload.get("sub")
    if not uid:
        raise HTTPException(status_code=401, detail="Invalid token")
    user = db.get(User, uuid.UUID(uid))
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user

class WatchIn(BaseModel):
    event_id: int
    max_price: float | None = None

@router.post("/watchlists")
def add_watch(w: WatchIn, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    wl = Watchlist(
        user_id=user.id,
        event_id=w.event_id,
        max_price=Decimal(str(w.max_price)) if w.max_price is not None else None,
    )
    db.add(wl)
    db.commit()
    db.refresh(wl)
    return {"id": wl.id, "event_id": wl.event_id, "max_price": float(wl.max_price) if wl.max_price is not None else None}

@router.get("/watchlists")
def my_watchlists(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    items = db.scalars(select(Watchlist).where(Watchlist.user_id == user.id)).all()
    return [{"id": x.id, "event_id": x.event_id, "max_price": float(x.max_price) if x.max_price is not None else None} for x in items]

@router.delete("/watchlists/{watch_id}")
def delete_watch(
    watch_id: int = Path(..., ge=1),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    wl = db.get(Watchlist, watch_id)
    if not wl or wl.user_id != user.id:
        raise HTTPException(status_code=404, detail="Not found")
    db.delete(wl)
    db.commit()
    return {"ok": True}

@router.post("/scan")
def scan_watchlists_endpoint(db: Session = Depends(get_db)):
    """Dev-only manual trigger; background job will also run automatically."""
    from .services.notify import scan_watchlists
    created = scan_watchlists(db)
    return {"created": created}

@router.get("/notifications")
def my_notifications(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    notes = db.scalars(select(Notification).where(Notification.user_id == user.id)).all()
    return [{"id": n.id, "listing_id": n.listing_id, "created_at": n.created_at.isoformat()} for n in notes]

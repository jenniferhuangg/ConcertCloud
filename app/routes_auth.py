from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import select, asc
from .db import get_db
from .models import Event, Venue, Section, Listing
import math

router = APIRouter(prefix="/events", tags=["events"])

def _dist(ax, ay, bx, by): return math.hypot(ax-bx, ay-by)

def rank_best(listings, sections_by_id, venue, w_loc=0.7, w_price=0.3):
    if not listings: return []
    prices = [float(x.price) for x in listings]
    pmin, pmax = min(prices), max(prices) or 1.0
    def score(x):
        sec = sections_by_id.get(x.section_id)
        if sec:
            loc = _dist(sec.cx, sec.cy, venue.stage_x, venue.stage_y) / max(venue.width, venue.height)
        else:
            loc = (x.seat_score or 100)/100.0
        price = (float(x.price)-pmin)/max(pmax-pmin, 1e-6)
        return w_loc*loc + w_price*price
    return sorted(listings, key=score)

@router.get("/{event_id}")
def get_event(event_id: int, db: Session = Depends(get_db)):
    ev = db.get(Event, event_id)
    if not ev: raise HTTPException(404, "Event not found")
    return {"id": ev.id, "artist_id": ev.artist_id, "venue": ev.venue, "when": ev.when, "status": ev.status}

@router.get("/{event_id}/listings")
def get_listings(
    event_id: int,
    sort: str = "cheapest",
    qty: int = Query(1, ge=1, le=8),
    max_price: float | None = None,
    verified_only: bool = False,
    db: Session = Depends(get_db),
):
    stmt = select(Listing).where(Listing.event_id == event_id)
    if verified_only: stmt = stmt.where(Listing.is_verified == True)
    if max_price is not None: stmt = stmt.where(Listing.price <= max_price)
    items = db.scalars(stmt).all()

    if sort == "cheapest":
        items.sort(key=lambda x: float(x.price))
    elif sort == "best":
        ev = db.get(Event, event_id); 
        if not ev: raise HTTPException(404, "Event not found")
        venue = db.scalar(select(Venue).where(Venue.name == ev.venue))
        sections = db.scalars(select(Section).where(Section.venue_id == (venue.id if venue else -1))).all()
        items = rank_best(items, {s.id: s for s in sections}, venue or Venue(width=1000, height=700, stage_x=500, stage_y=80))
    return [
        {"id": x.id, "section": x.section, "row": x.row, "seat": x.seat,
         "price": float(x.price), "seat_score": x.seat_score, "verified": x.is_verified,
         "section_id": x.section_id}
        for x in items
    ]

@router.get("/{event_id}/map")
def get_map(event_id: int, db: Session = Depends(get_db)):
    ev = db.get(Event, event_id)
    if not ev: raise HTTPException(404, "Event not found")
    venue = db.scalar(select(Venue).where(Venue.name == ev.venue))
    if not venue: raise HTTPException(404, "Venue map not found")
    sections = db.scalars(select(Section).where(Section.venue_id == venue.id)).all()
    listings = db.scalars(select(Listing).where(Listing.event_id == event_id)).all()
    cheapest = sorted(listings, key=lambda x: float(x.price))[:1]
    best = rank_best(listings, {s.id: s for s in sections}, venue)[:1]
    return {
        "venue": {"id": venue.id, "name": venue.name, "w": venue.width, "h": venue.height,
                  "stage_x": venue.stage_x, "stage_y": venue.stage_y},
        "sections": [{"id": s.id, "name": s.name, "cx": s.cx, "cy": s.cy} for s in sections],
        "cheapest": [{"id": x.id, "price": float(x.price), "section_id": x.section_id} for x in cheapest],
        "best": [{"id": x.id, "price": float(x.price), "section_id": x.section_id} for x in best],
    }

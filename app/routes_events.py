# app/routes_events.py
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session
from math import sqrt
from statistics import median

from .db import get_db
from .models import Event, Venue, Section, Listing

router = APIRouter(prefix="/events", tags=["events"])

# ---------- helpers ----------
def _norm(x: float, lo: float, hi: float) -> float:
    if hi == lo:
        return 0.0
    v = (x - lo) / (hi - lo)
    return min(1.0, max(0.0, v))

def _row_depth(row: str | None) -> int:
    if not row:
        return 10
    if row.isdigit():
        return int(row)
    alpha = "".join(ch for ch in row.upper() if ch.isalpha())
    if not alpha:
        return 10
    depth = 0
    for ch in alpha:
        depth = depth * 26 + (ord(ch) - 64)  # A=1
    return depth

def _score_listing(lst: Listing, sec_by_id: dict[int, Section], venue_xy: dict, p_lo: float, p_hi: float) -> float:
    """
    Lower is better. Blend:
      distance (0.6) + row depth (0.15) + price (0.25)
    """
    price = float(lst.price)
    price_n = _norm(price, p_lo, p_hi)

    if lst.section_id and lst.section_id in sec_by_id:
        s = sec_by_id[lst.section_id]
        dx = s.cx - venue_xy["stage_x"]
        dy = s.cy - venue_xy["stage_y"]
        dist = sqrt(dx * dx + dy * dy)
        dist_n = _norm(dist, 0, 1000)  # canvas is ~0..1000
    else:
        # fallback if not mapped to a section
        dist_n = _norm(lst.seat_score, 0, 100)

    row_n = _norm(_row_depth(lst.row), 1, 30)

    return 0.6 * dist_n + 0.15 * row_n + 0.25 * price_n

# ---------- endpoints ----------
@router.get("/{event_id}/listings")
def get_listings(
    event_id: int,
    sort: str = "cheapest",
    qty: int = Query(1, ge=1, le=8),
    together: bool = False,
    max_price: float | None = None,
    verified_only: bool = False,
    section_id: int | None = None,
    db: Session = Depends(get_db),
):
    # base query
    stmt = select(Listing).where(Listing.event_id == event_id)
    if verified_only:
        stmt = stmt.where(Listing.is_verified == True)
    if max_price is not None:
        stmt = stmt.where(Listing.price <= max_price)
    if section_id is not None:
        stmt = stmt.where(Listing.section_id == section_id)

    items = db.scalars(stmt).all()

    # together filter (find runs of consecutive seat_num)
    if together and qty > 1:
        grouped = {}
        for x in items:
            key = (x.section_id or 0, x.section or "", x.row or "")
            grouped.setdefault(key, []).append(x)
        kept = []
        for _, arr in grouped.items():
            arr.sort(key=lambda a: (a.seat_num or 10**9, a.id))
            run = []
            last = None
            for a in arr:
                if a.seat_num is None:
                    continue
                if last is None or a.seat_num == last + 1:
                    run.append(a)
                else:
                    if len(run) >= qty:
                        kept.extend(run)  # keep the whole run
                    run = [a]
                last = a.seat_num
            if len(run) >= qty:
                kept.extend(run)
        items = kept

    # sorting
    if sort == "cheapest":
        items.sort(key=lambda x: float(x.price))
    else:
        ev = db.get(Event, event_id)
        if not ev:
            raise HTTPException(status_code=404, detail="Event not found")

        vrow = db.execute(select(Venue).where(Venue.name == ev.venue)).scalar_one_or_none()
        if vrow:
            venue_xy = {"stage_x": vrow.stage_x, "stage_y": vrow.stage_y}
            secs = db.scalars(select(Section).where(Section.venue_id == vrow.id)).all()
            sec_by_id = {s.id: s for s in secs}
        else:
            venue_xy = {"stage_x": 500.0, "stage_y": 80.0}
            sec_by_id = {}

        prices = [float(x.price) for x in items] or [0.0]
        p_lo = min(prices)
        p_hi = max(median(prices), p_lo + 1e-6)
        items.sort(key=lambda x: _score_listing(x, sec_by_id, venue_xy, p_lo, p_hi))

    # serialize
    return [
        {
            "id": it.id,
            "event_id": it.event_id,
            "section": it.section,
            "section_id": it.section_id,
            "row": it.row,
            "seat": it.seat,
            "seat_num": it.seat_num,
            "price": float(it.price),
            "is_verified": it.is_verified,
        }
        for it in items
    ]

@router.get("/{event_id}/map")
def get_map(event_id: int, db: Session = Depends(get_db)):
    ev = db.get(Event, event_id)
    if not ev:
        raise HTTPException(status_code=404, detail="Event not found")

    v = db.execute(select(Venue).where(Venue.name == ev.venue)).scalar_one_or_none()
    if not v:
        return {"venue": {"name": ev.venue, "width": 1000, "height": 700, "stage_x": 500, "stage_y": 80},
                "sections": [], "cheapest": None, "best": None}

    secs = db.scalars(select(Section).where(Section.venue_id == v.id)).all()
    # markers
    listings = db.scalars(select(Listing).where(Listing.event_id == event_id)).all()
    cheapest = min(listings, key=lambda x: float(x.price)) if listings else None

    prices = [float(x.price) for x in listings] or [0.0]
    p_lo, p_hi = (min(prices), max(median(prices), min(prices) + 1e-6))
    sec_by_id = {s.id: s for s in secs}
    best = min(listings, key=lambda x: _score_listing(x, sec_by_id, {"stage_x": v.stage_x, "stage_y": v.stage_y}, p_lo, p_hi)) if listings else None

    return {
        "venue": {"name": v.name, "width": v.width, "height": v.height, "stage_x": v.stage_x, "stage_y": v.stage_y},
        "sections": [{"id": s.id, "name": s.name, "cx": s.cx, "cy": s.cy, "base_closeness": s.base_closeness} for s in secs],
        "cheapest": cheapest and {"listing_id": cheapest.id, "price": float(cheapest.price), "section_id": cheapest.section_id},
        "best": best and {"listing_id": best.id, "price": float(best.price), "section_id": best.section_id},
    }

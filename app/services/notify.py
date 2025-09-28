# app/services/notify.py
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models import Watchlist, Notification, Listing  # <-- absolute import

def scan_watchlists(db: Session) -> int:
    """
    For each watchlist: find matching listings (<= max_price if set) and
    create Notification rows if not already created. Returns # created.
    """
    created = 0
    watches = db.scalars(select(Watchlist)).all()
    for w in watches:
        stmt = select(Listing).where(Listing.event_id == w.event_id)
        if w.max_price is not None:
            stmt = stmt.where(Listing.price <= w.max_price)
        for m in db.scalars(stmt):
            exists = db.scalar(
                select(Notification).where(
                    Notification.user_id == w.user_id,
                    Notification.listing_id == m.id,
                )
            )
            if not exists:
                db.add(Notification(user_id=w.user_id, listing_id=m.id))
                created += 1
    db.commit()
    return created

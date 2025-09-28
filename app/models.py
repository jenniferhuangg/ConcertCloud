# app/models.py
from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import (
    String, Boolean, Integer, Float, DateTime, Numeric,
    ForeignKey, UniqueConstraint
)
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


# ---- User -------------------------------------------------------
class User(Base):
    __tablename__ = "users"
    id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String(320), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String, nullable=False)
    full_name: Mapped[str | None] = mapped_column(String)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)


# ---- Venue / Section (for map) ---------------------------------
class Venue(Base):
    __tablename__ = "venues"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String, unique=True, nullable=False, index=True)
    width: Mapped[int] = mapped_column(Integer, default=1000)
    height: Mapped[int] = mapped_column(Integer, default=700)
    stage_x: Mapped[float] = mapped_column(Float, default=500.0)
    stage_y: Mapped[float] = mapped_column(Float, default=80.0)

    sections: Mapped[list["Section"]] = relationship(
        back_populates="venue", cascade="all, delete-orphan"
    )

class Section(Base):
    __tablename__ = "sections"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    venue_id: Mapped[int] = mapped_column(ForeignKey("venues.id"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    cx: Mapped[float] = mapped_column(Float, nullable=False)
    cy: Mapped[float] = mapped_column(Float, nullable=False)
    base_closeness: Mapped[int] = mapped_column(Integer, default=50)

    venue: Mapped["Venue"] = relationship(back_populates="sections")


# ---- Artist / Event / Listing ----------------------------------
class Artist(Base):
    __tablename__ = "artists"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String, unique=True, nullable=False, index=True)
    image_url: Mapped[str | None] = mapped_column(String)

class Event(Base):
    __tablename__ = "events"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    artist_id: Mapped[int] = mapped_column(ForeignKey("artists.id"), nullable=False, index=True)
    venue: Mapped[str] = mapped_column(String, nullable=False)
    when: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    status: Mapped[str] = mapped_column(String, default="onsale")

class Listing(Base):
    __tablename__ = "listings"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    event_id: Mapped[int] = mapped_column(ForeignKey("events.id"), nullable=False, index=True)
    section: Mapped[str] = mapped_column(String)                   # free-text label like "101"
    section_id: Mapped[int | None] = mapped_column(ForeignKey("sections.id"), index=True)
    row: Mapped[str | None] = mapped_column(String)
    seat: Mapped[str | None] = mapped_column(String)
    seat_num: Mapped[int | None] = mapped_column(Integer)          # parsed integer seat number
    price: Mapped[Numeric] = mapped_column(Numeric(10, 2), nullable=False)
    seat_score: Mapped[int] = mapped_column(Integer, default=100)  # lower = better (fallback)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=True)


# ---- Watchlists / Notifications --------------------------------
class Watchlist(Base):
    __tablename__ = "watchlists"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False, index=True)
    event_id: Mapped[int] = mapped_column(ForeignKey("events.id"), nullable=False, index=True)
    max_price: Mapped[Numeric | None] = mapped_column(Numeric(10, 2))

class Notification(Base):
    __tablename__ = "notifications"
    __table_args__ = (UniqueConstraint("user_id", "listing_id", name="uq_notifications_user_listing"),)
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False, index=True)
    listing_id: Mapped[int] = mapped_column(ForeignKey("listings.id"), nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

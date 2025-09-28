# ConcertCloud 

Everyone deserves to see their favourite artist.

> **Status:** 🚧 Pre-alpha / incomplete  
> **Prototype / Demo:** **Not available** yet  

---

## Overview

ConcertCloud aims to help fans pick better seats—balancing **price**, **view**, and **experience**—and plan the show with friends. The vision is a single place to search events, compare seating trade-offs, track price changes, and coordinate plans.

This repository is an **early work-in-progress**. It’s here to capture initial scaffolding, notes, and milestones. **There is no working build or prototype at this time.**

### Goals

- Price vs. experience comparison, with clear trade-off explanations  
- Seat notifications  
- Collaborative planning calendar
- Artist and venue context (bios, setlists signals, venue tips)

---

## Current State

- ✅ Repo structure + initial docs
- 🚧 Early UI wireframes / component stubs (not functional)
- 🚧 Placeholder API routes (no real data)
- 🚧 Draft DB schema notes (not migrated)
- ❌ No integrations with ticketing providers
- ❌ No authentication / authorization
- ❌ No deployment target

> If you try to run it now, scripts will likely fail

---

## Tech Stack (planned)

- **Frontend:** React + TypeScript (component library TBD)
- **Backend:** Python + FastAPI
- **Database:** PostgreSQL (via SQLAlchemy / Alembic)
- **Infra:** Docker + Docker Compose (local), CI via GitHub Actions (later)
- **Integrations (planned):** Ticketing/event APIs (TBD), artist/venue info source (TBD)

---

## Getting Started (will not fully work yet)

> ⚠️ This project is **not set up** end-to-end. Commands below are placeholders for the eventual setup.

```bash
# Clone
git clone https://github.com/<your-username>/concertcloud.git
cd concertcloud

# Frontend (planned)
# cd web && npm install && npm run dev

# Backend (planned)
# cd api
# python -m venv .venv && source .venv/bin/activate
# pip install -r requirements.txt
# uvicorn app.main:app --reload

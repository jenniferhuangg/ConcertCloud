import re

def parse_seat_num(s: str | None) -> int | None:
    if not s:
        return None
    digits = re.sub(r"\D", "", s)
    return int(digits) if digits else None

# when constructing Listing(...)
lst = Listing(
    event_id=event_id,
    section=r.get("section"),
    row=r.get("row"),
    seat=r.get("seat"),
    seat_num=parse_seat_num(r.get("seat")),  # <--- set seat_num here
    price=Decimal(r["price"]),
    is_verified=(r.get("verified","true").lower() in ("1","true","yes")),
    source_url=r.get("source_url"),
)

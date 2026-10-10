"""Help desk ticket triage: category, priority, tier routing, and SLA breach tracking.

Anything the rules cannot place goes to a human queue instead of being guessed at.
"""
import re
from datetime import datetime, timedelta

CATEGORIES = [
    ("outage", re.compile(r"\b(server down|outage|everyone|all users|can'?t access (the )?(network|internet)|ransomware|breach)\b", re.I)),
    ("access", re.compile(r"\b(password|locked out|account locked|mfa|can'?t sign in|permissions?|access to)\b", re.I)),
    ("email", re.compile(r"\b(outlook|email|mailbox|calendar|teams|sharepoint|onedrive)\b", re.I)),
    ("hardware", re.compile(r"\b(laptop|monitor|printer|keyboard|docking|screen|won'?t (turn|power) on)\b", re.I)),
    ("network", re.compile(r"\b(wifi|wi-fi|vpn|slow internet|dns|ethernet)\b", re.I)),
]

# category -> (priority, tier, SLA hours to first response)
POLICY = {
    "outage": ("P1", 2, 1),
    "access": ("P2", 1, 4),
    "email": ("P3", 1, 8),
    "network": ("P3", 2, 8),
    "hardware": ("P3", 1, 24),
}


def categorize(text: str) -> str | None:
    for name, pattern in CATEGORIES:
        if pattern.search(text):
            return name
    return None


def triage(ticket: dict) -> dict:
    """ticket: {id, text, opened (datetime)}. Returns the ticket plus category, priority, tier and due time."""
    cat = categorize(ticket["text"])
    if cat is None:
        return {**ticket, "category": "unclassified", "priority": "P3", "tier": 2, "due": None, "needs_review": True}
    priority, tier, hours = POLICY[cat]
    return {**ticket, "category": cat, "priority": priority, "tier": tier,
            "due": ticket["opened"] + timedelta(hours=hours), "needs_review": False}


def sla_breaches(triaged: list[dict], now: datetime, responded: set[str] = frozenset()) -> list[str]:
    """Ids of tickets past their first-response due time with no response yet."""
    return [t["id"] for t in triaged if t["due"] and t["id"] not in responded and now > t["due"]]


def report(triaged: list[dict], now: datetime, responded: set[str] = frozenset()) -> dict:
    by_cat: dict[str, int] = {}
    for t in triaged:
        by_cat[t["category"]] = by_cat.get(t["category"], 0) + 1
    return {
        "total": len(triaged),
        "by_category": by_cat,
        "breached": sla_breaches(triaged, now, responded),
        "needs_review": [t["id"] for t in triaged if t["needs_review"]],
    }

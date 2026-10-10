# helpdesk-ticket-triage

Sorts help desk tickets by category and priority, routes them to a support tier, and tracks first-response SLA breaches.

- **Categories:** outage, access, email, network, hardware. A company-wide outage outranks any other keyword in the same ticket.
- **Policy table:** each category sets a priority, a tier, and an SLA in hours (for example outage is P1, tier 2, one hour).
- **Unclassified tickets** go to a human review list instead of being guessed at.
- **SLA tracking:** lists tickets past their first-response due time, ignoring ones already answered, and `report()` summarizes counts by category, breaches, and tickets needing review.

## Limits

Keyword rules and a handful of tests on synthetic tickets. A real desk would load categories and SLAs from its ticketing system (ConnectWise, Jira Service Management, and similar). No third-party packages, Python 3.10 or newer.

## Run

```bash
python3 -m unittest
```

Files: `triage.py`, `test_triage.py`

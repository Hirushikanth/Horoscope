Golden snapshots: deterministic payloads for the v2 computation
endpoints.

- ``jathakam_snapshot.json`` — the flagship ``POST /api/v2/jathakam``
  payload. Regenerated intentionally only when the computation
  semantics change. Birth data matches golden sample #2 of the Swiss
  Ephemeris suite: 1990-06-15 06:30:00 Asia/Colombo, 6.9271°N 79.8612°E.
- ``stars_snapshot.json`` — the ``POST /api/v2/stars`` yogatara
  catalogue payload (proper-motion corrected positions) for the same
  birth data. Regenerated only when the Hipparcos catalogue values or
  the payload shape change.

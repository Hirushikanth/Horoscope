# Jyotisha Backend v2.0 — Deployment

Production deployment guide for the FastAPI v2 backend. Everything in
this document is run from the `backend/` directory.

## Prerequisites

- **Python 3.12+** (pyproject requires `>=3.12`; `zip()` with
  `strict=True`, `StrEnum` and `list[str]` syntax need 3.12).
- **The JPL DE440 ephemeris file** (`de440.bsp`, ~114 MB) must be
  present in `backend/data/` before the first request. It is
  git-ignored; download it once:

  ```bash
  mkdir -p data
  # NASA/JPL (Park et al. 2021):
  curl -L -o data/de440.bsp \
    https://naif.jpl.nasa.gov/pub/naif/generic_kernels/spk/planets/de440.bsp
  ```

  Alternatively point `JYOTISHA_DATA_DIR` at a shared location and, for
  first boot on a machine with network access, set
  `JYOTISHA_AUTO_DOWNLOAD_EPHEMERIS=true`.

## Install

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"        # app + dev tools (pytest, ruff, mypy)
cp .env.example .env           # then adjust for the environment
```

## Configuration

All settings are environment variables with the `JYOTISHA_` prefix
(see `.env.example`). Production-relevant ones:

| Variable | Default | Notes |
|---|---|---|
| `JYOTISHA_ENVIRONMENT` | `development` | `production` disables `--reload` |
| `JYOTISHA_CORS_ORIGINS` | localhost:5173 | Comma-separated frontend origins |
| `JYOTISHA_DATA_DIR` | `data` | Directory holding `de440.bsp` |
| `JYOTISHA_AUTO_DOWNLOAD_EPHEMERIS` | `false` | First-boot download fallback |
| `JYOTISHA_CACHE_TTL_SECONDS` | `300` | TTL of the in-process result cache |
| `JYOTISHA_CACHE_MAX_ENTRIES` | `1024` | Bound on the result cache |
| `JYOTISHA_NODE_CONVENTION` | `mean` | `mean` (classical) or `true` |

The cache is per-process and in-memory. For multi-worker deployments
each worker keeps its own cache; this is safe (results are pure
functions of the request), it only reduces the hit rate.

## Run

Development (auto-reload):

```bash
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

Production (one process, N workers; the endpoint functions are `def`,
so CPU-bound ephemeris work runs on the threadpool — no async leak):

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

Behind a TLS-terminating proxy (nginx/Caddy), set `PROXY_HEADERS` mode
for correct client IPs:

```bash
uvicorn app.main:app --proxy-headers --forwarded-allow-ips "*"
```

### systemd unit (example)

```ini
[Unit]
Description=Jyotisha v2 API
After=network.target

[Service]
WorkingDirectory=/srv/jyotisha/backend
EnvironmentFile=/srv/jyotisha/backend/.env
ExecStart=/srv/jyotisha/backend/.venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000 --workers 4 --proxy-headers
Restart=on-failure
User=jyotisha

[Install]
WantedBy=multi-user.target
```

## Health & metadata

- `GET /api/v2/health` — liveness; reports whether the ephemeris file
  is present and loaded.
- `GET /api/v2/meta` — version, ephemeris, ayanamsa system/value,
  precision statement (the "Thirukanitha badge").
- `GET /docs` — interactive OpenAPI documentation.

## Quality gates (run locally before release)

```bash
pytest tests/                    # full suite (unit + golden + integration)
ruff check app tests benchmarks  # lint
ruff format --check app tests    # formatting
mypy app                         # static typing
python benchmarks/bench_jathakam.py   # perf: compute p95 must be < 1 s
```

## Golden snapshots

`tests/golden/data/` holds deterministic payload snapshots for the
jathakam and stars endpoints. They fail on any unintended drift and
must only be regenerated when the computation semantics deliberately
change.

## Troubleshooting

| Symptom | Cause / fix |
|---|---|
| `503 ephemeris_unavailable` | `de440.bsp` missing from `JYOTISHA_DATA_DIR` |
| `422 date_out_of_range` | Birth date outside DE440 coverage (1550–2650) |
| `422 validation_error` | Malformed request; `detail.context.fields` lists each offending field |
| Slow first request | One-off DE440 load + Skyfield setup (~1 s), then all requests hit the cache |

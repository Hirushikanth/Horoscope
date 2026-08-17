# Jyotisha — Precision Vedic Astrology Engine & Dashboard

Jyotisha is a high-precision Vedic (Thirukanitham / South Indian) astrology platform. The **FastAPI v2 backend** computes the complete **திருக்கணித ஜாதகம்** (Thirukanitha Jathakam) and **Kalyana Porutham** marriage matching from the **NASA JPL DE440 ephemeris** via Skyfield — sub-arcsecond accuracy, IEEE 754 float64 everywhere, Lahiri (Chitrapaksha) ayanamsa. The **React frontend** is a glassmorphic, starfield-backed dashboard rendering the South Indian 4×4 charts (D1 Rasi + D9 Navamsa), the Vimshottari dasha timeline and the 11-check porutham grid.

## 🌟 Key Features

- **Scientific Precision**: IEEE 754 float64 throughout; planet longitudes verified < 1 arc-second against Swiss Ephemeris and JPL Horizons.
- **NASA JPL DE440**: Latest planetary ephemeris, coverage 1550–2650 AD.
- **Thirukanitha Jathakam** (`POST /api/v2/jathakam`):
  - Panchangam (5 angas), sidereal Lagna, all 9 grahas with D1+D9 placements
  - Whole-sign bhavas, Vimshottari Dasha balance + MD/AD/PD timeline
  - Chevvai (Mars) Dosham, dignity, vargottama — all quadrilingual (English/Sanskrit/Tamil/Sinhala)
- **Kalyana Porutham** (`POST /api/v2/matching`): all 11 checks (Dina … Nadi), 10-point scoring, verdict bands, Rajju/Vedha gates, Chevvai cross-check — strictly per docs/02.
- **Yogatara stars** (`POST /api/v2/stars`): the 27 nakshatra junction stars + major navigation stars, proper-motion corrected from the Hipparcos catalogue.
- **Trust feature**: every response self-documents the ayanamsa value, ephemeris, node convention and precision — the "Thirukanitha badge".
- **Production hardening**: TTL caching, request-ID correlation logging, typed domain errors, concurrency-tested, p95 < 1 s benchmarked.

### Frontend features (`frontend/`)

- **Two modes** — Individual Chart and Kundali Matching, switched via a pill toggle.
- **Jathakam dashboard** (4 tabs): Bento overview (Lagna hero, panchangam, mahadasha balance, almanac), visual charts (D1 Rasi + D9 Navamsa side-by-side on the South Indian 4×4 grid), 12 bhavas as 3D flip cards, and the expandable 120-year Vimshottari dasha timeline.
- **Kundali matching dashboard**: animated score ring, dosha alerts (Rajju/Vedha gates, non-negotiables, Chevvai cross-check) and the 11-check porutham grid.
- **Custom pickers**: floating-label inputs, popup calendar and AM/PM clock for birth data.
- **Design system**: glassmorphic cards with gold accents, animated canvas starfield background, Motion (Framer Motion) transitions throughout.

> **Status note**: the dasha, vargas and stars client API functions exist (`src/utils/api.ts`) but are not yet wired into the UI — the dashboard currently calls `/jathakam` and `/jathakam/panchangam` (individual) and `/matching` (matching).

## 🛠️ Tech Stack

### Backend (`backend/`)
- **Language**: Python 3.12+
- **Framework**: [FastAPI](https://fastapi.tiangolo.com/) + Pydantic v2, packaged with `pyproject.toml`
- **Astronomy**: [Skyfield](https://rhodesmill.org/skyfield/) with NASA JPL DE440
- **Quality**: pytest (unit + golden + integration), ruff, mypy

### Frontend (`frontend/`)
- **Framework**: React 19 (TypeScript + Vite 7)
- **Styling**: Tailwind CSS 4, Motion v12 (Framer Motion) for animations, glassmorphism with gold-on-space theme
- **State Management**: Zustand; Data Fetching: TanStack Query, Axios

## 📂 Project Structure

```text
├── backend/              # Python FastAPI package (v2)
│   ├── app/              # config, core, astronomy, vedic, matching, services, api
│   ├── data/             # de440.bsp (git-ignored, ~114 MB)
│   ├── tests/            # unit / golden / integration suites
│   ├── benchmarks/       # latency benchmark (p95 < 1 s gate)
│   ├── pyproject.toml    # packaging + ruff/mypy/pytest config
│   └── DEPLOY.md         # production deployment guide
├── docs/                 # domain reference documents + v2 plan/timeline
└── frontend/             # React + Vite frontend
    └── src/
        ├── components/
        │   ├── canvas/       # StarfieldBg, SouthIndianChart, KundliChart, NavamsaChart
        │   ├── horoscope/    # BirthForm, Dashboard, DashaTimeline, MatchingForm, PoruthamsGrid …
        │   └── ui/           # GlassCard, GlowButton, Calendar, Clock, ModeToggle, ScoreRing …
        ├── store/            # Zustand store (mode, birth data, results)
        ├── types/            # TS interfaces mirroring the v2 OpenAPI schemas
        └── utils/            # Axios client (api.ts), chart helpers
```

## 🚀 Getting Started

### Prerequisites

- **Backend**: Python 3.12+ and `pip`
- **Frontend**: Node.js 18+ and `npm`

Install them for your platform:

| Platform | Python 3.12+ | Node.js 18+ |
|---|---|---|
| **macOS** | `brew install python@3.12` | `brew install node` |
| **Windows** | [python.org](https://www.python.org/downloads/) installer (tick *Add to PATH*) or `winget install Python.Python.3.12` | [nodejs.org](https://nodejs.org) LTS installer or `winget install OpenJS.NodeJS.LTS` |
| **Linux** (Ubuntu/Debian) | `sudo apt install python3.12 python3.12-venv` | `sudo apt install nodejs npm` (or via [nvm](https://github.com/nvm-sh/nvm) for a newer Node) |

### Backend setup — macOS / Linux

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"

# JPL DE440 ephemeris (~114 MB, git-ignored) — required once:
mkdir -p data
curl -L -o data/de440.bsp \
  https://naif.jpl.nasa.gov/pub/naif/generic_kernels/spk/planets/de440.bsp

# Run the API
python3 -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

### Backend setup — Windows

**PowerShell:**

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e ".[dev]"

# JPL DE440 ephemeris (~114 MB, git-ignored) — required once:
New-Item -ItemType Directory -Force data
Invoke-WebRequest -Uri "https://naif.jpl.nasa.gov/pub/naif/generic_kernels/spk/planets/de440.bsp" -OutFile data\de440.bsp

# Run the API
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

> If `Activate.ps1` is blocked, run `Set-ExecutionPolicy -Scope Process Bypass` first, or use the Command Prompt variant below.

**Command Prompt (cmd):**

```bat
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -e ".[dev]"

mkdir data
curl -L -o data\de440.bsp https://naif.jpl.nasa.gov/pub/naif/generic_kernels/spk/planets/de440.bsp

python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

> **No-`curl` alternative (any OS):** skip the download and let the API fetch DE440 itself on first boot:
> macOS/Linux: `export JYOTISHA_AUTO_DOWNLOAD_EPHEMERIS=true` · PowerShell: `$env:JYOTISHA_AUTO_DOWNLOAD_EPHEMERIS = "true"` · cmd: `set JYOTISHA_AUTO_DOWNLOAD_EPHEMERIS=true`

The API is then at `http://127.0.0.1:8000` (docs at `/docs`).

### Frontend setup (same on all platforms)

```bash
cd frontend
npm install
npm run dev    # http://localhost:5173
```

## 📡 API Endpoints (v2)

All under `/api/v2`. Every computation endpoint accepts:

```json
{
  "date": "1990-06-15",
  "time": "06:30:00",
  "timezone": "Asia/Colombo",
  "latitude": 6.9271,
  "longitude": 79.8612
}
```

| Endpoint | Purpose |
|---|---|
| `POST /api/v2/jathakam` | Complete Thirukanitha Jathakam (panchangam, lagna, 9 grahas, D1+D9, bhavas, dasha, chevvai dosham) |
| `POST /api/v2/jathakam/panchangam` | Birth panchangam + daily almanac (sunrise/sunset, Rahu Kalam, Yamagandam, Gulika, Abhijit) |
| `POST /api/v2/jathakam/dasha` | Vimshottari MD/AD/PD timeline with balance at birth |
| `POST /api/v2/jathakam/vargas` | Per-graha placements in requested divisional charts (D1–D60) |
| `POST /api/v2/matching` | Kalyana Porutham — 11 checks, scoring, verdict, chevvai cross-check |
| `POST /api/v2/stars` | Yogatara catalogue positions, proper-motion corrected |
| `GET /api/v2/meta` | Ephemeris, ayanamsa value, version, precision statement |
| `GET /api/v2/health` | Liveness/readiness probe |

Errors are typed: `{"detail": {"code": ..., "message": ..., "context": ...}}` with codes such as `validation_error`, `invalid_birth_data`, `date_out_of_range`, `ephemeris_unavailable`.

## 🧪 Testing & Quality

```bash
cd backend
pytest tests/                          # full suite (unit + golden + integration)
ruff check app tests benchmarks        # lint
mypy app                               # static typing
python benchmarks/bench_jathakam.py    # perf gate: compute p95 < 1 s
```

## 📚 Documentation

- `docs/backend-v2-plan.md` — the v2 architecture and API plan
- `docs/backend-v2-timeline.md` — implementation timeline (Phases A–H, milestones)
- `docs/01-thirukanitha-jathakam-calculation.md` — the jathakam domain rules
- `docs/02-kalyana-porutham-matching.md` — the matching domain rules
- `docs/south-indian-horoscope.md` — chart conventions
- `backend/DEPLOY.md` — production deployment guide

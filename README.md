# Jyotisha — Precision Vedic Astrology Engine & Dashboard

Jyotisha is a high-precision Vedic astrology platform. It features a robust **FastAPI backend** that leverages the **NASA JPL DE440 ephemeris** via the Skyfield library for sub-arcsecond accuracy, and a **React-based dashboard** for intuitive visualization of planetary positions, charts, and dashas.

## 🌟 Key Features

- **Scientific Precision**: Uses IEEE 754 float64 precision throughout all calculations.
- **NASA JPL DE440**: Backed by the latest planetary ephemeris (covering 1550 to 2650 AD).
- **Vedic Algorithms**: Full implementation of traditional Jyotisha systems:
  - **Nakshatras**: 27 lunar mansions with detailed attributes.
  - **Rashis**: 12 zodiac signs with lordships and elements.
  - **Bhavas**: Equal house system calculations.
  - **Vimshottari Dasha**: 120-year planetary period cycle calculations.
  - **Panchang**: Tithi, Vara, Nakshatra, Yoga, and Karana.
  - **Dignities**: Planetary strengths (Exaltation, Debilitation, Moolatrikona).
  - **Yogas**: Detection of important planetary combinations.
- **Sidereal Calculations**: Lahiri (Chitra Paksha) Ayanamsa by default.
- **Interactive UI**: Glassmorphic dashboard with dynamic Kundli charts and timelines.

## 🛠️ Tech Stack

### Backend
- **Language**: Python 3.10+
- **Framework**: [FastAPI](https://fastapi.tiangolo.com/)
- **Astronomy**: [Skyfield](https://rhodesmill.org/skyfield/)
- **Mathematics**: NumPy
- **Server**: Uvicorn

### Frontend
- **Framework**: React 19 (TypeScript + Vite)
- **Styling**: Tailwind CSS 4, Framer Motion (Animations)
- **State Management**: Zustand
- **Data Fetching**: TanStack Query, Axios

## 📂 Project Structure

```text
├── backend/            # Python FastAPI backend
│   ├── data/           # Ephemeris files (JPL DE440)
│   ├── tests/          # Unit tests for astrology logic
│   ├── api.py          # FastAPI routes and Pydantic models
│   ├── ephemeris.py    # Core astronomical computations
│   ├── main.py         # Application entry point
│   ├── requirements.txt # Python dependencies
│   └── vedic.py        # Vedic astrology algorithms
└── frontend/           # React + Vite frontend
    ├── src/            # Application source code
    ├── public/         # Static assets
    └── package.json    # Node dependencies and scripts
```

## 🚀 Getting Started

### Prerequisites

- **Backend**: Python 3.10 or higher, `pip` or `uv`
- **Frontend**: Node.js 18+ and `npm`

### Installation & Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/Hirushikanth/Horoscope
   cd horoscope-enhanced
   ```

2. **Backend Setup**:
   ```bash
   # Create and activate virtual environment
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate

   # Install dependencies
   pip install -r backend/requirements.txt

   # Run the API server
   cd backend
   python3 -m uvicorn main:app --host 127.0.0.1 --port 8000
   ```

3. **Frontend Setup**:
   ```bash
   # Navigate to frontend directory
   cd ../frontend

   # Install dependencies
   npm install

   # Run the development server
   npm run dev
   ```

The Backend will be at `http://127.0.0.1:8000`.
The Frontend will be at `http://localhost:5173`.

## 📡 API Endpoints

### `POST /api/horoscope`
Computes a full horoscope including planets, houses, nakshatras, and dashas.

**Request Body:**
```json
{
  "date": "1990-01-15",
  "time": "06:00:00",
  "latitude": 13.0827,
  "longitude": 80.2707,
  "timezone": "Asia/Kolkata"
}
```

## 🧪 Testing

Run the test suite using `pytest`:
```bash
pytest backend/tests
```
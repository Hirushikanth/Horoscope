# Jyotisha — Precision Vedic Astrology Engine

Jyotisha is a high-precision backend engine for Vedic astrology calculations. It leverages the **NASA JPL DE440 ephemeris** via the Skyfield library to provide sub-arcsecond accuracy for planetary positions, ensuring that all Jyotisha (Vedic astrology) algorithms are based on the most accurate astronomical data available.

## 🌟 Key Features

- **Scientific Precision**: Uses IEEE 754 float64 precision throughout all calculations.
- **NASA JPL DE440**: Backed by the latest planetary ephemeris (covering 1550 to 2650 AD).
- **Vedic Algorithms**: Full implementation of traditional Jyotisha systems:
  - **Nakshatras**: 27 lunar mansions with detailed attributes (Deity, Gana, Animal, etc.).
  - **Rashis**: 12 zodiac signs with lordships and elements.
  - **Bhavas**: Equal house system calculations.
  - **Vimshottari Dasha**: 120-year planetary period cycle calculations.
  - **Panchang**: Tithi, Vara, Nakshatra, Yoga, and Karana.
  - **Dignities**: Planetary strengths (Exaltation, Debilitation, Moolatrikona).
  - **Yogas**: Detection of important planetary combinations.
- **Sidereal Calculations**: Lahiri (Chitra Paksha) Ayanamsa by default.

## 🛠️ Tech Stack

- **Language**: Python 3.10+
- **Framework**: [FastAPI](https://fastapi.tiangolo.com/)
- **Astronomy**: [Skyfield](https://rhodesmill.org/skyfield/)
- **Mathematics**: NumPy
- **Server**: Uvicorn

## 📂 Project Structure

```text
backend/
├── data/               # Ephemeris files (JPL DE440)
├── tests/              # Unit tests for astrology logic
├── api.py              # FastAPI routes and Pydantic models
├── ephemeris.py        # Core astronomical computations
├── main.py             # Application entry point
├── requirements.txt    # Python dependencies
├── stars.py            # Fixed star calculations
└── vedic.py            # Vedic astrology algorithms
```

## 🚀 Getting Started

### Prerequisites

- Python 3.10 or higher
- `pip` or `uv`

### Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd horoscope-enhanced
   ```

2. **Set up a virtual environment**:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r backend/requirements.txt
   ```

4. **Run the API server**:
   ```bash
   cd backend
   uvicorn main:app --reload
   ```

The API will be available at `http://127.0.0.1:8000`. You can view the interactive documentation at `http://127.0.0.1:8000/docs`.

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

## 📜 License

This project is licensed under the MIT License.

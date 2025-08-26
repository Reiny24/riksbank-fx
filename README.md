# Riksbank FX Data Collector

This project is a **Flask-based application** that interacts with the [Riksbank API](https://developer.api.riksbank.se/api-details#api=swea-api) to fetch and store currency exchange series and their historical observations in a local database.  
It also includes a **daily scheduled task** that keeps the database updated with the latest available data.

---

## Features

- Fetches and stores **Riksbank currency series metadata**.
- Fetches and stores **latest and historical exchange rates**.
- Provides a **Flask REST API** to access stored data:
  - `/series` → List all series in the database.
  - `/fetch-store` → Fetch and update series metadata.
  - `/history/<seriesId>` → Retrieve historical data for a given series.
- Daily automatic update of data via `schedule`.

---

## Installation

### 1. Clone the repository
```bash
git clone https://github.com/yourusername/riksbank-fx.git
cd riksbank-fx
```

### 2. Install dependencies with Poetry

Make sure you have Poetry installed.
```bash
pip install poetry
```

```bash
poetry install
```

### 3. Activate the virtual environment
```bash
poetry env use 3.10.8
```

---
## Usage
### Run Flask API
```bash
poetry run python main.py
```
---

## API Endpoints

### 1. Update series from Riksbank
```bash
http://127.0.0.1:5000/fetch-store
```

Fetches new series metadata from Riksbank and stores it in the database.

### 2. List all series
```
http://127.0.0.1:5000/series
```

Returns all available series metadata.

### 3. Get historical data for a specific series
```bash
http://127.0.0.1:5000/history/<seriesId>
```
Returns historical exchange rates for the given seriesId. seriesId - optional.

Example:
```bash
http://127.0.0.1:5000/history/SECBREPOEFF
```

---

## Database
The project uses SQLite as the local database (by default).
It contains two main tables:

- series → Stores metadata about each currency series.
  - id INTEGER PRIMARY KEY AUTOINCREMENT
  - seriesId TEXT NOT NULL UNIQUE
  - date TEXT (latest observation date)
  - latest_value FLOAT (latest observation value)
- series_history → Stores historical exchange rate observations.
  - id INTEGER PRIMARY KEY AUTOINCREMENT
  - seriesId TEXT NOT NULL
  - date TEXT (observation date)
  - value FLOAT (observation value)
  - recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

manage_db.py keeps only the latest HISTORY_LIMIT records per seriesId (default: 3).

--- 

## Development
### Format code with Black
```bash
poetry run black .
```
---

## Automatic Daily Execution
This project uses the schedule Python package to run daily updates.

### On Linux/macOS
Use cron:
```bash
crontab -e
```

Add:
```bash
0 9 * * * cd /path/to/riksbank-fx && poetry run python main.py
```

This runs the script every day at 10:00.

### On Windows
Use Task Scheduler:
- Create a new task
- Set trigger to Daily
- Action: poetry run python main.py
- Start in: project directory

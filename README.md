# Disk Scheduling Visualizer (OSproject)

A small Flask-based web service that visualizes disk scheduling algorithms and returns the service order, seek statistics and a PNG plot as a base64 data URI.

## Project Structure

- `app.py`: Flask application implementing the scheduling algorithms and a `/visualize` API endpoint; serves `index.html` at the root.
- `templates/index.html`: Basic frontend page (not strictly required to use the API).
- `static/`: Static assets and built frontend files.

## Features

- Implements common disk scheduling algorithms:
  - `FCFS` (First-Come, First-Served)
  - `SSTF` (Shortest Seek Time First)
  - `SCAN` (Elevator)
  - `C-SCAN` (Circular SCAN)
- Produces a PNG plot of the service sequence (returned as a base64 data URI).
- Returns total and average movements and total seek time in milliseconds.
- CORS is enabled for cross-origin requests.

## Requirements

This project requires Python 3.8+ and the following packages:

- `Flask`
- `matplotlib`
- `numpy`
- `flask-cors`

You can install these with pip. Example:

PowerShell:

```powershell
python -m venv .venv; .\.venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install Flask matplotlib numpy flask-cors
```

Or a single-line pip command (once venv activated):

```powershell
pip install Flask matplotlib numpy flask-cors
```

## Running the App (locally)

PowerShell commands to run the app locally (default host 0.0.0.0, port 8088):

```powershell
# from project root (where app.py lives)
python app.py
```

Open a browser to `http://localhost:8088/` to view the frontend (if used).

## API: `/visualize` (POST)

This endpoint accepts a JSON payload describing disk head state and requests. It returns the scheduling sequence, metrics, total seek time, and a base64 PNG image of the plot.

Request JSON fields (keys used by `app.py`):

- `CurrentHeadPosition` (int or string): current head position (e.g. `50`).
- `TotalNumberOfTracks` (int or string, optional): total number of tracks (default 200 in code).
- `SpeedPerTrackMs` (int or string, optional): ms per track movement (default 10 in code).
- `RequestQueue` (string): comma-separated list of integer track requests (e.g. `10,20,78,34`).
- `Algorithm` (string): one of `FCFS`, `SSTF`, `SCAN`, `C-SCAN` (the code also accepts some longer labels like `FCFS (First-Come, First-Served)`).
- `Direction` (string): `Left` or `Right` (controls initial head movement for SCAN/C-SCAN).

Example POST (curl):

```bash
curl -X POST http://localhost:8088/visualize \
  -H "Content-Type: application/json" \
  -d '{
    "CurrentHeadPosition": "50",
    "RequestQueue": "10,20,78,34",
    "Algorithm": "SSTF",
    "Direction": "Right",
    "SpeedPerTrackMs": "10"
  }'
```

Example PowerShell using `Invoke-RestMethod`:

```powershell
$payload = @{
  CurrentHeadPosition = "50"
  RequestQueue = "10,20,78,34"
  Algorithm = "SSTF"
  Direction = "Right"
  SpeedPerTrackMs = "10"
} | ConvertTo-Json

Invoke-RestMethod -Uri http://localhost:8088/visualize -Method Post -Body $payload -ContentType 'application/json'
```

Response format (JSON):

- `algorithm_results`: object with `sequence` (list), `total_movements` (int) and `average_movements` (float).
- `total_seek_time_ms`: computed as `total_movements * SpeedPerTrackMs`.
- `plot_image`: data URI string like `data:image/png;base64,<base64-payload>`.

## Notes & Tips

- `matplotlib.use('Agg')` is set so the server can render plots headlessly (no display required).
- Input parsing in `app.py` expects many values as strings and attempts to coerce them to integers; malformed values will default (e.g. head defaults to `0`, tracks default to `200`).
- The server listens on port `8088` by default (see `app.run()` in `app.py`).
- CORS is enabled for `*` origins which is convenient for development but consider restricting origins for production.

## Troubleshooting

- If you see errors when importing modules, ensure your virtual environment is active and required packages are installed.
- If plots are blank or missing, confirm the request `sequence` is non-empty and that `matplotlib` saved the image bytes properly.

## License & Attribution

This repository is a small teaching/demo project. Adapt freely for educational purposes.

---


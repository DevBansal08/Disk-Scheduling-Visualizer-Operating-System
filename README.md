# Disk Scheduling Visualizer — College Project

A small, easy-to-run Flask web app that demonstrates and visualizes common disk scheduling algorithms. Useful for learning how different algorithms affect head movement and seek time.

**What this does:** The app accepts a list of disk track requests and a current head position, runs a chosen scheduling algorithm (FCFS, SSTF, SCAN, C-SCAN), and returns the service order, seek statistics, and a PNG plot (as a base64 data URI).

**Designed for:** students and instructors as a demonstration or lab exercise.

**Quick Links**

- **Run:** `python app.py`
- **API endpoint:** `POST /visualize`
- **Project file:** `app.py`

**Project structure (important files)**

- `app.py`: Main Flask server and API logic.
- `templates/index.html`: Simple frontend (optional).
- `static/`: Frontend assets.

**Supported algorithms (brief)**

- **FCFS** — First-Come, First-Served: serve requests in the order received.
- **SSTF** — Shortest Seek Time First: pick the closest pending request next.
- **SCAN** — Elevator: head moves in one direction, servicing requests, then reverses.
- **C-SCAN** — Circular SCAN: like SCAN but jumps back to the start without servicing on the return.

Getting started (Windows PowerShell)

1. Create and activate a virtual environment, then install dependencies:

```powershell
python -m venv .venv; .\.venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install Flask matplotlib numpy flask-cors
```

2. Run the app (default port 8088):

```powershell
# from project root (where README.md and app.py live)
python app.py
```

3. Open `http://localhost:8088/` in a browser to see the frontend (optional), or call the API directly.

API: `POST /visualize` (simple example)

Expected JSON fields (all strings or numbers accepted; code coerces types):

- `CurrentHeadPosition`: integer (e.g. `50`)
- `RequestQueue`: comma-separated numbers (e.g. `10,20,78,34`)
- `Algorithm`: `FCFS`, `SSTF`, `SCAN`, or `C-SCAN`
- `Direction`: `Left` or `Right` (used for SCAN/C-SCAN)
- `SpeedPerTrackMs`: time per track in ms (optional, default used if missing)

Example using PowerShell (`Invoke-RestMethod`):

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

Or with `curl`:

```bash
curl -X POST http://localhost:8088/visualize \
  -H "Content-Type: application/json" \
  -d '{"CurrentHeadPosition":"50","RequestQueue":"10,20,78,34","Algorithm":"SSTF","Direction":"Right","SpeedPerTrackMs":"10"}'
```

Response (JSON) includes:

- `algorithm_results`: `{ sequence: [...], total_movements: n, average_movements: x }`
- `total_seek_time_ms`: integer
- `plot_image`: `data:image/png;base64,...` (plot of head movement)

How it helps your project / report

- Use the outputs to compare algorithms: total movements and seek time are easy metrics to tabulate.
- Save the returned `plot_image` (decode base64) for reports or slides.

Troubleshooting

- If imports fail, ensure your virtual env is active and dependencies installed.
- If responses are missing fields, check that `RequestQueue` parses to integers (comma-separated) and `CurrentHeadPosition` is numeric.
- The app sets `matplotlib` to headless mode (`Agg`) so it works on servers without a display.



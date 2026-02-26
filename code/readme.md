## Open Source Python project (example missions)

This repo also ships small Python scripts that you can reuse or adapt.

### What it does

- Generate **grid missions** (lawnmower pattern)
- Generate **POI circle/orbit missions**
- Export to:
  - **KML** (Google Earth preview)
  - **Litchi CSV** (import into Litchi Mission Hub)

### Quick start

```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

pip install -r requirements.txt
python map_os2.py
```

### Outputs

- `mission.kml` — preview the path in Google Earth
- `mission_litchi.csv` — import into Litchi Mission Hub

![Python 3.13](https://img.shields.io/badge/Python-3.13-green.svg)
![PyQt5](https://img.shields.io/badge/PyQT5-green.svg)
![license MIT](https://img.shields.io/badge/license-MIT-green.svg)
![platform Windows](https://img.shields.io/badge/platform-Windows-lightgrey.svg) 
![platform MacOS](https://img.shields.io/badge/platform-MacOS-lightgrey.svg) 

# map-creator + Open Source Mission Generator

This repository contains:

- **map-creator (Desktop App)** — a GUI tool to plan and visualize drone waypoint missions on an interactive map and export DJI-compatible KMZ missions.
- **Open Source Python examples** — small, readable scripts (grid + POI/orbit) that demonstrate the core math and exports (KML + Litchi CSV).

> If you are here for the compiled desktop app (Windows / macOS), go to **GitHub Releases** of this repository.

---

## map-creator (Desktop App)

**map-creator** is a desktop application for planning and visualizing drone missions directly on an interactive map. It allows you to:

- Draw **polygons** or **circles** on a map
- Generate **waypoint grids** inside the drawn area
- Adjust **bearing, altitude, photo distance, pitch, and cross patterns**
- Preview missions visually
- Export missions as **KMZ** files for DJI applications
- Load **KMZ, KML and CSV** missions

### Installation (Windows)

1. Download the **Map-Creator ZIP** from this repository’s **Releases** page.
2. Start the setup wizard.
3. Start the application:
   - Windows: double-click `map-creator.exe`

No additional installation is required.

### Creating a mission

1. Draw an area on the map:
   - Polygon for area missions
   - 2-point circle (centre + radius) for circular missions
2. Adjust parameters using the sliders:
   - Bearing
   - Altitude
   - Photo distance
   - Pitch
   - Cross pattern (optional)
3. Click **Calculate Raster** to generate waypoints.
4. Review the flight path and waypoint markers.

### Elevation mode

When **Elevation** is enabled, terrain data is fetched online and added to your waypoints (internet connection required). A progress indicator is shown during processing.

### Exporting missions

1. Click **Save KMZ**
2. Choose a file location
3. Import the KMZ into supported DJI applications (optionally via **DJIKMZInjector**)

### Photogrammetry Wizard (Assistant)

map-creator includes an integrated **Photogrammetry Wizard** that evaluates mission parameters while you plan and provides real-time feedback and suggestions (e.g., altitude, photo distance, mission splitting). It is designed as **guidance**, not a restriction—you can always continue with your chosen settings.

### Privacy & connectivity

Elevation requests require an internet connection. Missions are processed locally on your computer.

Watch the video:
[![Watch the video](https://img.youtube.com/vi/LUwJ74JaNIQ/maxresdefault.jpg)](https://youtu.be/LUwJ74JaNIQ)

---

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
# generate a mission grid
mission = generate_grid_mission(
   rows=5,
   cols=5,
   start_lon=8.3,
   start_lat=47.5,
   heading=45,
   pitch=-70,
   spacing=10,
   altitude=60,
   poi_lat=0,
   poi_lon=0
)
# export kml
export_kml(
   [[p.lon, p.lat, p.alt] for p in mission],
   "mission.kml"
)
# export Litchi csv
export_litchi_csv(mission, "mission_litchi.csv")
# generate a circle POI mission grid
mission = single_circle_poi(
  poi_lat=47.5,
  poi_lon=8.3,
  altitude=60,
  radius_m=25,
  poi_alt=0,
  edges=12
)
# export Litchi csv
export_litchi_csv(mission, "orbit.csv")
```

### Outputs

- `mission.kml` — preview the path in Google Earth
- `mission_litchi.csv` — import into Litchi Mission Hub

---

## Releases (compiled app)

Precompiled binaries for **Windows** and **macOS** are published under the **Releases** section of this GitHub repository:

- Windows: `map-creator.exe` (installer/zip)
- macOS: packaged app (see Releases)

---

## Support / Contact

- Website: https://map-creator.com
- Email: support@map-creator.com

---

## License

- The **open source Python examples** in this repository are released under the license specified in `LICENSE`.
- The **map-creator desktop application** distributed via Releases may have separate licensing/terms.

## Gaussian Splatting

Watch the video:
[![Watch the video](https://img.youtube.com/vi/xbpYkrBMoUU/maxresdefault.jpg)](https://youtu.be/xbpYkrBMoUU)

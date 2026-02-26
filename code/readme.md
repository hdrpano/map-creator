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

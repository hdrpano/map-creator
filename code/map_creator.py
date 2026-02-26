"""
Simple Drone Map Grid Creator
Open Source Example
"""

import math
from typing import List, Tuple
import simplekml
from litchi_mission import LitchiMissionCSV, MissionPoint


# ===============================
# Constants
# ===============================

EARTH_RADIUS = 6371000.0  # meters
DEG2RAD = math.pi / 180.0
RAD2DEG = 180.0 / math.pi


# ===============================
# Geodesy Helpers
# ===============================

def destination_point(lat: float, lon: float, distance: float, heading: float,
                      radius: float = EARTH_RADIUS) -> Tuple[float, float]:
    """
    Calculate destination point given start lat/lon, distance (m) and heading (deg).
    Returns (lon, lat)
    """
    lat_rad = lat * DEG2RAD
    lon_rad = lon * DEG2RAD
    heading_rad = heading * DEG2RAD

    angular_distance = distance / radius

    new_lat = math.asin(
        math.sin(lat_rad) * math.cos(angular_distance) +
        math.cos(lat_rad) * math.sin(angular_distance) * math.cos(heading_rad)
    )

    new_lon = lon_rad + math.atan2(
        math.sin(heading_rad) * math.sin(angular_distance) * math.cos(lat_rad),
        math.cos(angular_distance) - math.sin(lat_rad) * math.sin(new_lat)
    )

    return new_lon * RAD2DEG, new_lat * RAD2DEG


def distance_between(lat1: float, lon1: float,
                     lat2: float, lon2: float) -> float:
    """
    Great circle distance in meters.
    """
    lat1_rad = lat1 * DEG2RAD
    lat2_rad = lat2 * DEG2RAD
    dlon_rad = (lon2 - lon1) * DEG2RAD

    x = (math.sin(lat1_rad) * math.sin(lat2_rad) +
         math.cos(lat1_rad) * math.cos(lat2_rad) * math.cos(dlon_rad))

    x = max(-1.0, min(1.0, x))  # numerical safety
    return math.acos(x) * EARTH_RADIUS


def bearing_between(lat1: float, lon1: float,
                    lat2: float, lon2: float) -> float:
    """
    Bearing in degrees (0° = North)
    """
    lat1_rad = lat1 * DEG2RAD
    lat2_rad = lat2 * DEG2RAD
    dlon_rad = (lon2 - lon1) * DEG2RAD

    y = math.sin(dlon_rad) * math.cos(lat2_rad)
    x = (math.cos(lat1_rad) * math.sin(lat2_rad) -
         math.sin(lat1_rad) * math.cos(lat2_rad) * math.cos(dlon_rad))

    return math.atan2(y, x) * RAD2DEG


# ===============================
# KML Export
# ===============================

def export_kml(mission: List[List[float]], filename: str) -> None:
    """
    Export mission as Google Earth KML.
    """
    kml = simplekml.Kml()
    kml.document.name = "Drone Grid Mission"

    coords = [(p[0], p[1], round(p[2], 1)) for p in mission]

    line = kml.newlinestring(
        name="Mission",
        description="Generated Drone Grid",
        coords=coords
    )

    line.altitudemode = simplekml.AltitudeMode.relativetoground
    line.extrude = 1
    line.style.linestyle.width = 1.5
    line.style.linestyle.color = simplekml.Color.red

    kml.save(filename)


# ===============================
# Grid Mission Generator
# ===============================

def generate_grid_mission(
    rows: int,
    cols: int,
    start_lon: float,
    start_lat: float,
    heading: float,
    pitch: float,
    spacing: float,
    altitude: float,
    poi_lat: float,
    poi_lon: float
) -> List[MissionPoint]:
    """
    Generate lawnmower-style grid mission.
    """
    mission: list[MissionPoint] = []
    
    curve = max(0.2, round(spacing / 3, 1))
    speed = max(0.5, round(spacing / 5, 1))

    heading = (heading + 540) % 360 - 180  # normalize to ±180

    current_lat = start_lat
    current_lon = start_lon

    mission.append(MissionPoint(
        lat=current_lat,
        lon=current_lon,
        alt=altitude,
        pitch=pitch,
        curve=curve,
        poi_lat=poi_lat,
        poi_lon=poi_lon,
        trigger_dist=spacing,
        speed=speed
    ))

    direction_flag = 0

    for col in range(cols):
        # move forward rows
        for _ in range(rows - 1):
            current_lon, current_lat = destination_point(
                current_lat, current_lon, spacing, heading
            )

            mission.append(MissionPoint(
                lat=current_lat,
                lon=current_lon,
                alt=altitude,
                pitch=pitch,
                curve=curve,
                poi_lat=poi_lat,
                poi_lon=poi_lon,
                trigger_dist=spacing,
                speed=speed
            ))

        # move sideways between columns
        if col < cols - 1:
            side_heading = heading + 90 if direction_flag == 0 else heading - 90
            direction_flag = 1 - direction_flag

            current_lon, current_lat = destination_point(
                current_lat, current_lon, spacing, side_heading
            )

            mission.append(MissionPoint(
                lat=current_lat,
                lon=current_lon,
                alt=altitude,
                pitch=pitch,
                curve=curve,
                poi_lat=poi_lat,
                poi_lon=poi_lon,
                trigger_dist=spacing,
                speed=speed
            ))

            heading = (heading + 180) % 360 - 180

    return mission

def inner_circle_radius(circum_radius: float, edges: int) -> float:
    """Inkreisradius eines regelmäßigen Polygons mit Umkreisradius."""
    if edges < 3:
        return 0.0
    return circum_radius * math.cos(math.pi / edges)

def single_circle_poi(
    poi_lat: float,
    poi_lon: float,
    altitude: float,
    radius_m: float,
    poi_alt: float = 0.0,
    edges: int = 6,
) -> List[MissionPoint]:
    """
    Orbit um POI (Waypoint-Punkte auf Kreis). Heading/Pitch wird später im Litchi-Export
    zum POI berechnet (empfohlen).
    """
    edges = max(3, int(edges))

    trigger_dist = round(2 * math.pi * radius_m / edges, 1)
    speed = max(0.1, round(trigger_dist / 5, 1))
    speed = min(8.0, speed)

    curve = round(inner_circle_radius(radius_m, edges) / 2 * 0.6, 1)

    mission: List[MissionPoint] = []

    for c in range(edges):
        heading = c * 360.0 / edges
        # destination_point erwartet heading in Grad (0=N)
        lon, lat = destination_point(poi_lat, poi_lon, radius_m, heading)

        mission.append(MissionPoint(
            lat=lat,
            lon=lon,
            alt=altitude,
            pitch=0.0,          # wird im Exporter (POI) gesetzt
            curve=curve,
            poi_lat=poi_lat,
            poi_lon=poi_lon,
            trigger_dist=trigger_dist,
            speed=speed,
            poi_alt=poi_alt
        ))

    return mission

def export_litchi_csv(mission: List[MissionPoint], filename: str) -> None:
    litchi = LitchiMissionCSV()
    litchi.points = mission
    litchi.export(filename)

# ===============================
# Example Usage
# ===============================

if __name__ == "__main__":
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

    export_kml(
        [[p.lon, p.lat, p.alt] for p in mission],
        "mission.kml"
    )

    export_litchi_csv(mission, "mission_litchi.csv")

    mission = single_circle_poi(
        poi_lat=47.5,
        poi_lon=8.3,
        altitude=60,
        radius_m=25,
        poi_alt=0,
        edges=12
    )

    export_litchi_csv(mission, "orbit.csv")

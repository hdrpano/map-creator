"""
Simple Drone Map Grid Creator
Open Source Example CSV import/export
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Iterable, Union
import csv
import logging
import math


@dataclass
class MissionPoint:
    lat: float
    lon: float
    alt: float
    pitch: float
    curve: float
    poi_lat: float
    poi_lon: float
    trigger_dist: float
    speed: float
    poi_alt: float = 0.0


class LitchiMissionCSV:
    """
    Reads/writes Litchi Mission CSV to an internal array format:
    [[lat, lon, alt, pitch, curve, latPOI, lonPOI, trigger, speed], ...]
    """

    # Litchi CSV header prefix (fix)
    HEADER_PREFIX = [
        "latitude", "longitude", "altitude(m)", "heading(deg)", "curvesize(m)",
        "rotationdir", "gimbalmode", "gimbalpitchangle",
    ]

    # Litchi actions block (fix)
    ACTION_COLS = []
    for i in range(1, 16):
        ACTION_COLS += [f"actiontype{i}", f"actionparam{i}"]

    # Litchi tail (fix, except speed index in older exports varies -> we detect by name)
    HEADER_SUFFIX = [
        "altitudemode", "speed(m/s)",
        "poi_latitude", "poi_longitude", "poi_altitude(m)", "poi_altitudemode",
        "photo_timeinterval", "photo_distinterval",
    ]

    POI_MIN_DISTANCE = 0.5  # Meter

    def __init__(self, logger: Optional[logging.Logger] = None):
        self.log = logger or logging.getLogger(__name__)
        self.points: List[MissionPoint] = []
        self.alt_ref: float = 0.0
        self.heading: float = 0.0
        self.photo_dist_default: float = 20.0

    @staticmethod
    def _to_float(val: str, default: float = 0.0) -> float:
        try:
            return float(val)
        except (TypeError, ValueError):
            return default

    def _validate_header(self, header: List[str]) -> int:
        """
        Returns speedIndex (index of 'speed(m/s)').
        Raises ValueError on invalid header.
        """
        if len(header) < 8:
            raise ValueError("Invalid CSV: header too short")

        if header[0] != "latitude" or header[1] != "longitude":
            raise ValueError("Invalid CSV: first columns must be latitude,longitude")

        if "speed(m/s)" not in header:
            raise ValueError("Invalid CSV: 'speed(m/s)' column not found")

        if header[2] != "altitude(m)":
            raise ValueError("Only meters are supported for KMZ export (altitude(m) required)")

        speed_index = header.index("speed(m/s)")

        # Deine bisherige Prüfung: len(row) == speedIndex + 7
        # Das ist praktisch: ab speed(m/s) kommen noch 7 Felder bis photo_distinterval.
        expected_len = speed_index + 7
        if len(header) != expected_len:
            raise ValueError(f"Invalid CSV: expected {expected_len} columns, got {len(header)}")

        return speed_index

    def _bearing(self, lat1, lon1, lat2, lon2):
        """
        Bearing 0–360° (North = 0)
        """
        DEG2RAD = math.pi / 180.0
        RAD2DEG = 180.0 / math.pi

        lat1 *= DEG2RAD
        lat2 *= DEG2RAD
        dlon = (lon2 - lon1) * DEG2RAD

        y = math.sin(dlon) * math.cos(lat2)
        x = (math.cos(lat1) * math.sin(lat2) -
             math.sin(lat1) * math.cos(lat2) * math.cos(dlon))

        brng = math.atan2(y, x) * RAD2DEG
        return (brng + 360) % 360

    def _haversine(self, lat1, lon1, lat2, lon2):
        R = 6371000.0
        DEG2RAD = math.pi / 180.0

        dlat = (lat2 - lat1) * DEG2RAD
        dlon = (lon2 - lon1) * DEG2RAD

        lat1 *= DEG2RAD
        lat2 *= DEG2RAD

        a = (math.sin(dlat / 2) ** 2 +
             math.cos(lat1) * math.cos(lat2) *
             math.sin(dlon / 2) ** 2)

        return 2 * R * math.asin(math.sqrt(a))

    def _pitch_to_poi(self, lat, lon, alt, poi_lat, poi_lon, poi_alt=0.0):
        """
        Negative pitch looking down at POI.
        """
        # horizontale Distanz
        dist = self._haversine(lat, lon, poi_lat, poi_lon)

        if dist <= 0:
            return 0.0

        angle = math.degrees(math.atan2(alt, dist))
        return -abs(angle)
        alt_diff = alt - poi_alt
        return -math.degrees(math.atan2(alt_diff, dist))
    

    def load(self, csv_path: Union[str, Path]) -> "LitchiMissionCSV":
        """
        Reads CSV and fills self.points, alt_ref, heading.
        """
        csv_path = Path(csv_path)
        self.log.info(f"Load CSV mission file {csv_path}")

        self.points.clear()
        self.alt_ref = 0.0
        self.heading = 0.0

        with csv_path.open("r", newline="", encoding="utf-8-sig") as f:
            reader = csv.reader(f, delimiter=",")
            header = next(reader, None)
            if not header:
                raise ValueError("Empty CSV")

            speed_index = self._validate_header(header)

            # Row parsing: wir lesen nur die Felder, die du benutzt
            for row_i, row in enumerate(reader, start=1):
                # Skip empty rows
                if not row or all((c.strip() == "" for c in row)):
                    continue

                # Schutz: Zeilenlänge muss passen
                if len(row) != len(header):
                    raise ValueError(f"Invalid row length at line {row_i+1}: {len(row)} != {len(header)}")

                lat = self._to_float(row[0])
                lon = self._to_float(row[1])
                alt = self._to_float(row[2])
                heading = self._to_float(row[3])
                curve = self._to_float(row[4])
                pitch = self._to_float(row[7])

                speed = self._to_float(row[speed_index])
                poi_lat = self._to_float(row[speed_index + 1])
                poi_lon = self._to_float(row[speed_index + 2])
                trigger_dist = self._to_float(row[speed_index + 6])

                # Deine Logik für erste Zeile (Referenzwerte/Defaults)
                if not self.points:
                    self.heading = heading
                    self.alt_ref = alt
                    self.log.info(f"Heading {round(self.heading, 1)}° mission altitude {self.alt_ref}m")

                    if self.alt_ref < 5 or self.alt_ref > 120:
                        self.alt_ref = 30.0
                        self.log.info("Mission altitude in CSV out of range, set it to 30m")

                    # distance/speed defaults wie bei dir
                    if trigger_dist in (-1.0, 0.0):
                        trigger_dist = self.photo_dist_default
                        self.log.info(
                            f"Distance photo trigger not set, set it to {self.photo_dist_default}m"
                        )

                    # Du hast speed aus distance/5 überschrieben (DNG save 5s)
                    # Ich lasse das als Option: nur wenn speed<=0 setzen wir sie aus trigger_dist
                    if speed <= 0:
                        speed = round(trigger_dist / 5.0, 1)

                self.points.append(MissionPoint(
                    lat=lat, lon=lon, alt=alt, pitch=pitch, curve=curve,
                    poi_lat=poi_lat, poi_lon=poi_lon,
                    trigger_dist=trigger_dist, speed=speed
                ))

        return self

    def to_array(self) -> List[List[float]]:
        return [
            [p.lat, p.lon, p.alt, p.pitch, p.curve, p.poi_lat, p.poi_lon, p.trigger_dist, p.speed]
            for p in self.points
        ]

    def from_array(self, arr: Iterable[Iterable[float]]) -> "LitchiMissionCSV":
        self.points = [
            MissionPoint(*map(float, row))  # erwartet genau 9 Werte
            for row in arr
        ]
        return self

    def export(self, out_path: Union[str, Path]) -> Path:
        """
        Writes Litchi CSV. If out_path has no suffix, '.csv' is added.
        """
        out_path = Path(out_path)
        if out_path.suffix.lower() != ".csv":
            out_path = out_path.with_suffix(".csv")

        header = (
            self.HEADER_PREFIX
            + self.ACTION_COLS
            + self.HEADER_SUFFIX
        )

        with out_path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f, delimiter=",", lineterminator="\n")
            writer.writerow(header)

            for i, p in enumerate(self.points):
                dist_to_poi = self._haversine(
                    p.lat, p.lon,
                    p.poi_lat, p.poi_lon
                )

                # Heading Berechnung
                if dist_to_poi > self.POI_MIN_DISTANCE:
                    heading = self._bearing(p.lat, p.lon, p.poi_lat, p.poi_lon)
                    pitch = self._pitch_to_poi(
                        p.lat, p.lon, p.alt,
                        p.poi_lat, p.poi_lon,
                        poi_alt=getattr(p, "poi_alt", 0.0)  # falls du poi_alt ergänzt hast
                    )
                else:
                    # Richtung zum nächsten Punkt (oder letzter Punkt: vorheriger)
                    if i < len(self.points) - 1:
                        next_p = self.points[i + 1]
                        heading = self._bearing(p.lat, p.lon, next_p.lat, next_p.lon)
                    elif len(self.points) >= 2:
                        prev_p = self.points[i - 1]
                        heading = self._bearing(prev_p.lat, prev_p.lon, p.lat, p.lon)
                    else:
                        heading = 0.0

                    pitch = p.pitch
                
                row = [
                    p.lat, p.lon, p.alt,
                    heading,            # heading(deg)
                    p.curve,
                    0,                  # rotationdir
                    2,                  # gimbalmode
                    pitch,              # gimbalpitchangle
                ]

                # actiontype/actionparam 1..15: alles -1,0 wie bei dir
                for _ in range(15):
                    row += [-1, 0]

                row += [
                    0,          # altitudemode
                    p.speed,
                    p.poi_lat,
                    p.poi_lon,
                    p.poi_alt,  # poi_altitude(m)
                    0,          # poi_altitudemode
                    0,          # photo_timeinterval
                    p.trigger_dist,  # photo_distinterval
                ]

                writer.writerow(row)

        return out_path

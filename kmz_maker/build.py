from __future__ import annotations
import pandas as pd
import simplekml
from dataclasses import dataclass
from typing import Optional, Iterable

@dataclass
class StyleConfig:
    point_color: str = "ff33aaff"   # aabbggrr
    cemetery_color: str = "ff00a000"
    trail_color: str = "ffffaa00"
    point_scale: float = 1.1

def _add_point(kml: simplekml.Kml, row: pd.Series, style: StyleConfig):
    p = kml.newpoint(name=str(row.get("name","")), coords=[(row["lon"], row["lat"])])
    p.description = str(row.get("description", ""))
    p.style.iconstyle.color = style.point_color if row.get("type","point")!="cemetery" else style.cemetery_color
    p.style.iconstyle.scale = style.point_scale

def _add_trails(kml: simplekml.Kml, df: pd.DataFrame, style: StyleConfig):
    # Expect rows with type == 'trail' and a 'route' id to group
    for route, g in df.groupby("route"):
        line = kml.newlinestring(name=f"Trail {route}")
        line.coords = [(lon, lat) for lat, lon in zip(g["lat"], g["lon"])]
        line.style.linestyle.width = 3
        line.style.linestyle.color = style.trail_color

def build_kmz(csv_path: str, out_kmz: str, style: Optional[StyleConfig]=None) -> str:
    """Build a KMZ from a CSV describing points and trails.

    CSV columns:
      type: 'point' | 'cemetery' | 'trail'
      name: str
      description: str (optional)
      lat, lon: float
      route: str/int (for trail rows; groups line segments)

    """
    style = style or StyleConfig()
    df = pd.read_csv(csv_path)

    # basic validation
    required = {"type","lat","lon"}
    missing = required - set(map(str.lower, df.columns))
    # normalize columns to lowercase
    df.columns = [c.lower() for c in df.columns]

    if not required.issubset(df.columns):
        raise ValueError(f"CSV must include columns: {sorted(required)}")

    kml = simplekml.Kml()

    # points (including cemeteries)
    points = df[df["type"].isin(["point","cemetery"])]
    for _, row in points.iterrows():
        _add_point(kml, row, style)

    # trails
    trails = df[df["type"] == "trail"]
    if not trails.empty:
        if "route" not in trails.columns:
            trails = trails.assign(route="A")
        _add_trails(kml, trails.sort_values(["route","lat","lon"]), style)

    kml.savekmz(out_kmz)
    return out_kmz

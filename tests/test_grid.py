import sys
from pathlib import Path

import geopandas as gpd
from shapely.geometry import box

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from fifteenmc.grid import build_grid


def test_build_grid_small_polygon():
    boundary = gpd.GeoDataFrame({"district_name": ["test"]}, geometry=[box(121.0, 31.0, 121.02, 31.02)], crs="EPSG:4326")
    grid = build_grid(boundary, grid_size_m=500, limit=10)
    assert not grid.empty
    assert {"grid_id", "centroid_lon", "centroid_lat"}.issubset(grid.columns)

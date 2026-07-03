import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from fifteenmc.h3_export import aggregate_to_h3


def test_aggregate_to_h3():
    df = pd.DataFrame(
        {
            "grid_id": ["g1", "g2"],
            "district_name": ["Huangpu", "Huangpu"],
            "mode": ["walk", "walk"],
            "centroid_lon": [121.48, 121.481],
            "centroid_lat": [31.23, 31.231],
            "baseline_score": [80, 90],
            "track_score": [70, 80],
            "composite_score": [75, 85],
            "gym_fitness": [2, 3],
        }
    )
    gdf = aggregate_to_h3(df, resolution=8)
    assert not gdf.empty
    assert "h3_id" in gdf.columns
    assert gdf.crs.to_string() == "EPSG:4326"

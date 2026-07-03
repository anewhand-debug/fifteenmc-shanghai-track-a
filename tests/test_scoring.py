import sys
from pathlib import Path

import pandas as pd
import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from fifteenmc.scoring import add_scores


def test_add_scores_ranges():
    cfg = yaml.safe_load((ROOT / "config" / "weights.yaml").read_text(encoding="utf-8"))
    df = pd.DataFrame(
        {
            "grid_id": ["a"],
            "mode": ["walk"],
            "centroid_lon": [121.47],
            "centroid_lat": [31.23],
            "baseline_food": [3],
            "baseline_healthcare": [2],
            "baseline_education": [2],
            "baseline_transit": [4],
            "green_area_m2": [10000],
            "baseline_daily_services": [5],
            "gym_fitness": [3],
            "sports_fields_courts": [2],
            "swimming_pool_public": [1],
            "yoga_martial_dance": [2],
            "cycle_lane_km": [4],
            "fresh_market_health_food": [3],
            "iso_radius_m": [1200],
        }
    )
    out = add_scores(df, cfg)
    assert out["baseline_score"].between(0, 100).all()
    assert out["track_score"].between(0, 100).all()
    assert out["composite_score"].between(0, 100).all()

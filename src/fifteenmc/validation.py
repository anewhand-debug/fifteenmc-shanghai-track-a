from __future__ import annotations

from pathlib import Path

import geopandas as gpd
import pandas as pd


def assert_nonempty_file(path: Path) -> None:
    if not path.exists() or path.stat().st_size == 0:
        raise AssertionError(f"Expected non-empty file: {path}")


def assert_score_columns(df: pd.DataFrame) -> None:
    required = ["baseline_score", "track_score", "composite_score", "mode"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise AssertionError(f"Missing score columns: {missing}")
    for col in ["baseline_score", "track_score", "composite_score"]:
        if not df[col].between(0, 100).all():
            raise AssertionError(f"{col} must be in 0-100 range")


def assert_geojson_loads(path: Path) -> None:
    gdf = gpd.read_file(path)
    if gdf.empty:
        raise AssertionError(f"GeoJSON has no features: {path}")
    assert_score_columns(gdf)

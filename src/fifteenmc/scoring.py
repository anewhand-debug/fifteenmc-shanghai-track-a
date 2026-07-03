from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd


def cap_score(value: pd.Series | float, target: float) -> pd.Series | float:
    if target <= 0:
        raise ValueError("Score target must be positive")
    return np.minimum(100, 100 * value / target)


def _col(df: pd.DataFrame, name: str) -> pd.Series:
    if name in df.columns:
        return pd.to_numeric(df[name], errors="coerce").fillna(0)
    return pd.Series(0, index=df.index, dtype=float)


def normalize_weights(weights: dict[str, float]) -> dict[str, float]:
    total = sum(weights.values())
    if total <= 0:
        raise ValueError("Weights must sum to a positive value")
    return {k: v / total for k, v in weights.items()}


def add_scores(metrics: pd.DataFrame, cfg: dict[str, Any]) -> pd.DataFrame:
    out = metrics.copy()
    targets = cfg["targets"]
    baseline_components = {
        "food": cap_score(_col(out, "baseline_food"), targets["food_count"]),
        "healthcare": cap_score(_col(out, "baseline_healthcare"), targets["healthcare_count"]),
        "education": cap_score(_col(out, "baseline_education"), targets["education_count"]),
        "transit": cap_score(
            _col(out, "baseline_transit") + _col(out, "metro_station") + _col(out, "metro_exit") + _col(out, "bus_stop"),
            targets["transit_count"],
        ),
        "parks": cap_score(_col(out, "green_area_m2"), targets["parks_area_m2"]),
        "daily_services": cap_score(_col(out, "baseline_daily_services"), targets["daily_services_count"]),
    }
    track_components = {
        "gym_fitness": cap_score(_col(out, "gym_fitness"), targets["gym_fitness_count"]),
        "public_park_exercise": cap_score(
            _col(out, "public_park_exercise") + (_col(out, "green_area_m2") > 0).astype(int),
            targets["public_park_exercise_count"],
        ),
        "sports_fields_courts": cap_score(_col(out, "sports_fields_courts"), targets["sports_fields_courts_count"]),
        "swimming_pool_public": cap_score(_col(out, "swimming_pool_public"), targets["swimming_pool_public_count"]),
        "yoga_martial_dance": cap_score(_col(out, "yoga_martial_dance"), targets["yoga_martial_dance_count"]),
        "cycle_lane_length": cap_score(_col(out, "cycle_lane_km"), targets["cycle_lane_length_km"]),
        "fresh_market_health_food": cap_score(
            _col(out, "fresh_market_health_food") + _col(out, "baseline_food"),
            targets["fresh_market_health_food_count"],
        ),
        "greenery_index": cap_score(
            _col(out, "green_area_m2") / np.maximum((_col(out, "iso_radius_m") ** 2 * np.pi), 1),
            targets["greenery_index"],
        ),
        "air_quality": pd.Series(50, index=out.index, dtype=float),
    }
    for name, values in baseline_components.items():
        out[f"baseline_{name}_score"] = values
    for name, values in track_components.items():
        out[f"track_{name}_score"] = values
    b_weights = normalize_weights(cfg["baseline"])
    t_weights = normalize_weights(cfg["track_a"])
    out["baseline_score"] = sum(out[f"baseline_{k}_score"] * w for k, w in b_weights.items())
    out["track_score"] = sum(out[f"track_{k}_score"] * w for k, w in t_weights.items())
    out["composite_score"] = (
        out["baseline_score"] * cfg["composite"]["baseline"]
        + out["track_score"] * cfg["composite"]["track_a"]
    )
    return out


def add_rent_band(df: pd.DataFrame, value_col: str = "rent_m2") -> pd.DataFrame:
    out = df.copy()
    if value_col not in out.columns or out[value_col].isna().all():
        out["rent_band"] = "No rent data"
        return out
    q = out[value_col].quantile([0.25, 0.5, 0.75]).to_dict()

    def band(v: float) -> str:
        if pd.isna(v):
            return "No rent data"
        if v <= q[0.25]:
            return "Low"
        if v <= q[0.5]:
            return "Medium-low"
        if v <= q[0.75]:
            return "Medium-high"
        return "High"

    out["rent_band"] = out[value_col].apply(band)
    return out

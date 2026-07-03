from __future__ import annotations

import math
from typing import Any

import geopandas as gpd
import pandas as pd

from .crs import METRIC_CRS, WEB_CRS


EXPECTED_ACCESS_COLUMNS = [
    "food",
    "healthcare",
    "education",
    "daily_services",
    "park",
    "gym_fitness",
    "public_park_exercise",
    "sports_fields_courts",
    "swimming_pool_public",
    "yoga_martial_dance",
    "fresh_market_health_food",
    "metro_station",
    "metro_exit",
    "bus_stop",
    "baseline_food",
    "baseline_healthcare",
    "baseline_education",
    "baseline_transit",
    "baseline_parks",
    "baseline_daily_services",
]


def mode_radius_m(speed_kmh: float, minutes: float = 15) -> float:
    return speed_kmh * 1000 * (minutes / 60)


def build_buffer_isochrones(grid: gpd.GeoDataFrame, mode_config: dict[str, Any]) -> gpd.GeoDataFrame:
    grid_m = grid.to_crs(METRIC_CRS).copy()
    if "centroid" in grid_m.columns:
        points = gpd.GeoSeries(grid_m["centroid"], crs=METRIC_CRS)
    else:
        points = grid_m.geometry.centroid
    radius = mode_radius_m(mode_config["speed_kmh"], mode_config.get("minutes", 15))
    out = gpd.GeoDataFrame(
        {
            "grid_id": grid_m["grid_id"].values,
            "mode": mode_config.get("mode", "unknown"),
            "radius_m": radius,
        },
        geometry=points.buffer(radius),
        crs=METRIC_CRS,
    )
    return out.to_crs(WEB_CRS)


def count_points_within_isochrones(
    isochrones: gpd.GeoDataFrame,
    points: gpd.GeoDataFrame,
    group_col: str,
    prefix: str,
    max_pairs_for_sjoin: int = 2_000_000,
) -> pd.DataFrame:
    if points.empty or group_col not in points.columns:
        return pd.DataFrame({"grid_id": isochrones["grid_id"]})
    iso_m = isochrones.to_crs(METRIC_CRS)
    pts_m = points.to_crs(METRIC_CRS).copy()
    pts_m[group_col] = pts_m[group_col].fillna("").astype(str)
    pts_m[group_col] = pts_m[group_col].str.split("|")
    pts_m = pts_m.explode(group_col)
    pts_m[group_col] = pts_m[group_col].astype(str).str.strip()
    pts_m = pts_m[pts_m[group_col] != ""]
    if pts_m.empty:
        return pd.DataFrame({"grid_id": isochrones["grid_id"]})
    if len(iso_m) * len(pts_m) > max_pairs_for_sjoin:
        return _count_points_batched(iso_m, pts_m, group_col, prefix)
    joined = gpd.sjoin(
        pts_m[[group_col, "geometry"]],
        iso_m[["grid_id", "geometry"]],
        how="inner",
        predicate="within",
    )
    if joined.empty:
        return pd.DataFrame({"grid_id": isochrones["grid_id"]})
    counts = (
        joined.groupby(["grid_id", group_col])
        .size()
        .unstack(fill_value=0)
        .add_prefix(prefix)
        .reset_index()
    )
    return counts


def _count_points_batched(
    iso_m: gpd.GeoDataFrame,
    pts_m: gpd.GeoDataFrame,
    group_col: str,
    prefix: str,
    batch_size: int = 500,
) -> pd.DataFrame:
    sindex = pts_m.sindex
    records: list[dict[str, Any]] = []
    for start in range(0, len(iso_m), batch_size):
        batch = iso_m.iloc[start : start + batch_size]
        for row in batch.itertuples():
            candidate_idx = list(sindex.query(row.geometry, predicate="intersects"))
            if not candidate_idx:
                records.append({"grid_id": row.grid_id})
                continue
            counts = pts_m.iloc[candidate_idx][group_col].value_counts()
            record: dict[str, Any] = {"grid_id": row.grid_id}
            for group, value in counts.items():
                record[f"{prefix}{group}"] = int(value)
            records.append(record)
    return pd.DataFrame(records).fillna(0)


def area_within_isochrones(
    isochrones: gpd.GeoDataFrame,
    polygons: gpd.GeoDataFrame,
    output_col: str,
) -> pd.DataFrame:
    if polygons.empty:
        return pd.DataFrame({"grid_id": isochrones["grid_id"], output_col: 0.0})
    iso_m = isochrones.to_crs(METRIC_CRS)
    poly_m = polygons.to_crs(METRIC_CRS)
    clipped = gpd.overlay(poly_m[["geometry"]], iso_m[["grid_id", "geometry"]], how="intersection")
    if clipped.empty:
        return pd.DataFrame({"grid_id": isochrones["grid_id"], output_col: 0.0})
    clipped[output_col] = clipped.geometry.area
    result = clipped.groupby("grid_id", as_index=False)[output_col].sum()
    return result


def nearest_distance(
    origins: gpd.GeoDataFrame,
    destinations: gpd.GeoDataFrame,
    output_col: str,
) -> pd.DataFrame:
    if destinations.empty:
        return pd.DataFrame({"grid_id": origins["grid_id"], output_col: math.nan})
    ori = origins.to_crs(METRIC_CRS).copy()
    dest = destinations.to_crs(METRIC_CRS).copy()
    ori["geometry"] = ori.geometry.centroid
    joined = gpd.sjoin_nearest(
        ori[["grid_id", "geometry"]],
        dest[["geometry"]],
        how="left",
        distance_col=output_col,
    )
    return joined[["grid_id", output_col]].drop_duplicates("grid_id")


def build_accessibility_table(
    grid: gpd.GeoDataFrame,
    amenities: gpd.GeoDataFrame,
    green: gpd.GeoDataFrame,
    weights_cfg: dict[str, Any],
) -> pd.DataFrame:
    modes = weights_cfg["modes"]
    frames = []
    for mode, cfg in modes.items():
        cfg = dict(cfg)
        cfg["mode"] = mode
        iso = build_buffer_isochrones(grid, cfg)
        counts = count_points_within_isochrones(iso, amenities, "category_group", "")
        baseline = count_points_within_isochrones(iso, amenities, "baseline_groups", "baseline_")
        merged = grid[["grid_id", "district_name", "centroid_lon", "centroid_lat", "geometry"]].copy()
        for table in [counts, baseline]:
            merged = merged.merge(table, on="grid_id", how="left")
        if not green.empty:
            area = area_within_isochrones(iso, green, "green_area_m2")
            merged = merged.merge(area, on="grid_id", how="left")
        else:
            merged["green_area_m2"] = 0.0
        merged["mode"] = mode
        merged["iso_radius_m"] = iso["radius_m"].iloc[0] if len(iso) else None
        for col in EXPECTED_ACCESS_COLUMNS:
            if col not in merged.columns:
                merged[col] = 0
        frames.append(pd.DataFrame(merged.drop(columns="geometry")))
    out = pd.concat(frames, ignore_index=True).fillna(0)
    return out

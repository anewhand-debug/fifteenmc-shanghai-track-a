from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import geopandas as gpd
import pandas as pd
from shapely.geometry import Polygon

from .crs import WEB_CRS
from .io import ensure_parent

try:
    import h3
except Exception:  # pragma: no cover
    h3 = None


def latlng_to_h3(lat: float, lng: float, resolution: int) -> str:
    if h3 is None:
        raise ImportError("h3 package is required for H3 export")
    if hasattr(h3, "latlng_to_cell"):
        return h3.latlng_to_cell(lat, lng, resolution)
    return h3.geo_to_h3(lat, lng, resolution)


def h3_boundary(cell: str) -> Polygon:
    if h3 is None:
        raise ImportError("h3 package is required for H3 export")
    if hasattr(h3, "cell_to_boundary"):
        coords = h3.cell_to_boundary(cell)
    else:
        coords = h3.h3_to_geo_boundary(cell)
    return Polygon([(lng, lat) for lat, lng in coords])


def aggregate_to_h3(grid_scores: pd.DataFrame, resolution: int = 8) -> gpd.GeoDataFrame:
    df = grid_scores.copy()
    df["h3_id"] = [latlng_to_h3(lat, lon, resolution) for lat, lon in zip(df["centroid_lat"], df["centroid_lon"])]
    numeric_cols = [
        c
        for c in df.columns
        if c not in {"grid_id", "district_name", "mode", "h3_id", "rent_band"}
        and pd.api.types.is_numeric_dtype(df[c])
    ]
    agg_numeric = df.groupby(["h3_id", "mode"], as_index=False)[numeric_cols].mean()
    district = (
        df.groupby(["h3_id", "mode"])["district_name"]
        .agg(lambda s: s.mode().iloc[0] if not s.mode().empty else "Unknown")
        .reset_index()
    )
    out = agg_numeric.merge(district, on=["h3_id", "mode"], how="left")
    out["geometry"] = out["h3_id"].apply(h3_boundary)
    gdf = gpd.GeoDataFrame(out, geometry="geometry", crs=WEB_CRS)
    gdf["top_amenities"] = gdf.apply(_top_amenities, axis=1)
    gdf["rent_band"] = "See local housing proxy"
    gdf["metro_distance_m"] = gdf.get("metro_distance_m", pd.Series([None] * len(gdf))).fillna(-1)
    gdf["data_quality_flags"] = "Buffer-based isochrone approximation; AQI optional unless supplied"
    return gdf


def _top_amenities(row: pd.Series) -> str:
    candidates = [
        ("Gyms", row.get("gym_fitness", 0)),
        ("Sports courts", row.get("sports_fields_courts", 0)),
        ("Pools", row.get("swimming_pool_public", 0)),
        ("Yoga/dance", row.get("yoga_martial_dance", 0)),
        ("Transit stops", row.get("bus_stop", 0) + row.get("metro_station", 0)),
    ]
    ranked = sorted(candidates, key=lambda x: x[1], reverse=True)
    return ", ".join(f"{name}: {int(value)}" for name, value in ranked[:3])


def export_frontend_geojson(h3_scores: gpd.GeoDataFrame, path: Path) -> Path:
    keep = [
        "h3_id",
        "mode",
        "district_name",
        "baseline_score",
        "track_score",
        "composite_score",
        "top_amenities",
        "metro_distance_m",
        "rent_band",
        "data_quality_flags",
        "gym_fitness",
        "sports_fields_courts",
        "swimming_pool_public",
        "yoga_martial_dance",
        "green_area_m2",
        "cycle_lane_km",
        "geometry",
    ]
    cols = [c for c in keep if c in h3_scores.columns]
    gdf = h3_scores[cols].copy().to_crs(WEB_CRS)
    for col in gdf.select_dtypes(include="number").columns:
        gdf[col] = gdf[col].round(3)
    ensure_parent(path)
    gdf.to_file(path, driver="GeoJSON")
    return path


def export_frontend_geojson_wide(h3_scores: gpd.GeoDataFrame, path: Path) -> Path:
    id_cols = ["h3_id", "geometry"]
    static_cols = ["district_name", "top_amenities", "metro_distance_m", "rent_band", "data_quality_flags"]
    score_cols = [
        "baseline_score",
        "track_score",
        "composite_score",
        "gym_fitness",
        "sports_fields_courts",
        "swimming_pool_public",
        "yoga_martial_dance",
        "green_area_m2",
        "cycle_lane_km",
    ]
    base = h3_scores.sort_values("mode").drop_duplicates("h3_id")[id_cols + [c for c in static_cols if c in h3_scores.columns]].copy()
    wide = base.set_index("h3_id")
    for mode in sorted(h3_scores["mode"].unique()):
        mode_df = h3_scores[h3_scores["mode"] == mode].set_index("h3_id")
        for col in score_cols:
            if col in mode_df.columns:
                wide[f"{mode}_{col}"] = mode_df[col]
    wide = wide.reset_index()
    gdf = gpd.GeoDataFrame(wide, geometry="geometry", crs=WEB_CRS).to_crs(WEB_CRS)
    for col in gdf.select_dtypes(include="number").columns:
        gdf[col] = gdf[col].round(3)
    ensure_parent(path)
    gdf.to_file(path, driver="GeoJSON")
    return path


def export_frontend_h3_json_wide(h3_scores: gpd.GeoDataFrame, path: Path) -> Path:
    static_cols = ["district_name", "top_amenities", "metro_distance_m", "rent_band", "data_quality_flags"]
    score_cols = [
        "baseline_score",
        "track_score",
        "composite_score",
        "gym_fitness",
        "sports_fields_courts",
        "swimming_pool_public",
        "yoga_martial_dance",
        "green_area_m2",
        "cycle_lane_km",
    ]
    base = h3_scores.sort_values("mode").drop_duplicates("h3_id")[["h3_id"] + [c for c in static_cols if c in h3_scores.columns]].copy()
    wide = base.set_index("h3_id")
    for mode in sorted(h3_scores["mode"].unique()):
        mode_df = h3_scores[h3_scores["mode"] == mode].set_index("h3_id")
        for col in score_cols:
            if col in mode_df.columns:
                wide[f"{mode}_{col}"] = mode_df[col]
    wide = wide.reset_index()
    for col in wide.select_dtypes(include="number").columns:
        wide[col] = wide[col].round(3)
    features = [
        {"type": "Feature", "properties": {k: _json_safe(v) for k, v in row.items()}}
        for row in wide.to_dict("records")
    ]
    data = {"type": "FeatureCollection", "features": features}
    ensure_parent(path)
    path.write_text(json.dumps(data, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    return path


def _json_safe(value: Any) -> Any:
    if pd.isna(value):
        return None
    if hasattr(value, "item"):
        return value.item()
    return value

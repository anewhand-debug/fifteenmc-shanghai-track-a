from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Any

import geopandas as gpd
import pandas as pd
import yaml

from .crs import METRIC_CRS, WEB_CRS, ensure_crs
from .io import read_any_geodata, write_geoparquet
from .paths import ProjectPaths


POI_SOURCE_SPECS = [
    {
        "key": "sports_poi",
        "source": "sports_fitness_poi",
        "collection_date": "2023-01-14",
        "default_category_group": "gym_fitness",
        "default_track_groups": ["gym_fitness"],
        "default_baseline_groups": [],
    },
    {
        "key": "food_poi",
        "source": "food_poi",
        "collection_date": "2021-08-26",
        "default_category_group": "food",
        "default_track_groups": [],
        "default_baseline_groups": ["food"],
    },
    {
        "key": "shopping_poi",
        "source": "shopping_poi",
        "collection_date": "2021-08-26",
        "default_category_group": "daily_services",
        "default_track_groups": [],
        "default_baseline_groups": ["food"],
    },
    {
        "key": "healthcare_poi",
        "source": "healthcare_poi",
        "collection_date": "2021-11-30",
        "default_category_group": "healthcare",
        "default_track_groups": [],
        "default_baseline_groups": ["healthcare"],
    },
    {
        "key": "education_poi",
        "source": "education_poi",
        "collection_date": "2021-08-26",
        "default_category_group": "education",
        "default_track_groups": [],
        "default_baseline_groups": ["education"],
    },
    {
        "key": "daily_finance_poi",
        "source": "daily_finance_poi",
        "collection_date": "2021-08-26",
        "default_category_group": "daily_services",
        "default_track_groups": [],
        "default_baseline_groups": ["daily_services"],
    },
    {
        "key": "daily_other_poi",
        "source": "daily_other_poi",
        "collection_date": "2021-08-26",
        "default_category_group": "daily_services",
        "default_track_groups": [],
        "default_baseline_groups": ["daily_services"],
    },
    {
        "key": "park_poi",
        "source": "park_poi",
        "collection_date": "2022-04-22",
        "default_category_group": "park",
        "default_track_groups": [],
        "default_baseline_groups": ["parks"],
    },
    {
        "key": "sports_field_polygons",
        "source": "sports_field_polygons",
        "collection_date": "2021-08-27",
        "default_category_group": "sports_fields_courts",
        "default_track_groups": ["sports_fields_courts"],
        "default_baseline_groups": [],
    },
    {
        "key": "sports_center_polygons",
        "source": "sports_center_polygons",
        "collection_date": "2021-08-27",
        "default_category_group": "sports_fields_courts",
        "default_track_groups": ["sports_fields_courts"],
        "default_baseline_groups": [],
    },
    {
        "key": "swimming_pool_polygons",
        "source": "swimming_pool_polygons",
        "collection_date": "2021-08-27",
        "default_category_group": "swimming_pool_public",
        "default_track_groups": ["swimming_pool_public"],
        "default_baseline_groups": [],
    },
    {
        "key": "running_track_polygons",
        "source": "running_track_polygons",
        "collection_date": "2021-08-27",
        "default_category_group": "sports_fields_courts",
        "default_track_groups": ["sports_fields_courts"],
        "default_baseline_groups": [],
    },
]


def _first_present(columns: list[str], candidates: list[str]) -> str | None:
    lowered = {str(c).lower(): c for c in columns}
    for cand in candidates:
        if cand.lower() in lowered:
            return lowered[cand.lower()]
    for col in columns:
        col_text = str(col).lower()
        if any(cand.lower() in col_text for cand in candidates):
            return col
    return None


def _combine_text(row: pd.Series, columns: list[str]) -> str:
    values = [str(row.get(col, "")) for col in columns if col in row.index and pd.notna(row.get(col))]
    return " ".join(values)


def _keyword_match(text: str, mapping: dict[str, Any]) -> list[str]:
    text_l = text.lower()
    matches = []
    for group, spec in mapping.items():
        if any(str(kw).lower() in text_l for kw in spec.get("keywords", [])):
            matches.append(group)
    return matches


def load_category_mapping(project_root: Path) -> dict[str, Any]:
    with (project_root / "config" / "category_mapping.yaml").open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def clean_geometries(gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    gdf = gdf[gdf.geometry.notna()].copy()
    gdf = gdf[~gdf.geometry.is_empty].copy()
    invalid = ~gdf.geometry.is_valid
    if invalid.any():
        gdf.loc[invalid, "geometry"] = gdf.loc[invalid, "geometry"].buffer(0)
    return gdf[gdf.geometry.notna() & ~gdf.geometry.is_empty].copy()


def load_boundary(paths: ProjectPaths) -> gpd.GeoDataFrame:
    gdf = read_any_geodata(paths.raw("shanghai_boundary"))
    gdf = clean_geometries(gdf)
    gdf = gdf.to_crs(WEB_CRS)
    name_col = _first_present(list(gdf.columns), ["name", "district", "区", "市"])
    if name_col and name_col != "district_name":
        gdf["district_name"] = gdf[name_col].astype(str)
    elif "district_name" not in gdf.columns:
        gdf["district_name"] = "Shanghai"
    return gdf


def dissolve_boundary(boundary: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    dissolved = boundary.to_crs(METRIC_CRS).dissolve()
    dissolved["study_area"] = "Shanghai"
    return dissolved[["study_area", "geometry"]].to_crs(WEB_CRS)


def normalize_sports_poi(paths: ProjectPaths, limit: int | None = None) -> gpd.GeoDataFrame:
    return normalize_poi_source(paths, POI_SOURCE_SPECS[0], limit=limit)


def normalize_poi_source(paths: ProjectPaths, spec: dict[str, Any], limit: int | None = None) -> gpd.GeoDataFrame:
    mapping = load_category_mapping(paths.project_root)
    row_limit = limit or _env_int("FIFTEENMC_POI_LIMIT")
    path = paths.raw(spec["key"])
    if not path.exists():
        return gpd.GeoDataFrame(
            columns=[
                "poi_id",
                "name",
                "category_raw",
                "category_group",
                "track_a_groups",
                "baseline_groups",
                "source",
                "collection_date",
                "is_public",
                "geometry",
            ],
            geometry="geometry",
            crs=WEB_CRS,
        )
    gdf = read_any_geodata(path, rows=row_limit)
    gdf = clean_geometries(gdf).to_crs(WEB_CRS)
    gdf = _ensure_point_geometry(gdf)
    cols = [c for c in gdf.columns if c != "geometry"]
    name_col = _first_present(cols, ["name", "名称", "name_ch", "poi_name"])
    type_col = _first_present(cols, ["type", "category", "类别", "大类", "中类", "小类"])
    text_cols = [c for c in [name_col, type_col] if c]
    if not text_cols:
        text_cols = cols[: min(4, len(cols))]
    rows = []
    for idx, row in gdf.iterrows():
        text = _combine_text(row, text_cols)
        track_groups = _keyword_match(text, mapping["track_a_categories"]) or spec.get("default_track_groups", [])
        baseline_groups = _keyword_match(text, mapping["baseline_categories"]) or spec.get("default_baseline_groups", [])
        category_group = track_groups[0] if track_groups else spec.get("default_category_group", "uncategorized")
        rows.append(
            {
                "poi_id": f"{spec['source']}_{idx}",
                "name": str(row.get(name_col, "")) if name_col else "",
                "category_raw": str(row.get(type_col, "")) if type_col else text,
                "category_group": category_group,
                "track_a_groups": "|".join(track_groups),
                "baseline_groups": "|".join(baseline_groups),
                "source": spec["source"],
                "collection_date": spec["collection_date"],
                "is_public": None,
                "geometry": row.geometry,
            }
        )
    out = gpd.GeoDataFrame(rows, crs=WEB_CRS)
    out["lon"] = out.geometry.x
    out["lat"] = out.geometry.y
    out = out.drop_duplicates(subset=["name", "lon", "lat"])
    return out


def normalize_local_pois(paths: ProjectPaths, limit: int | None = None) -> gpd.GeoDataFrame:
    frames = [normalize_poi_source(paths, spec, limit=limit) for spec in POI_SOURCE_SPECS]
    frames = [frame for frame in frames if not frame.empty]
    if not frames:
        return gpd.GeoDataFrame(columns=["poi_id", "name", "category_group", "geometry"], geometry="geometry", crs=WEB_CRS)
    out = pd.concat(frames, ignore_index=True)
    return gpd.GeoDataFrame(out, geometry="geometry", crs=WEB_CRS)


def normalize_transit(paths: ProjectPaths, limit: int | None = None) -> gpd.GeoDataFrame:
    row_limit = limit or _env_int("FIFTEENMC_POI_LIMIT")
    frames = []
    for key, mode, date in [
        ("metro_stations", "metro_station", "2023-12-19"),
        ("metro_exits", "metro_exit", "2023-12-19"),
        ("bus_stops", "bus_stop", "2024-07-13"),
    ]:
        path = paths.raw(key)
        if not path.exists():
            continue
        gdf = read_any_geodata(path, rows=row_limit)
        gdf = clean_geometries(gdf).to_crs(WEB_CRS)
        cols = [c for c in gdf.columns if c != "geometry"]
        name_col = _first_present(cols, ["name", "名称", "station", "站名"])
        frame = gpd.GeoDataFrame(
            {
                "poi_id": [f"{mode}_{i}" for i in range(len(gdf))],
                "name": gdf[name_col].astype(str).values if name_col else [mode] * len(gdf),
                "category_group": [mode] * len(gdf),
                "baseline_groups": ["transit"] * len(gdf),
                "source": [key] * len(gdf),
                "collection_date": [date] * len(gdf),
            },
            geometry=gdf.geometry.values,
            crs=WEB_CRS,
        )
        frames.append(frame)
    if not frames:
        return gpd.GeoDataFrame(columns=["poi_id", "name", "category_group", "geometry"], geometry="geometry", crs=WEB_CRS)
    return pd.concat(frames, ignore_index=True)


def normalize_green(paths: ProjectPaths, limit: int | None = None) -> gpd.GeoDataFrame:
    row_limit = limit or _env_int("FIFTEENMC_POI_LIMIT")
    frames = []
    for key, source, date in [
        ("park_polygons", "park_polygons", "2022-11-13"),
        ("green_polygons", "green_polygons", "2026-05-28"),
    ]:
        path = paths.raw(key)
        if not path.exists():
            continue
        gdf = read_any_geodata(path)
        if row_limit:
            gdf = gdf.head(row_limit)
        gdf = clean_geometries(gdf).to_crs(WEB_CRS)
        out = gdf[["geometry"]].copy()
        out["source"] = source
        out["collection_date"] = date
        frames.append(out)
        if key == "park_polygons":
            break
    if not frames:
        return gpd.GeoDataFrame(columns=["source", "geometry"], geometry="geometry", crs=WEB_CRS)
    return gpd.GeoDataFrame(pd.concat(frames, ignore_index=True), geometry="geometry", crs=WEB_CRS)


def _ensure_point_geometry(gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    if gdf.empty:
        return gdf
    if gdf.geometry.geom_type.isin(["Point", "MultiPoint"]).all():
        return gdf
    metric = gdf.to_crs(METRIC_CRS).copy()
    metric["geometry"] = metric.geometry.representative_point()
    return metric.to_crs(WEB_CRS)


def normalize_housing(paths: ProjectPaths, limit: int | None = None) -> gpd.GeoDataFrame:
    path = paths.raw("house_price_points")
    if not path.exists():
        return gpd.GeoDataFrame(columns=["price_value", "geometry"], geometry="geometry", crs=WEB_CRS)
    row_limit = limit or _env_int("FIFTEENMC_POI_LIMIT")
    gdf = read_any_geodata(path, rows=row_limit)
    gdf = clean_geometries(gdf).to_crs(WEB_CRS)
    cols = [c for c in gdf.columns if c != "geometry"]
    price_col = _first_present(cols, ["price", "rent", "价格", "房价", "均价", "单价"])
    name_col = _first_present(cols, ["name", "名称", "小区", "project"])
    out = gpd.GeoDataFrame(
        {
            "name": gdf[name_col].astype(str).values if name_col else "",
            "price_value": _parse_numeric_series(gdf[price_col]) if price_col else pd.Series([None] * len(gdf)),
            "price_field": price_col or "",
            "source": "housing_rent_price",
            "collection_date": "2024-06-07",
        },
        geometry=gdf.geometry.values,
        crs=WEB_CRS,
    )
    return out


def build_processed_datasets(paths: ProjectPaths, smoke: bool = False) -> dict[str, Path]:
    limit = 500 if smoke else None
    boundary = load_boundary(paths)
    write_geoparquet(boundary, paths.output("boundary"))
    pois = normalize_local_pois(paths, limit=limit)
    transit = normalize_transit(paths, limit=limit)
    amenities = pd.concat([pois, transit], ignore_index=True)
    write_geoparquet(gpd.GeoDataFrame(amenities, geometry="geometry", crs=WEB_CRS), paths.output("amenities"))
    write_geoparquet(transit, paths.output("transit"))
    return {
        "boundary": paths.output("boundary"),
        "amenities": paths.output("amenities"),
        "transit": paths.output("transit"),
    }


def _parse_numeric_series(series: pd.Series) -> pd.Series:
    return pd.to_numeric(
        series.astype(str).str.replace(",", "", regex=False).str.extract(r"([-+]?\d*\.?\d+)")[0],
        errors="coerce",
    )


def _env_int(name: str) -> int | None:
    value = os.getenv(name)
    if not value:
        return None
    try:
        return int(value)
    except ValueError:
        return None

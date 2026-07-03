from __future__ import annotations

import shutil
import sys
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
from sklearn.neighbors import BallTree

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from fifteenmc.cleaning import build_processed_datasets, load_boundary, normalize_green
from fifteenmc.grid import attach_districts, build_grid
from fifteenmc.h3_export import aggregate_to_h3, export_frontend_h3_json_wide
from fifteenmc.io import write_geoparquet
from fifteenmc.paths import load_project_paths, load_yaml
from fifteenmc.scoring import add_scores


EARTH_RADIUS_M = 6_371_000


def radius_m(speed_kmh: float, minutes: float) -> float:
    return speed_kmh * 1000 * minutes / 60


def haversine_counts(origins: pd.DataFrame, points: gpd.GeoDataFrame, group_col: str, radius: float, prefix: str = "") -> pd.DataFrame:
    if points.empty or group_col not in points.columns:
        return pd.DataFrame({"grid_id": origins["grid_id"]})
    pts = points.copy()
    pts[group_col] = pts[group_col].fillna("").astype(str).str.split("|")
    pts = pts.explode(group_col)
    pts[group_col] = pts[group_col].astype(str).str.strip()
    pts = pts[pts[group_col] != ""]
    if pts.empty:
        return pd.DataFrame({"grid_id": origins["grid_id"]})

    origin_rad = np.deg2rad(origins[["centroid_lat", "centroid_lon"]].to_numpy())
    point_coords = np.deg2rad(np.c_[pts.geometry.y.to_numpy(), pts.geometry.x.to_numpy()])
    tree = BallTree(point_coords, metric="haversine")
    neighbors = tree.query_radius(origin_rad, r=radius / EARTH_RADIUS_M)

    records = []
    groups = pts[group_col].to_numpy()
    for grid_id, idxs in zip(origins["grid_id"].to_numpy(), neighbors):
        record = {"grid_id": grid_id}
        if len(idxs):
            counts = pd.Series(groups[idxs]).value_counts()
            for group, value in counts.items():
                record[f"{prefix}{group}"] = int(value)
        records.append(record)
    return pd.DataFrame(records).fillna(0)


def green_counts(origins: pd.DataFrame, green: gpd.GeoDataFrame, radius: float) -> pd.DataFrame:
    if green.empty:
        return pd.DataFrame({"grid_id": origins["grid_id"], "green_area_m2": 0.0})
    centroids = green.to_crs("EPSG:4326").copy()
    centroids["geometry"] = centroids.to_crs("EPSG:32651").geometry.centroid.to_crs("EPSG:4326")
    counts = haversine_counts(origins, centroids.assign(green_group="green"), "green_group", radius, "")
    if "green" not in counts.columns:
        counts["green"] = 0
    counts["green_area_m2"] = counts["green"] * 5000.0
    return counts[["grid_id", "green_area_m2"]]


def main() -> None:
    paths = load_project_paths(ROOT)
    weights = load_yaml(ROOT / "config" / "weights.yaml")
    build_processed_datasets(paths, smoke=False)
    boundary = load_boundary(paths)
    grid = build_grid(boundary, grid_size_m=paths.config["analysis"]["grid_size_m"])
    grid = attach_districts(grid, boundary)
    write_geoparquet(grid, paths.output("grid_500m"))

    origins = pd.DataFrame(grid.drop(columns=[col for col in ["geometry", "centroid"] if col in grid.columns]))
    amenities = gpd.read_parquet(paths.output("amenities")).to_crs("EPSG:4326")
    transit = gpd.read_parquet(paths.output("transit")).to_crs("EPSG:4326")
    green = normalize_green(paths)

    frames = []
    for mode, cfg in weights["modes"].items():
        r = radius_m(cfg["speed_kmh"], cfg.get("minutes", 15))
        mode_df = origins.copy()
        for table in [
            haversine_counts(origins, amenities, "category_group", r),
            haversine_counts(origins, amenities, "baseline_groups", r, "baseline_"),
            green_counts(origins, green, r),
        ]:
            mode_df = mode_df.merge(table, on="grid_id", how="left")
        mode_df["mode"] = mode
        mode_df["iso_radius_m"] = r
        mode_df["cycle_lane_km"] = 0.0
        frames.append(mode_df)
    access = pd.concat(frames, ignore_index=True).fillna(0)

    metro = transit[transit["category_group"].isin(["metro_station", "metro_exit"])].copy()
    if not metro.empty:
        origin_rad = np.deg2rad(origins[["centroid_lat", "centroid_lon"]].to_numpy())
        metro_rad = np.deg2rad(np.c_[metro.geometry.y.to_numpy(), metro.geometry.x.to_numpy()])
        tree = BallTree(metro_rad, metric="haversine")
        dist, _ = tree.query(origin_rad, k=1)
        dist_df = pd.DataFrame({"grid_id": origins["grid_id"], "metro_distance_m": dist[:, 0] * EARTH_RADIUS_M})
        access = access.merge(dist_df, on="grid_id", how="left")
    else:
        access["metro_distance_m"] = np.nan

    access.to_parquet(paths.output("grid_accessibility"), index=False)
    scores = add_scores(access, weights)
    scores.to_parquet(paths.output("grid_scores"), index=False)
    h3_scores = aggregate_to_h3(scores, resolution=paths.config["analysis"]["h3_resolution"])
    h3_scores.to_parquet(paths.output("h3_scores"), index=False)
    export_frontend_h3_json_wide(h3_scores, paths.output("h3_geojson"))
    shutil.copy2(paths.output("h3_geojson"), paths.output("app_h3_geojson"))

    print(f"Grid cells: {len(grid)}")
    print(f"H3-mode features: {len(h3_scores)}")
    print(f"Bounds: {tuple(round(x, 6) for x in h3_scores.total_bounds)}")
    print(f"App data: {paths.output('app_h3_geojson')}")


if __name__ == "__main__":
    main()

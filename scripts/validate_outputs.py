from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

import geopandas as gpd
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from fifteenmc.catalog import build_data_catalog, write_catalog_markdown
from fifteenmc.cleaning import (
    build_processed_datasets,
    load_boundary,
    normalize_green,
)
from fifteenmc.grid import attach_districts, build_grid
from fifteenmc.h3_export import aggregate_to_h3, export_frontend_geojson
from fifteenmc.io import write_geoparquet
from fifteenmc.isochrones import build_accessibility_table, nearest_distance
from fifteenmc.paths import load_project_paths, load_yaml
from fifteenmc.scoring import add_scores
from fifteenmc.validation import assert_geojson_loads, assert_nonempty_file, assert_score_columns


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate or smoke-run the Track A pipeline.")
    parser.add_argument("--smoke", action="store_true", help="Run with small limits for quick validation.")
    parser.add_argument("--grid-limit", type=int, default=None, help="Limit grid cells for medium-size reproducibility checks.")
    parser.add_argument("--poi-limit", type=int, default=None, help="Limit records per POI source for medium-size checks.")
    parser.add_argument(
        "--write-app",
        action="store_true",
        help="Allow limited sample runs to overwrite the app GeoJSON. Full unlimited runs always write app data.",
    )
    args = parser.parse_args()

    paths = load_project_paths(ROOT)
    weights = load_yaml(ROOT / "config" / "weights.yaml")

    catalog = build_data_catalog(paths)
    paths.output("data_catalog").parent.mkdir(parents=True, exist_ok=True)
    catalog.to_csv(paths.output("data_catalog"), index=False, encoding="utf-8-sig")
    write_catalog_markdown(catalog, ROOT / "docs" / "DATA_DICTIONARY.md")

    if args.poi_limit:
        import os

        os.environ["FIFTEENMC_POI_LIMIT"] = str(args.poi_limit)
    build_processed_datasets(paths, smoke=args.smoke)
    boundary = load_boundary(paths)
    grid_limit = 120 if args.smoke else args.grid_limit
    grid = build_grid(boundary, grid_size_m=paths.config["analysis"]["grid_size_m"], limit=grid_limit)
    grid = attach_districts(grid, boundary)
    write_geoparquet(grid, paths.output("grid_500m"))

    amenities = gpd.read_parquet(paths.output("amenities"))
    green = normalize_green(paths, limit=100 if args.smoke else None)
    access = build_accessibility_table(grid, amenities, green, weights)

    transit = gpd.read_parquet(paths.output("transit"))
    metro = transit[transit["category_group"].isin(["metro_station", "metro_exit"])].copy()
    distance = nearest_distance(grid, metro, "metro_distance_m")
    access = access.merge(distance, on="grid_id", how="left")
    access["cycle_lane_km"] = 0.0
    access.to_parquet(paths.output("grid_accessibility"), index=False)

    scores = add_scores(access, weights)
    assert_score_columns(scores)
    scores.to_parquet(paths.output("grid_scores"), index=False)

    h3_scores = aggregate_to_h3(scores, resolution=paths.config["analysis"]["h3_resolution"])
    h3_scores.to_parquet(paths.output("h3_scores"), index=False)
    limited_run = args.smoke or args.grid_limit is not None or args.poi_limit is not None
    if limited_run and not args.write_app:
        sample_geojson = paths.project("data", "web", "h3_scores_track_a_sample.geojson")
        export_frontend_geojson(h3_scores, sample_geojson)
        geojson_for_validation = sample_geojson
    else:
        export_frontend_geojson(h3_scores, paths.output("h3_geojson"))
        shutil.copy2(paths.output("h3_geojson"), paths.output("app_h3_geojson"))
        geojson_for_validation = paths.output("h3_geojson")

    for key in ["data_catalog", "grid_500m", "grid_accessibility", "grid_scores"]:
        assert_nonempty_file(paths.output(key))
    assert_nonempty_file(geojson_for_validation)
    assert_geojson_loads(geojson_for_validation)
    print("Validation complete.")
    print(f"H3 GeoJSON: {geojson_for_validation}")
    if not limited_run or args.write_app:
        print(f"App data: {paths.output('app_h3_geojson')}")
    else:
        print("Limited run did not overwrite app/public/data/h3_scores_track_a.geojson.")


if __name__ == "__main__":
    main()

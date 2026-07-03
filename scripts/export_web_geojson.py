from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

import geopandas as gpd
import pandas as pd
import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from fifteenmc.h3_export import aggregate_to_h3, export_frontend_geojson
from fifteenmc.paths import load_project_paths, load_yaml


def main() -> None:
    parser = argparse.ArgumentParser(description="Export H3-scored frontend GeoJSON.")
    parser.add_argument("--resolution", type=int, default=None)
    args = parser.parse_args()

    paths = load_project_paths(ROOT)
    cfg = load_yaml(ROOT / "config" / "paths.yaml")
    resolution = args.resolution or cfg["analysis"]["h3_resolution"]
    scores = pd.read_parquet(paths.output("grid_scores"))
    h3_scores = aggregate_to_h3(scores, resolution=resolution)
    h3_scores.to_parquet(paths.output("h3_scores"), index=False)
    export_frontend_geojson(h3_scores, paths.output("h3_geojson"))
    shutil.copy2(paths.output("h3_geojson"), paths.output("app_h3_geojson"))
    print(f"Exported {paths.output('h3_geojson')}")
    print(f"Copied to {paths.output('app_h3_geojson')}")


if __name__ == "__main__":
    main()

from __future__ import annotations

import math

import geopandas as gpd
import pandas as pd
from shapely.geometry import box

from .crs import METRIC_CRS, WEB_CRS, to_metric
from .cleaning import clean_geometries


def build_grid(boundary: gpd.GeoDataFrame, grid_size_m: int = 500, limit: int | None = None) -> gpd.GeoDataFrame:
    metric_boundary = clean_geometries(boundary).to_crs(METRIC_CRS)
    study = metric_boundary.dissolve().geometry.iloc[0]
    minx, miny, maxx, maxy = study.bounds
    minx = math.floor(minx / grid_size_m) * grid_size_m
    miny = math.floor(miny / grid_size_m) * grid_size_m
    maxx = math.ceil(maxx / grid_size_m) * grid_size_m
    maxy = math.ceil(maxy / grid_size_m) * grid_size_m
    cells = []
    row = 0
    y = miny
    while y < maxy:
        col = 0
        x = minx
        while x < maxx:
            geom = box(x, y, x + grid_size_m, y + grid_size_m)
            if geom.intersects(study):
                cells.append({"grid_id": f"g{row:04d}_{col:04d}", "geometry": geom.intersection(study)})
                if limit and len(cells) >= limit:
                    break
            x += grid_size_m
            col += 1
        if limit and len(cells) >= limit:
            break
        y += grid_size_m
        row += 1
    grid = gpd.GeoDataFrame(cells, crs=METRIC_CRS)
    grid["centroid"] = grid.geometry.centroid
    centroids = gpd.GeoSeries(grid["centroid"], crs=METRIC_CRS).to_crs(WEB_CRS)
    grid["centroid_lon"] = centroids.x
    grid["centroid_lat"] = centroids.y
    grid["area_m2"] = grid.geometry.area
    return grid.to_crs(WEB_CRS)


def attach_districts(grid: gpd.GeoDataFrame, districts: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    grid_metric = grid.to_crs(METRIC_CRS).copy()
    districts_metric = districts.to_crs(METRIC_CRS).copy()
    if "level" in districts_metric.columns:
        district_only = districts_metric["level"].astype(str).str.lower().eq("district")
        if district_only.any():
            districts_metric = districts_metric[district_only].copy()
    if "district_name" not in districts_metric.columns:
        districts_metric["district_name"] = "Shanghai"
    centroids = grid_metric.copy()
    centroids["geometry"] = centroids.geometry.centroid
    joined = gpd.sjoin(
        centroids[["grid_id", "geometry"]],
        districts_metric[["district_name", "geometry"]],
        how="left",
        predicate="within",
    )
    joined = joined.drop_duplicates("grid_id")
    out = grid.copy()
    out = out.merge(joined[["grid_id", "district_name"]], on="grid_id", how="left")
    out["district_name"] = out["district_name"].fillna("Unknown")
    return out

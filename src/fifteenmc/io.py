from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable

import geopandas as gpd
import pandas as pd
from shapely.geometry.base import BaseGeometry

from .crs import WEB_CRS, ensure_crs


def ensure_parent(path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def read_vector(path: Path, rows: int | slice | None = None) -> gpd.GeoDataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Vector dataset not found: {path}")
    gdf = gpd.read_file(path, rows=rows)
    return ensure_crs(gdf)


def read_any_geodata(path: Path, rows: int | None = None) -> gpd.GeoDataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Dataset not found: {path}")
    suffix = path.suffix.lower()
    if suffix in {".parquet", ".pq"}:
        gdf = gpd.read_parquet(path)
        if rows:
            gdf = gdf.head(rows)
        return ensure_crs(gdf)
    return read_vector(path, rows=rows)


def write_geoparquet(gdf: gpd.GeoDataFrame, path: Path) -> Path:
    ensure_parent(path)
    gdf.to_parquet(path, index=False)
    return path


def write_geojson(gdf: gpd.GeoDataFrame, path: Path, precision: int = 6) -> Path:
    ensure_parent(path)
    gdf = ensure_crs(gdf).to_crs(WEB_CRS).copy()
    # GeoPandas writes valid GeoJSON; rounding selected numeric columns keeps web payload smaller.
    for col in gdf.select_dtypes(include="number").columns:
        gdf[col] = gdf[col].round(precision)
    gdf.to_file(path, driver="GeoJSON")
    return path


def safe_read_csv(path: Path, nrows: int | None = None) -> pd.DataFrame:
    errors: list[str] = []
    for enc in ("utf-8", "utf-8-sig", "gb18030", "gbk"):
        try:
            return pd.read_csv(path, nrows=nrows, encoding=enc)
        except Exception as exc:  # pragma: no cover - diagnostic path
            errors.append(f"{enc}: {exc}")
    raise ValueError(f"Could not read CSV {path}. Tried encodings: {'; '.join(errors)}")


def geometry_to_wkt(geoms: Iterable[BaseGeometry]) -> list[str]:
    return [geom.wkt if geom is not None else "" for geom in geoms]


def write_json(data: dict, path: Path) -> Path:
    ensure_parent(path)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return path

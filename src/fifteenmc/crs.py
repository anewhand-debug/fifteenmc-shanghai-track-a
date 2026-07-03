from __future__ import annotations

import geopandas as gpd


WEB_CRS = "EPSG:4326"
METRIC_CRS = "EPSG:32651"


def ensure_crs(gdf: gpd.GeoDataFrame, default_crs: str = WEB_CRS) -> gpd.GeoDataFrame:
    if gdf.crs is None:
        return gdf.set_crs(default_crs)
    return gdf


def to_metric(gdf: gpd.GeoDataFrame, metric_crs: str = METRIC_CRS) -> gpd.GeoDataFrame:
    return ensure_crs(gdf).to_crs(metric_crs)


def to_web(gdf: gpd.GeoDataFrame, web_crs: str = WEB_CRS) -> gpd.GeoDataFrame:
    return ensure_crs(gdf).to_crs(web_crs)

# Data Dictionary

This file is generated from `config/data_sources.yaml` and the local data inventory.

## Shanghai administrative boundary

- Dataset ID: `shanghai_admin_boundary`
- Source: Local GeoJSON boundary file in course data folder
- Collection date: 2026-05-27
- Local path: `D:\fifteenmcproject\sh-province-district.geojson`
- Exists locally: `True`
- Fields: district or name fields vary by source; polygon geometry
- Cleaning steps: Reproject to EPSG:4326 and EPSG:32651 for analysis.; Dissolve district polygons to one Shanghai study boundary.; Repair invalid geometries.
- Limitations: Administrative coastline and water treatment may differ from other sources.

## Shanghai road network

- Dataset ID: `local_roads`
- Source: Local simplified road parquet and course shapefile road layers
- Collection date: 2026-05-27
- Local path: `D:\fifteenmcproject\shanghai-roads-simplified.parquet`
- Exists locally: `True`
- Fields: road class or highway-like category if present; geometry
- Cleaning steps: Reproject to metric CRS.; Filter unusable geometries.; Assign mode speeds for walk, bike, car approximation.
- Limitations: Does not guarantee routable topology or turn restrictions.; Isochrones are approximate unless an external routing API is supplied.

## Sports and fitness services POI

- Dataset ID: `sports_fitness_poi`
- Source: Local Shanghai sports fitness service shapefile
- Collection date: 2023-01-14
- Local path: `D:\fifteenmcproject\01-SHP\01-SHP\2021.08\上海市-体育健身服务.shp`
- Exists locally: `True`
- Fields: name; category or type fields, depending on source schema; point geometry
- Cleaning steps: Normalize names and category labels.; Map raw categories to Track A amenity groups.; Remove duplicate name-coordinate pairs.
- Limitations: POI completeness and category labels may be uneven.; Public/private facility status may require manual validation.

## Baseline daily amenity POI layers

- Dataset ID: `baseline_daily_poi`
- Source: Local 2021.08 course shapefiles for food, shopping, healthcare, education, finance, other facilities, and parks
- Collection date: 2021-08-26 / 2021-11-30 / 2022-04-22
- Local path: `D:\fifteenmcproject\01-SHP\01-SHP\2021.08\上海市_餐饮.shp`
- Exists locally: `True`
- Fields: place name; category/type fields where available; point geometry or polygon centroid
- Cleaning steps: Normalize each source to a shared POI schema.; Map records to baseline groups: food, healthcare, education, parks, and daily services.; Convert polygon-only facilities to representative points for accessibility counts.
- Limitations: Some categories are broad proxies, for example shopping may include more than fresh food.; Opening hours, capacity, price, and quality are not modeled.

## Track A sports facility polygons

- Dataset ID: `track_a_sports_polygons`
- Source: Local sports field, sports center, swimming pool, and running track polygon shapefiles
- Collection date: 2021-08-27
- Local path: `D:\fifteenmcproject\01-SHP\01-SHP\2021.08\上海市_体育场区域.shp`
- Exists locally: `True`
- Fields: facility name or category fields where available; polygon geometry
- Cleaning steps: Repair geometries.; Convert polygons to representative points for isochrone counts.; Map to sports_fields_courts or swimming_pool_public Track A categories.
- Limitations: Public/private status is not guaranteed.; Facility access, fees, and current operating status are not modeled.

## Shanghai metro and bus stops/lines

- Dataset ID: `transit_stops_lines`
- Source: Local metro and bus shapefiles
- Collection date: 2023-12-19 / 2024-07-13
- Local path: `D:\fifteenmcproject\04-traffic\04-交通数据\地铁数据\上海市_地铁站.shp`
- Exists locally: `True`
- Fields: station or stop name; route or line name where available; point or line geometry
- Cleaning steps: Reproject to metric CRS.; Merge metro stations, exits, and bus stops into transit access layer.; Calculate nearest metro distance.
- Limitations: Headways, timetables, fares, crowding, and transfers are not modeled unless GTFS is added.

## Green polygons and land-use layers

- Dataset ID: `green_landuse`
- Source: Local green parquet, ESA land-use raster, and AOI/land-use shapefiles
- Collection date: 2026-05-28 / 2023-06-29
- Local path: `D:\fifteenmcproject\shanghai-full-green.parquet`
- Exists locally: `True`
- Fields: class or land-use type; polygon or raster geometry
- Cleaning steps: Clip to Shanghai.; Compute green coverage ratio by grid/isochrone.; Use as greenery proxy if Sentinel-2 NDVI is not computed.
- Limitations: Green coverage proxy is not identical to NDVI.; Vegetation season and raster acquisition date affect greenness estimates.

## Housing price and rent proxy

- Dataset ID: `housing_rent_price`
- Source: Local Anjuke/real-estate files and house price shapefile
- Collection date: 2024-06-07 / 2026-05-27
- Local path: `D:\fifteenmcproject\13-other\13-其它\06-房价数据\上海市-房价_WGS84.shp`
- Exists locally: `True`
- Fields: price or rent fields where available; residential project name; location geometry
- Cleaning steps: Parse numeric price/rent values.; Spatially aggregate to grid/H3.; Convert to rent/price band for web display.
- Limitations: Listing prices are not transaction prices.; Rent and sale price fields may be mixed depending on source.

## Shanghai bike-share activity

- Dataset ID: `mobike_activity`
- Source: UTSEUS Mobike Shanghai full CSV
- Collection date: 2026-05-27
- Local path: `D:\fifteenmcproject\UTSEUS-MOBIKE-shanghai_full.csv`
- Exists locally: `True`
- Fields: trip origin/destination coordinates if present; trip timestamps if present
- Cleaning steps: Use only aggregated activity density if included in analysis.; Remove impossible coordinates.
- Limitations: Historic bike-share data may not represent current cycling demand.

## AQI daily district average

- Dataset ID: `air_quality_optional`
- Source: AQICN/CNEMC API or user-supplied CSV
- Collection date: User supplied at runtime
- Local path: `D:\fifteenmcproject\13-other\13-其它\02-空气质量\空气质量.txt`
- Exists locally: `True`
- Fields: date; district_name; aqi; pm25
- Cleaning steps: Validate district names.; Aggregate monitoring stations to district-day averages.
- Limitations: If only sample CSV is present, it is used for interface testing and excluded from official scoring.

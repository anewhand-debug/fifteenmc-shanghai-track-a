# Methodology

## Study Unit

The project builds a 500 m grid clipped to the Shanghai study boundary. Grid construction uses EPSG:32651 so cell sizes and distances are calculated in meters. Outputs for web mapping are reprojected to EPSG:4326.

## Travel Modes

The default reproducible method approximates 15-minute isochrones using speed-based buffers from grid centroids:

- Walk: 4.8 km/h
- Bike: 14.0 km/h
- Transit: 18.0 km/h
- Car: 28.0 km/h

This is transparent and reproducible without API keys. It is not a substitute for turn-by-turn routing. If Gaode or another routing service is available, the same cache paths can be replaced with API-generated isochrones.

For large runs, point-in-isochrone counts are processed in batches to avoid materializing a citywide many-to-many spatial join in memory. Development checks can use `--smoke`, `--grid-limit`, or `--poi-limit`; final production runs should remove those limits.

## Baseline Score

The baseline measures six universal 15-minute needs: food, healthcare, education, transit, parks, and daily services. Walk and bike are the official 15-minute-city modes; transit and car are comparison layers.

Each component is capped at 100 using:

```text
component_score = min(100, 100 * observed_value / target_value)
```

Weights and targets are editable in `config/weights.yaml`.

## Track A Score

Track A focuses on healthy lifestyle and sport:

- Gym / fitness studio
- Public park with outdoor exercise support
- Running track / sports field / basketball court
- Swimming pool
- Yoga / martial arts / dance studio
- Dedicated cycling lane length, if field-identifiable
- Fresh market / health food retailer
- Greenery index or green-coverage proxy
- AQI, if a real district daily dataset is supplied

When true NDVI or AQI is unavailable, the pipeline labels the substitute clearly. Sample files are not treated as real scoring evidence.

## H3 Aggregation

Grid scores are assigned to Uber H3 resolution 8 cells using grid centroid coordinates. Numeric fields are averaged by `h3_id` and mode. The web app loads the derived H3 GeoJSON only, not raw platform data.

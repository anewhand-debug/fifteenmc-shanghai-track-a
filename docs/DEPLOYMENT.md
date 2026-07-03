# Deployment

## Local Development

```powershell
cd D:\fifteenmcproject\15mc-shanghai-track-a
python scripts\validate_outputs.py --smoke
cd app
npm install
npm run dev
```

For a medium-size local verification:

```powershell
python scripts\validate_outputs.py --grid-limit 1000 --poi-limit 2000
```

This limited command writes a sample GeoJSON and does not overwrite the app dataset by default. Refresh the full-city app dataset with:

```powershell
python scripts\build_fast_app_geojson.py
```

The app reads:

```text
app/public/data/h3_scores_track_a.geojson
```

## Production Build

```powershell
cd D:\fifteenmcproject\15mc-shanghai-track-a\app
npm run build
```

Deploy `app/dist` to Vercel, Netlify, or GitHub Pages. The app uses a public CARTO basemap and does not require a Mapbox token by default.

## Performance Notes

- Publish only the H3 GeoJSON, not raw GIS files.
- Keep web fields minimal.
- Enable gzip or brotli compression on the host.
- Use the production build for final demo timing.

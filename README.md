# The 15-Minute Shanghai Project: Track A

Healthy Lifestyle & Sport accessibility analysis for Shanghai. The project builds a reproducible pipeline from local raw GIS data to H3 resolution 8 scored GeoJSON and a deployable Web GIS application.

## Deliverables

- `notebooks/01_data_collection.ipynb`: data provenance, cleaning, validation, and an 800-word literature review.
- `notebooks/02_grid_isochrones.ipynb`: Shanghai 500 m grid and four-mode 15-minute reachability approximations.
- `notebooks/03_scoring_h3.ipynb`: baseline score, Track A score, H3 aggregation, and web GeoJSON export.
- `app/`: React + Vite + deck.gl app with H3 choropleth, mode/layer toggles, detail panel, recommender, and transparency panel.
- `docs/TRELLO_PLAN.md`: five-sprint Trello board plan with labels, due dates, checklists, and Definition of Done.

## Quick Start

```powershell
cd D:\fifteenmcproject\15mc-shanghai-track-a
conda env create -f environment.yml
conda activate 15mc-shanghai-track-a
python scripts\validate_outputs.py --smoke
```

For a larger reproducibility check without running the full city:

```powershell
python scripts\validate_outputs.py --grid-limit 1000 --poi-limit 2000
```

Limited validation writes `data/web/h3_scores_track_a_sample.geojson` and does not overwrite the app dataset unless `--write-app` is explicitly passed. To refresh the full-city app dataset, use the faster H3 export:

```powershell
python scripts\build_fast_app_geojson.py
```

Run notebook/script pipelines without limits for full analytical outputs. Full-city polygon spatial joins may take substantially longer and require more memory depending on the machine.

For the web app:

```powershell
cd D:\fifteenmcproject\15mc-shanghai-track-a\app
npm install
npm run dev
```

## Raw Data

The repository is designed to read existing local raw data from `D:\fifteenmcproject`. Large raw files are intentionally not committed. Paths are configured in `config/paths.yaml`; the environment variable `FIFTEENMC_RAW_DATA_ROOT` can override the default.

## API Keys

No API keys are committed. Optional keys are documented in `.env.example`. If Gaode/AQI credentials are not available, notebooks run with documented local data or clearly labeled sample files for interface testing only.

## Academic Integrity

AI assistance is documented in `docs/AI_USE.md`. The analysis pipeline records source, collection date, fields, cleaning actions, and limitations for every dataset in the notebooks and `docs/DATA_DICTIONARY.md`.

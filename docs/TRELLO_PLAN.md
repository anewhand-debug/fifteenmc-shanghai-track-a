# Trello Plan

Board name: `15MC Shanghai - Track A`

Lists:

- Backlog
- Sprint 1 - Week 1 Literature & environment setup
- Sprint 2 - Week 2 Data collection & grid construction
- Sprint 3 - Week 3 Isochrones, scoring & notebook
- Sprint 4 - Week 4 Track analysis & app skeleton
- Sprint 5 - Week 5 App completion & final demo
- Done
- Blocked

Labels:

- Data
- Analysis
- App
- Literature
- Review

## Sprint 1: Literature & Environment Setup

### Review project brief

- Label: Literature
- Due date: 2026-06-15
- Description: Extract all Track A deliverables, constraints, and assessment criteria from the course brief.
- Acceptance criteria / Definition of Done: A checklist exists mapping every brief requirement to a repository file or notebook section.
- Checklist:
  - Read project PDF.
  - Confirm Track A.
  - List notebook requirements.
  - List web app requirements.
  - List Trello requirements.

### Compile literature review

- Label: Literature
- Due date: 2026-06-17
- Description: Collect and synthesize at least four academic sources covering proximity planning, walkability/cycling, equity critique, and health amenities.
- Acceptance criteria / Definition of Done: An approximately 800-word literature review is placed at the top of `01_data_collection.ipynb`.
- Checklist:
  - Add 15-minute city measurement sources.
  - Add walkability/cycling sources.
  - Add equity critique sources.
  - Add health-oriented amenities sources.
  - Check citations.

### Configure Python environment

- Label: Analysis
- Due date: 2026-06-18
- Description: Create a reproducible Python environment for notebooks and scripts.
- Acceptance criteria / Definition of Done: `environment.yml` and `requirements.txt` install all required packages.
- Checklist:
  - Add geospatial packages.
  - Add H3 package.
  - Add notebook tools.
  - Test imports.

### Create repository skeleton

- Label: Review
- Due date: 2026-06-19
- Description: Create the GitHub-ready project folder structure.
- Acceptance criteria / Definition of Done: README, configs, notebooks, source folder, app folder, and docs folder exist.
- Checklist:
  - Create `.gitignore`.
  - Create `.env.example`.
  - Create config files.
  - Create notebook placeholders.
  - Create docs folder.

## Sprint 2: Data Collection & Grid Construction

### Inventory local datasets

- Label: Data
- Due date: 2026-06-22
- Description: Scan available Shanghai datasets and record source, path, collection date, fields, cleaning steps, and limitations.
- Acceptance criteria / Definition of Done: `data/processed/data_catalog.csv` and `docs/DATA_DICTIONARY.md` are generated.
- Checklist:
  - Check boundary files.
  - Check road files.
  - Check sports POI files.
  - Check transit files.
  - Check green and housing files.

### Clean amenity datasets

- Label: Data
- Due date: 2026-06-24
- Description: Normalize POI categories for baseline and Track A indicators.
- Acceptance criteria / Definition of Done: `data/processed/amenities_normalized.parquet` exists and contains standardized category fields.
- Checklist:
  - Load sports POI.
  - Load transit stops.
  - Map Track A categories.
  - Map baseline categories.
  - Remove duplicates.

### Build Shanghai 500m grid

- Label: Analysis
- Due date: 2026-06-25
- Description: Generate a 500 m grid clipped to Shanghai.
- Acceptance criteria / Definition of Done: `data/processed/grid_500m.parquet` contains stable grid IDs, centroids, district names, and geometry.
- Checklist:
  - Load boundary.
  - Reproject to metric CRS.
  - Generate grid.
  - Clip to boundary.
  - Attach district names.

### Validate data provenance

- Label: Review
- Due date: 2026-06-26
- Description: Confirm every dataset used in notebooks has provenance metadata.
- Acceptance criteria / Definition of Done: Notebook 01 records source, collection date, fields, cleaning steps, and limitations.
- Checklist:
  - Review data catalogue.
  - Review missing optional sources.
  - Mark sample-only files.
  - Confirm no API keys are committed.

## Sprint 3: Isochrones, Scoring & Notebook

### Construct travel networks

- Label: Analysis
- Due date: 2026-06-29
- Description: Prepare the assumptions or network inputs for walk, bike, transit, and car accessibility.
- Acceptance criteria / Definition of Done: Mode speed assumptions or routing source are documented in Notebook 02.
- Checklist:
  - Define walk speed.
  - Define bike speed.
  - Define transit proxy.
  - Define car comparison.
  - Cache mode assumptions.

### Generate 15-minute isochrones

- Label: Analysis
- Due date: 2026-07-01
- Description: Compute or approximate 15-minute isochrones for all four travel modes.
- Acceptance criteria / Definition of Done: Four-mode accessibility metrics are generated for each grid cell.
- Checklist:
  - Generate walk reach.
  - Generate bike reach.
  - Generate transit reach.
  - Generate car reach.
  - Document approximation limits.

### Calculate accessibility metrics

- Label: Analysis
- Due date: 2026-07-03
- Description: Spatially join amenities, transit, and green area into isochrones.
- Acceptance criteria / Definition of Done: `data/processed/grid_accessibility.parquet` contains indicator columns for scoring.
- Checklist:
  - Count baseline POIs.
  - Count Track A POIs.
  - Calculate green area.
  - Calculate metro distance.
  - Add cycling lane placeholder or real length.

### Write scoring notebook

- Label: Analysis
- Due date: 2026-07-05
- Description: Implement baseline, Track A, composite, and H3 aggregation.
- Acceptance criteria / Definition of Done: `data/web/h3_scores_track_a.geojson` is exported and loads in the app.
- Checklist:
  - Load weights.
  - Score baseline.
  - Score Track A.
  - Aggregate H3 r8.
  - Export GeoJSON.

## Sprint 4: Track Analysis & App Skeleton

### Build React app skeleton

- Label: App
- Due date: 2026-07-06
- Description: Create the Vite React app with map layout.
- Acceptance criteria / Definition of Done: The app starts locally and displays a basemap.
- Checklist:
  - Configure Vite.
  - Add MapLibre.
  - Add deck.gl.
  - Add responsive shell.

### Implement H3 choropleth

- Label: App
- Due date: 2026-07-08
- Description: Render H3 score data as a choropleth map.
- Acceptance criteria / Definition of Done: H3 cells are colored by selected score layer.
- Checklist:
  - Load GeoJSON.
  - Add H3HexagonLayer.
  - Add color scale.
  - Add legend.

### Implement detail panel

- Label: App
- Due date: 2026-07-10
- Description: Show hex-level information on click.
- Acceptance criteria / Definition of Done: Detail panel displays top amenities, metro distance, rent band, and score breakdown.
- Checklist:
  - Store selected hex.
  - Show composite score.
  - Show amenities.
  - Show rent and metro fields.
  - Adapt for mobile.

### Add transparency panel

- Label: App
- Due date: 2026-07-12
- Description: Display data sources, collection dates, and limitations.
- Acceptance criteria / Definition of Done: Users can inspect all major sources and caveats inside the app.
- Checklist:
  - Add source list.
  - Add collection dates.
  - Add API-key note.
  - Add approximation note.

## Sprint 5: App Completion & Final Demo

### Implement recommender sliders

- Label: App
- Due date: 2026-07-14
- Description: Add “Where to live” ranking controls.
- Acceptance criteria / Definition of Done: Slider changes update top 10 highlighted H3 cells.
- Checklist:
  - Add priority sliders.
  - Define ranking formula.
  - Highlight top 10.
  - Display ranked list.

### Optimize app performance

- Label: App
- Due date: 2026-07-16
- Description: Keep the public app fast on desktop and mobile.
- Acceptance criteria / Definition of Done: Production build loads the H3 layer in under 4 seconds on a normal connection.
- Checklist:
  - Minimize GeoJSON fields.
  - Build production bundle.
  - Check bundle size.
  - Enable host compression.

### Prepare final demo

- Label: Review
- Due date: 2026-07-18
- Description: Prepare final walkthrough materials and deployment notes.
- Acceptance criteria / Definition of Done: README, deployed app, notebooks, and Trello board are ready for submission.
- Checklist:
  - Run notebooks.
  - Build app.
  - Check README.
  - Capture demo screenshots.
  - Add deployed URL.

### Review academic integrity

- Label: Review
- Due date: 2026-07-19
- Description: Confirm source compliance and AI-use documentation.
- Acceptance criteria / Definition of Done: `docs/AI_USE.md` is complete and no credentials are committed.
- Checklist:
  - Check `.env`.
  - Check `.gitignore`.
  - Mark samples.
  - Review data limitations.

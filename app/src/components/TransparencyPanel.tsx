const sources = [
  ['Boundary', 'Local Shanghai administrative GeoJSON', '2026-05-27'],
  ['Roads', 'Local simplified roads and course road shapefiles', '2026-05-27'],
  ['Sport POI', 'Shanghai sports fitness service shapefile', '2023-01-14'],
  ['Transit', 'Local metro and bus stop/line shapefiles', '2023-12-19 / 2024-07-13'],
  ['Green', 'Local green polygons and ESA land-use layers', '2026-05-28 / 2023-06-29'],
  ['Housing', 'Local housing price/rent proxy files', '2024-06-07 / 2026-05-27'],
  ['AQI', 'Optional AQICN/CNEMC or user-supplied CSV', 'Runtime']
];

export default function TransparencyPanel() {
  return (
    <div className="panel-body">
      <h2>Data transparency</h2>
      <div className="source-table">
        {sources.map(([name, source, date]) => (
          <div key={name}>
            <strong>{name}</strong>
            <span>{source}</span>
            <small>{date}</small>
          </div>
        ))}
      </div>
      <p className="muted">
        Default isochrones are speed-based approximations. Walk and bike are the official 15-minute city modes;
        transit and car are comparison layers. API-key sources are optional and excluded unless configured locally.
      </p>
      <p className="muted">
        Raw platform datasets are not republished. This app loads a derived H3 GeoJSON with aggregated scores only.
      </p>
    </div>
  );
}

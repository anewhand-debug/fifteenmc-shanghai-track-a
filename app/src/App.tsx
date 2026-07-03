import { useEffect, useMemo, useState } from 'react';
import { Activity, Database, SlidersHorizontal } from 'lucide-react';
import MapView from './components/MapView';
import ModeToggle from './components/ModeToggle';
import LayerToggle from './components/LayerToggle';
import DetailPanel from './components/DetailPanel';
import RecommenderPanel from './components/RecommenderPanel';
import TransparencyPanel from './components/TransparencyPanel';
import Legend from './components/Legend';
import { featureForMode, topHexIds } from './lib/scoring';
import type { HexFeature, LayerMode, TravelMode, UserPriorities } from './types';

const defaultPriorities: UserPriorities = {
  fitness: 5,
  green: 4,
  cycling: 3,
  transit: 3,
  affordability: 2
};

export default function App() {
  const [features, setFeatures] = useState<HexFeature[]>([]);
  const [mode, setMode] = useState<TravelMode>('walk');
  const [layer, setLayer] = useState<LayerMode>('composite');
  const [selected, setSelected] = useState<HexFeature | null>(null);
  const [priorities, setPriorities] = useState<UserPriorities>(defaultPriorities);
  const [panel, setPanel] = useState<'recommend' | 'data'>('recommend');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch(`${import.meta.env.BASE_URL}data/h3_scores_track_a.geojson`, { cache: 'no-store' })
      .then((res) => {
        if (!res.ok) throw new Error(`GeoJSON request failed: ${res.status}`);
        return res.json();
      })
      .then((geojson: GeoJSON.FeatureCollection) => {
        setFeatures((geojson.features ?? []) as HexFeature[]);
      })
      .catch((error) => {
        console.error(error);
        setFeatures([]);
      })
      .finally(() => setLoading(false));
  }, []);

  const filtered = useMemo(() => features.map((feature) => featureForMode(feature, mode)), [features, mode]);
  const highlighted = useMemo(() => topHexIds(features, mode, priorities), [features, mode, priorities]);

  return (
    <main className="app-shell">
      <MapView
        features={filtered}
        layer={layer}
        mode={mode}
        selectedId={selected?.properties.h3_id}
        highlightedIds={highlighted}
        onSelect={(feature) => setSelected(featureForMode(feature, mode))}
      />

      <header className="topbar">
        <div className="brand">
          <Activity size={20} aria-hidden />
          <div>
            <h1>15-Minute Shanghai</h1>
            <p>Healthy Lifestyle & Sport</p>
          </div>
        </div>
        <div className="controls">
          <ModeToggle mode={mode} onChange={setMode} />
          <LayerToggle layer={layer} onChange={setLayer} />
        </div>
      </header>

      <aside className="side-panel">
        <div className="panel-tabs" role="tablist" aria-label="Analysis panels">
          <button className={panel === 'recommend' ? 'active' : ''} onClick={() => setPanel('recommend')}>
            <SlidersHorizontal size={16} aria-hidden />
            Recommender
          </button>
          <button className={panel === 'data' ? 'active' : ''} onClick={() => setPanel('data')}>
            <Database size={16} aria-hidden />
            Data
          </button>
        </div>
        {panel === 'recommend' ? (
          <RecommenderPanel priorities={priorities} onChange={setPriorities} features={filtered} mode={mode} highlightedIds={highlighted} />
        ) : (
          <TransparencyPanel />
        )}
      </aside>

      <DetailPanel feature={selected} onClose={() => setSelected(null)} />
      <Legend layer={layer} />

      {loading && <div className="loading">Loading H3 accessibility layer...</div>}
      {!loading && features.length === 0 && (
        <div className="loading error">No GeoJSON found. Run notebooks or `python scripts/validate_outputs.py --smoke` first.</div>
      )}
    </main>
  );
}

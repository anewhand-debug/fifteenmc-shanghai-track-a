import { X } from 'lucide-react';
import { cssScoreColor } from '../lib/colors';
import type { HexFeature } from '../types';

type Props = {
  feature: HexFeature | null;
  onClose: () => void;
};

function fmt(value?: number, digits = 0) {
  if (value === undefined || value === null || Number.isNaN(value)) return 'n/a';
  return value.toLocaleString(undefined, { maximumFractionDigits: digits });
}

export default function DetailPanel({ feature, onClose }: Props) {
  if (!feature) return null;
  const p = feature.properties;
  return (
    <section className="detail-panel" aria-label="Selected hex detail">
      <div className="detail-header">
        <div>
          <p className="eyebrow">{p.district_name ?? 'Shanghai'} · {p.mode}</p>
          <h2>{p.h3_id}</h2>
        </div>
        <button className="icon-button" onClick={onClose} aria-label="Close detail panel" title="Close">
          <X size={18} />
        </button>
      </div>

      <div className="score-row">
        <div>
          <span>Composite</span>
          <strong style={{ color: cssScoreColor(p.composite_score ?? 0) }}>{fmt(p.composite_score, 1)}</strong>
        </div>
        <div>
          <span>Baseline</span>
          <strong>{fmt(p.baseline_score, 1)}</strong>
        </div>
        <div>
          <span>Track A</span>
          <strong>{fmt(p.track_score, 1)}</strong>
        </div>
      </div>

      <dl className="detail-list">
        <div>
          <dt>Top amenities</dt>
          <dd>{p.top_amenities ?? 'No amenity summary available'}</dd>
        </div>
        <div>
          <dt>Metro distance</dt>
          <dd>{p.metro_distance_m && p.metro_distance_m > 0 ? `${fmt(p.metro_distance_m)} m` : 'n/a'}</dd>
        </div>
        <div>
          <dt>Rent band</dt>
          <dd>{p.rent_band ?? 'No rent data'}</dd>
        </div>
        <div>
          <dt>Green area</dt>
          <dd>{fmt(p.green_area_m2)} m² in modeled reach</dd>
        </div>
        <div>
          <dt>Data notes</dt>
          <dd>{p.data_quality_flags ?? 'No flags'}</dd>
        </div>
      </dl>
    </section>
  );
}

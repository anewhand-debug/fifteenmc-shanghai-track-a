import type { HexFeature, TravelMode, UserPriorities } from '../types';
import { recommenderScore } from '../lib/scoring';

type Props = {
  priorities: UserPriorities;
  onChange: (priorities: UserPriorities) => void;
  features: HexFeature[];
  mode: TravelMode;
  highlightedIds: Set<string>;
};

const controls: Array<{ key: keyof UserPriorities; label: string }> = [
  { key: 'fitness', label: 'Fitness facilities' },
  { key: 'green', label: 'Green access' },
  { key: 'cycling', label: 'Cycling support' },
  { key: 'transit', label: 'Metro access' },
  { key: 'affordability', label: 'Rent context' }
];

export default function RecommenderPanel({ priorities, onChange, features, mode, highlightedIds }: Props) {
  const top = features
    .filter((feature) => highlightedIds.has(feature.properties.h3_id))
    .map((feature) => ({ feature, score: recommenderScore(feature, priorities, mode) }))
    .sort((a, b) => b.score - a.score)
    .slice(0, 10);

  return (
    <div className="panel-body">
      <h2>Where to live</h2>
      <p className="muted">Adjust priorities to highlight the top 10 H3 hexes for an active daily routine.</p>
      <div className="slider-stack">
        {controls.map((control) => (
          <label key={control.key}>
            <span>
              {control.label}
              <b>{priorities[control.key]}</b>
            </span>
            <input
              type="range"
              min="0"
              max="10"
              step="1"
              value={priorities[control.key]}
              onChange={(event) => onChange({ ...priorities, [control.key]: Number(event.target.value) })}
            />
          </label>
        ))}
      </div>
      <ol className="top-list">
        {top.map(({ feature, score }, index) => (
          <li key={feature.properties.h3_id}>
            <span>{index + 1}</span>
            <div>
              <strong>{feature.properties.district_name ?? 'Shanghai'}</strong>
              <small>{feature.properties.h3_id} · {score.toFixed(1)}</small>
            </div>
          </li>
        ))}
      </ol>
    </div>
  );
}

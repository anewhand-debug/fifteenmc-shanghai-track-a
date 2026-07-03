import type { LayerMode } from '../types';

type Props = {
  layer: LayerMode;
};

const bins = [
  ['80-100', 'rgb(24, 121, 104)'],
  ['65-79', 'rgb(72, 157, 120)'],
  ['50-64', 'rgb(224, 177, 77)'],
  ['35-49', 'rgb(214, 112, 74)'],
  ['0-34', 'rgb(160, 62, 71)']
];

export default function Legend({ layer }: Props) {
  const label = layer === 'track' ? 'Track A score' : layer === 'baseline' ? 'Baseline score' : 'Composite score';
  return (
    <div className="legend" aria-label="Map legend">
      <strong>{label}</strong>
      {bins.map(([text, color]) => (
        <span key={text}>
          <i style={{ background: color }} />
          {text}
        </span>
      ))}
    </div>
  );
}

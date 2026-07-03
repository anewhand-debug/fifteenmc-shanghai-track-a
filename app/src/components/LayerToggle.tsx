import { Layers } from 'lucide-react';
import type { LayerMode } from '../types';

type Props = {
  layer: LayerMode;
  onChange: (layer: LayerMode) => void;
};

const layers: Array<{ key: LayerMode; label: string }> = [
  { key: 'composite', label: 'Composite' },
  { key: 'baseline', label: 'Baseline' },
  { key: 'track', label: 'Track A' }
];

export default function LayerToggle({ layer, onChange }: Props) {
  return (
    <div className="segmented layer-toggle" aria-label="Score layer">
      <span className="segmented-icon">
        <Layers size={16} aria-hidden />
      </span>
      {layers.map((item) => (
        <button key={item.key} className={layer === item.key ? 'active' : ''} onClick={() => onChange(item.key)}>
          {item.label}
        </button>
      ))}
    </div>
  );
}

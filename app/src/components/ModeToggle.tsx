import { Bike, Bus, Car, Footprints } from 'lucide-react';
import type { ReactNode } from 'react';
import type { TravelMode } from '../types';

type Props = {
  mode: TravelMode;
  onChange: (mode: TravelMode) => void;
};

const modes: Array<{ key: TravelMode; label: string; icon: ReactNode }> = [
  { key: 'walk', label: 'Walk', icon: <Footprints size={16} /> },
  { key: 'bike', label: 'Bike', icon: <Bike size={16} /> },
  { key: 'transit', label: 'Transit', icon: <Bus size={16} /> },
  { key: 'car', label: 'Car', icon: <Car size={16} /> }
];

export default function ModeToggle({ mode, onChange }: Props) {
  return (
    <div className="segmented" aria-label="Travel mode">
      {modes.map((item) => (
        <button
          key={item.key}
          className={mode === item.key ? 'active' : ''}
          onClick={() => onChange(item.key)}
          title={item.label}
          aria-label={item.label}
        >
          {item.icon}
          <span>{item.label}</span>
        </button>
      ))}
    </div>
  );
}

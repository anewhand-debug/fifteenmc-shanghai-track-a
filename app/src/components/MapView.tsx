import DeckGL from '@deck.gl/react';
import { H3HexagonLayer } from '@deck.gl/geo-layers';
import { Map } from 'react-map-gl/maplibre';
import type { PickingInfo } from '@deck.gl/core';
import { scoreColor } from '../lib/colors';
import { scoreForLayer } from '../lib/scoring';
import type { HexFeature, LayerMode } from '../types';

type Props = {
  features: HexFeature[];
  layer: LayerMode;
  mode: import('../types').TravelMode;
  selectedId?: string;
  highlightedIds: Set<string>;
  onSelect: (feature: HexFeature) => void;
};

const initialViewState = {
  longitude: 121.47,
  latitude: 31.23,
  zoom: 9.4,
  pitch: 0,
  bearing: 0
};

export default function MapView({ features, layer, mode, selectedId, highlightedIds, onSelect }: Props) {
  const h3Layer = new H3HexagonLayer<HexFeature>({
    id: 'h3-scores',
    data: features,
    pickable: true,
    stroked: true,
    filled: true,
    extruded: false,
    lineWidthMinPixels: 0.5,
    getHexagon: (feature) => feature.properties.h3_id,
    getLineColor: (feature) => {
      const id = feature.properties.h3_id;
      if (id === selectedId) return [18, 26, 36, 255];
      if (highlightedIds.has(id)) return [20, 20, 20, 255];
      return [255, 255, 255, 90];
    },
    getLineWidth: (feature) => {
      const id = feature.properties.h3_id;
      return id === selectedId || highlightedIds.has(id) ? 3 : 1;
    },
    getFillColor: (feature) => {
      const base = scoreColor(scoreForLayer(feature, layer, mode));
      if (highlightedIds.has(feature.properties.h3_id)) return [base[0], base[1], base[2], 245];
      return base;
    },
    updateTriggers: {
      getFillColor: [layer, highlightedIds],
      getLineColor: [selectedId, highlightedIds],
      getLineWidth: [selectedId, highlightedIds]
    },
    onClick: (info: PickingInfo<HexFeature>) => {
      if (info.object) onSelect(info.object);
    }
  });

  return (
    <DeckGL initialViewState={initialViewState} controller layers={[h3Layer]}>
      <Map
        mapStyle="https://basemaps.cartocdn.com/gl/positron-gl-style/style.json"
        attributionControl
      />
    </DeckGL>
  );
}

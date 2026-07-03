import type { HexFeature, LayerMode, TravelMode, UserPriorities } from '../types';

function modeValue(feature: HexFeature, mode: TravelMode, key: string): number {
  const props = feature.properties;
  const value = props[`${mode}_${key}`] ?? props[key];
  return typeof value === 'number' ? value : Number(value ?? 0);
}

function modeText(feature: HexFeature, mode: TravelMode, key: string): string | undefined {
  const props = feature.properties;
  const value = props[`${mode}_${key}`] ?? props[key];
  return value === undefined ? undefined : String(value);
}

export function scoreForLayer(feature: HexFeature, layer: LayerMode, mode?: TravelMode): number {
  const props = feature.properties;
  if (mode) {
    if (layer === 'baseline') return modeValue(feature, mode, 'baseline_score');
    if (layer === 'track') return modeValue(feature, mode, 'track_score');
    return modeValue(feature, mode, 'composite_score');
  }
  if (layer === 'baseline') return Number(props.baseline_score ?? 0);
  if (layer === 'track') return Number(props.track_score ?? 0);
  return Number(props.composite_score ?? 0);
}

export function recommenderScore(feature: HexFeature, priorities: UserPriorities, mode: TravelMode): number {
  const p = feature.properties;
  const total =
    priorities.fitness +
    priorities.green +
    priorities.cycling +
    priorities.transit +
    priorities.affordability;
  const denom = total || 1;
  const fitness = modeValue(feature, mode, 'track_score');
  const green = Math.min(100, (modeValue(feature, mode, 'green_area_m2') / 20000) * 100);
  const cycling = Math.min(100, (modeValue(feature, mode, 'cycle_lane_km') / 4) * 100);
  const metroDistance = modeValue(feature, mode, 'metro_distance_m') || Number(p.metro_distance_m ?? 0);
  const transit = metroDistance > 0 ? Math.max(0, 100 - metroDistance / 20) : 45;
  const affordability = p.rent_band?.toLowerCase().includes('low') ? 90 : p.rent_band?.includes('No') ? 50 : 60;
  return (
    fitness * priorities.fitness +
    green * priorities.green +
    cycling * priorities.cycling +
    transit * priorities.transit +
    affordability * priorities.affordability
  ) / denom;
}

export function topHexIds(features: HexFeature[], mode: TravelMode, priorities: UserPriorities): Set<string> {
  const ranked = features
    .map((feature) => ({ id: feature.properties.h3_id, score: recommenderScore(feature, priorities, mode) }))
    .sort((a, b) => b.score - a.score)
    .slice(0, 10)
    .map((item) => item.id);
  return new Set(ranked);
}

export function featureForMode(feature: HexFeature, mode: TravelMode): HexFeature {
  const p = feature.properties;
  return {
    ...feature,
    properties: {
      ...p,
      mode,
      baseline_score: modeValue(feature, mode, 'baseline_score'),
      track_score: modeValue(feature, mode, 'track_score'),
      composite_score: modeValue(feature, mode, 'composite_score'),
      gym_fitness: modeValue(feature, mode, 'gym_fitness'),
      sports_fields_courts: modeValue(feature, mode, 'sports_fields_courts'),
      swimming_pool_public: modeValue(feature, mode, 'swimming_pool_public'),
      yoga_martial_dance: modeValue(feature, mode, 'yoga_martial_dance'),
      green_area_m2: modeValue(feature, mode, 'green_area_m2'),
      cycle_lane_km: modeValue(feature, mode, 'cycle_lane_km'),
      top_amenities: modeText(feature, mode, 'top_amenities') ?? p.top_amenities
    }
  };
}

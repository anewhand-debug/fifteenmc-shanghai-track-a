export type TravelMode = 'walk' | 'bike' | 'transit' | 'car';
export type LayerMode = 'composite' | 'baseline' | 'track';

export type HexProperties = {
  h3_id: string;
  mode?: TravelMode;
  district_name?: string;
  baseline_score?: number;
  track_score?: number;
  composite_score?: number;
  top_amenities?: string;
  metro_distance_m?: number;
  rent_band?: string;
  data_quality_flags?: string;
  gym_fitness?: number;
  sports_fields_courts?: number;
  swimming_pool_public?: number;
  yoga_martial_dance?: number;
  green_area_m2?: number;
  cycle_lane_km?: number;
  [key: string]: string | number | undefined;
};

export type HexFeature = GeoJSON.Feature<GeoJSON.Polygon, HexProperties>;

export type UserPriorities = {
  fitness: number;
  green: number;
  cycling: number;
  transit: number;
  affordability: number;
};

// ═══════════════════════════════════════════════════════════════════════ #
// Jyotisha v2 API types
// Hand-written from the v2 OpenAPI schemas (backend/app/api/schemas/*).
// Lock to the OpenAPI contract, not to memory (timeline M6 risk note).
// ═══════════════════════════════════════════════════════════════════════ #

// ──────────────────────────── shared blocks ──────────────────────────── //

export interface Trilingual {
  english: string;
  sanskrit: string;
  tamil: string | null;
  sinhala: string | null;
}

export interface EphemerisInfo {
  name: string;
  source: string;
  coverage: Record<string, string>;
  accuracy: string;
}

export interface AyanamsaInfo {
  system: string;
  value_deg: number;
  definition: string;
}

/** The "Thirukanitha badge" — self-description present in every v2 response. */
export interface ComputationBadge {
  version: string;
  tradition: string;
  precision: string;
  ephemeris: EphemerisInfo;
  ayanamsa: AyanamsaInfo;
  node_convention: 'mean' | 'true';
}

/** Echo of the resolved birth input, plus the astronomical instant. */
export interface BirthInfo {
  date: string;
  time: string;
  timezone: string;
  latitude: number;
  longitude: number;
  local_datetime: string;
  utc_datetime: string;
  jd_ut1: number;
}

// ─────────────────────────────── requests ────────────────────────────── //

export interface BirthRequest {
  date: string; // YYYY-MM-DD
  time: string; // HH:MM or HH:MM:SS
  timezone: string; // IANA zone name
  latitude: number;
  longitude: number;
  node_convention?: 'mean' | 'true';
}

export interface DashaOptions {
  depth?: 1 | 2 | 3;
  year_length_days?: number;
  minimum_span_years?: number;
}

export interface MatchingRequest {
  bride: BirthRequest;
  groom: BirthRequest;
}

// ────────────────────────────── panchangam ───────────────────────────── //

export interface TithiInfo {
  index: number;
  number: number;
  paksha: 'shukla' | 'krishna';
  name: Trilingual;
}

export interface VaraInfo {
  index: number;
  name: Trilingual;
}

export interface NakshatraInfo {
  index: number;
  pada: number;
  lord: string;
  name: Trilingual;
}

export interface YogaInfo {
  index: number;
  name: Trilingual;
}

export interface KaranaInfo {
  index: number;
  name: Trilingual;
}

export interface PanchangamInfo {
  tithi: TithiInfo;
  vara: VaraInfo;
  nakshatra: NakshatraInfo;
  yoga: YogaInfo;
  karana: KaranaInfo;
}

// ────────────────────────────── jathakam ─────────────────────────────── //

export interface LagnaInfo {
  sidereal_longitude_deg: number;
  rasi_index: number;
  degree_in_sign_deg: number;
  rasi: Trilingual;
  navamsa_rasi_index: number;
  navamsa_rasi: Trilingual;
}

export type DignityType =
  | 'exalted'
  | 'debilitated'
  | 'moolatrikona'
  | 'own_sign'
  | 'neutral';

export interface DignityInfo {
  dignity: DignityType;
  rasi_index: number;
  degree_in_sign_deg: number;
  distance_from_exaltation_deg: number | null;
}

export interface GrahaInfo {
  name: string;
  names: Trilingual;
  tropical_longitude_deg: number;
  sidereal_longitude_deg: number;
  rasi_index: number;
  rasi: Trilingual;
  degree_in_sign_deg: number;
  nakshatra_index: number;
  nakshatra: Trilingual;
  pada: number;
  house_number: number;
  retrograde: boolean;
  combust: boolean;
  combustion_separation_deg: number | null;
  distance_au: number;
  dignity: DignityInfo;
  navamsa_rasi_index: number;
  navamsa_rasi: Trilingual;
  vargottama: boolean;
}

export interface BhavaInfo {
  house_number: number;
  rasi_index: number;
  rasi: Trilingual;
  lord: string;
  kendra: boolean;
  trikona: boolean;
  dusthana: boolean;
}

export interface ChevvaiDoshamInfo {
  present: boolean;
  reference_count: number;
  houses_from_lagna: number[];
  houses_from_moon: number[];
  houses_from_venus: number[];
}

// ─────────────────────────────── dasha ───────────────────────────────── //

export interface DashaBalanceInfo {
  lord: string;
  lord_years: number;
  balance_years: number;
  balance_days: number;
  fraction_remaining: number;
  janma_nakshatra_index: number;
}

export type DashaCategory = 'mahadasha' | 'antardasha' | 'pratyantardasha';

export interface DashaPeriodInfo {
  graha: string;
  category: DashaCategory;
  years: number;
  days: number;
  start_jd: number;
  end_jd: number;
  start_utc: string;
  end_utc: string;
}

export interface DashaInfo {
  year_length_days: number;
  balance: DashaBalanceInfo;
  periods: DashaPeriodInfo[];
}

// ─────────────────────────────── vargas ──────────────────────────────── //

export interface VargaSign {
  rasi_index: number;
  rasi: Trilingual;
  division_index: number;
}

export interface GrahaVargas {
  name: string;
  positions: Record<string, VargaSign>;
  vargottama: boolean;
}

// ────────────────────────────── responses ────────────────────────────── //

export interface JathakamResponse {
  meta: ComputationBadge;
  birth: BirthInfo;
  panchangam: PanchangamInfo;
  lagna: LagnaInfo;
  grahas: GrahaInfo[];
  bhavas: BhavaInfo[];
  dasha: DashaInfo;
  chevvai_dosham: ChevvaiDoshamInfo;
}

export interface AlmanacWindow {
  start_local: string;
  end_local: string;
  start_utc: string;
  end_utc: string;
}

export interface DailyAlmanac {
  available: boolean;
  vara: VaraInfo;
  sunrise_utc: string | null;
  sunrise_local: string | null;
  sunset_utc: string | null;
  sunset_local: string | null;
  next_sunrise_utc: string | null;
  next_sunrise_local: string | null;
  rahu_kalam: AlmanacWindow | null;
  yamagandam: AlmanacWindow | null;
  gulika: AlmanacWindow | null;
  abhijit: AlmanacWindow | null;
}

export interface PanchangamResponse {
  meta: ComputationBadge;
  birth: BirthInfo;
  panchangam: PanchangamInfo;
  almanac: DailyAlmanac;
}

export interface DashaResponse {
  meta: ComputationBadge;
  birth: BirthInfo;
  dasha: DashaInfo;
}

export interface VargasResponse {
  meta: ComputationBadge;
  birth: BirthInfo;
  grahas: GrahaVargas[];
}

// ────────────────────────────── matching ─────────────────────────────── //

export interface PartnerBrief {
  birth: BirthInfo;
  nakshatra_index: number;
  pada: number;
  nakshatra: Trilingual;
  rasi_index: number;
  rasi: Trilingual;
  moon_degree_in_sign_deg: number;
  chevvai_dosham: boolean;
}

export type PoruthamResult = 'uthamam' | 'madhyamam' | 'athamam';

export interface PoruthamCheck {
  id: string;
  name: Trilingual;
  governs: string;
  result: PoruthamResult;
  score: number;
  in_total: boolean;
  detail: Record<string, unknown>;
  notes: string[];
}

export interface MatchingScore {
  total: number;
  out_of: number;
  uthamam_count: number;
  madhyamam_count: number;
  athamam_count: number;
}

export interface MatchingVerdict {
  verdict: PoruthamResult;
  band: string;
  gates: Record<string, string>;
  non_negotiables: Record<string, boolean>;
  gate_overridden: boolean;
  reasons: string[];
}

export interface ChevvaiCrossCheck {
  bride_dosham: boolean;
  groom_dosham: boolean;
  compatible: boolean;
  note: string;
}

export interface MatchingResponse {
  meta: ComputationBadge;
  tradition: string;
  bride: PartnerBrief;
  groom: PartnerBrief;
  poruthams: PoruthamCheck[];
  score: MatchingScore;
  verdict: MatchingVerdict;
  chevvai_cross_check: ChevvaiCrossCheck;
}

// ─────────────────────────────── stars ───────────────────────────────── //

export interface StarInfo {
  hip_id: number;
  name: string;
  designation: string;
  sanskrit_name: string | null;
  associated_nakshatra_index: number | null;
  associated_nakshatra: Trilingual | null;
  magnitude: number;
  ra_hours: number;
  dec_degrees: number;
  distance_light_years: number;
  tropical_longitude_deg: number;
  sidereal_longitude_deg: number;
  ecliptic_latitude_deg: number;
  rasi_index: number;
  rasi: Trilingual;
  nakshatra_index: number;
  proper_motion_ra_mas_per_year: number;
  proper_motion_dec_mas_per_year: number;
}

export interface StarsResponse {
  meta: ComputationBadge;
  birth: BirthInfo;
  stars: StarInfo[];
  count: number;
}

// ────────────────────────────── system ───────────────────────────────── //

export interface MetaResponse {
  name: string;
  version: string;
  ephemeris: EphemerisInfo;
  precision: string;
  tradition: string;
  ayanamsa: AyanamsaInfo;
  node_convention: string;
  runtime: Record<string, string>;
}

export interface HealthResponse {
  status: string;
  service: string;
  version: string;
  ephemeris: {
    name: string;
    file_present: boolean;
    loaded: boolean;
  };
}

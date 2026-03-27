export interface BirthData {
  date: string;     // YYYY-MM-DD
  time: string;     // HH:MM:SS
  latitude: number;
  longitude: number;
  timezone: string;
}

export interface HoroscopeResponse {
  ascendant: {
    sidereal_longitude: number;
    rashi: { name: string; english: string; lord: string };
    nakshatra: { name: string; ruler: string; pada: number };
  };
  planets: Record<string, any>;
  bhavas: any[];
  janma_nakshatra: any;
  panchang: any;
  dasha: any;
  divisional_charts: any;
  yogas: any[];
}

export interface MatchingInput {
  bride: BirthData;
  groom: BirthData;
  system: 'north_indian' | 'south_indian' | 'both';
}

export interface MatchingResponse {
  bride: { nakshatra: any; rashi: any; moon_longitude: number };
  groom: { nakshatra: any; rashi: any; moon_longitude: number };
  kootas?: Record<string, any>;
  total_points: number;
  max_points: number;
  compatibility_level: string;
  compatibility_description: string;
  vedha: { has_vedha: boolean; description: string };
  manglik_dosha: { bride: any; groom: any; both_manglik_cancellation: boolean };
  navamsa_compatibility: any;
  lagna_analysis: any;
  south_indian_poruthams?: any;
  dasha_compatibility?: any;
  warnings: string[];
  conclusion: string;
}
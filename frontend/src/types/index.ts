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
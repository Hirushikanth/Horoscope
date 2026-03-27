import { create } from 'zustand';
import { type HoroscopeResponse, type BirthData, type MatchingInput, type MatchingResponse } from '../types';

interface AppState {
  mode: 'horoscope' | 'matching';
  setMode: (mode: 'horoscope' | 'matching') => void;

  birthData: BirthData | null;
  horoscopeData: HoroscopeResponse | null;
  setHoroscopeData: (data: HoroscopeResponse, birthData: BirthData) => void;

  matchingInput: MatchingInput | null;
  matchingData: MatchingResponse | null;
  setMatchingData: (data: MatchingResponse, input: MatchingInput) => void;

  reset: () => void;
}

export const useAppStore = create<AppState>((set) => ({
  mode: 'horoscope',
  setMode: (mode) => set({ mode }),

  birthData: null,
  horoscopeData: null,
  setHoroscopeData: (horoscopeData, birthData) => set({ horoscopeData, birthData }),

  matchingInput: null,
  matchingData: null,
  setMatchingData: (matchingData, matchingInput) => set({ matchingData, matchingInput }),

  reset: () => set({ 
    horoscopeData: null, 
    birthData: null,
    matchingData: null,
    matchingInput: null 
  }),
}));
import { create } from 'zustand';
import type {
  BirthRequest,
  JathakamResponse,
  MatchingRequest,
  MatchingResponse,
  PanchangamResponse,
} from '../types';

interface AppState {
  mode: 'horoscope' | 'matching';
  setMode: (mode: 'horoscope' | 'matching') => void;

  birthData: BirthRequest | null;
  horoscopeData: JathakamResponse | null;
  panchangamData: PanchangamResponse | null;
  setHoroscopeData: (data: JathakamResponse, birthData: BirthRequest) => void;
  setPanchangamData: (data: PanchangamResponse | null) => void;

  matchingInput: MatchingRequest | null;
  matchingData: MatchingResponse | null;
  setMatchingData: (data: MatchingResponse, input: MatchingRequest) => void;

  reset: () => void;
}

export const useAppStore = create<AppState>((set) => ({
  mode: 'horoscope',
  setMode: (mode) => set({ mode }),

  birthData: null,
  horoscopeData: null,
  panchangamData: null,
  setHoroscopeData: (horoscopeData, birthData) => set({ horoscopeData, birthData }),
  setPanchangamData: (panchangamData) => set({ panchangamData }),

  matchingInput: null,
  matchingData: null,
  setMatchingData: (matchingData, matchingInput) => set({ matchingData, matchingInput }),

  reset: () => set({
    horoscopeData: null,
    birthData: null,
    panchangamData: null,
    matchingData: null,
    matchingInput: null,
  }),
}));

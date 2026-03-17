import { create } from 'zustand';
import { type HoroscopeResponse, type BirthData } from '../types';

interface AppState {
  birthData: BirthData | null;
  horoscopeData: HoroscopeResponse | null;
  setHoroscopeData: (data: HoroscopeResponse, birthData: BirthData) => void;
  reset: () => void;
}

export const useAppStore = create<AppState>((set) => ({
  birthData: null,
  horoscopeData: null,
  setHoroscopeData: (horoscopeData, birthData) => set({ horoscopeData, birthData }),
  reset: () => set({ horoscopeData: null, birthData: null }),
}));
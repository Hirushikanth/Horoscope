import axios from 'axios';
import { type BirthData, type HoroscopeResponse } from '../types';

const api = axios.create({
  baseURL: 'http://localhost:8000/api',
  headers: {
    'Content-Type': 'application/json',
  },
});

export const fetchHoroscope = async (data: BirthData): Promise<HoroscopeResponse> => {
  const response = await api.post('/horoscope', data);
  return response.data;
};
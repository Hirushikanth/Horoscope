import axios from 'axios';
import type {
  BirthRequest,
  DashaOptions,
  DashaResponse,
  HealthResponse,
  JathakamResponse,
  MatchingRequest,
  MatchingResponse,
  MetaResponse,
  PanchangamResponse,
  StarsResponse,
  VargasResponse,
} from '../types';

const api = axios.create({
  baseURL: 'http://localhost:8000/api/v2',
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 60_000,
});

export const fetchMeta = async (): Promise<MetaResponse> => {
  const response = await api.get('/meta');
  return response.data;
};

export const fetchHealth = async (): Promise<HealthResponse> => {
  const response = await api.get('/health');
  return response.data;
};

export const fetchJathakam = async (data: BirthRequest): Promise<JathakamResponse> => {
  const response = await api.post('/jathakam', data);
  return response.data;
};

export const fetchPanchangam = async (data: BirthRequest): Promise<PanchangamResponse> => {
  const response = await api.post('/jathakam/panchangam', data);
  return response.data;
};

export const fetchDasha = async (
  data: BirthRequest,
  options?: DashaOptions,
): Promise<DashaResponse> => {
  const response = await api.post('/jathakam/dasha', { ...data, ...options });
  return response.data;
};

export const fetchVargas = async (
  data: BirthRequest,
  vargas: string[] = ['D9'],
): Promise<VargasResponse> => {
  const response = await api.post('/jathakam/vargas', { ...data, vargas });
  return response.data;
};

export const fetchMatching = async (data: MatchingRequest): Promise<MatchingResponse> => {
  const response = await api.post('/matching', data);
  return response.data;
};

export const fetchStars = async (data: BirthRequest): Promise<StarsResponse> => {
  const response = await api.post('/stars', data);
  return response.data;
};

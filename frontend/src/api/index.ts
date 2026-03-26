import axios from 'axios';

const api = axios.create({
  baseURL: '/api',
});

export const runKing = async (matrix: number[][]) => {
  const res = await api.post('/king', { matrix });
  return res.data;
};

export const runChaining = async (matrix: number[][]) => {
  const res = await api.post('/chaining', { matrix });
  return res.data;
};

export const runAnalyze = async (matrix: number[][], groups: Record<number, number>, routing?: number[][]) => {
  const res = await api.post('/analyze', { matrix, groups, routing });
  return res.data;
};

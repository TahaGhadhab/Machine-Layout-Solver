import { create } from 'zustand';
import { runKing, runChaining, runAnalyze } from '../api';

interface MatrixState {
  matrix: number[][];
  rows: number;
  cols: number;
  results: any;
  loading: boolean;
  activeMethod: 'king' | 'chaining' | null;
  
  setMatrixSize: (rows: number, cols: number) => void;
  updateCell: (r: number, c: number, val: number) => void;
  randomizeMatrix: () => void;
  clearMatrix: () => void;
  
  solveKing: () => Promise<void>;
  solveChaining: () => Promise<void>;
}

export const useMatrixStore = create<MatrixState>((set, get) => ({
  matrix: Array(6).fill(0).map(() => Array(6).fill(0)),
  rows: 6,
  cols: 6,
  results: null,
  loading: false,
  activeMethod: null,

  setMatrixSize: (rows, cols) => {
    const current = get().matrix;
    const newMatrix = Array(rows).fill(0).map((_, r) =>
      Array(cols).fill(0).map((_, c) => (current[r] && current[r][c] !== undefined ? current[r][c] : 0))
    );
    set({
      rows, cols,
      matrix: newMatrix,
      results: null,
      activeMethod: null
    });
  },

  updateCell: (r, c, val) => {
    const newMatrix = [...get().matrix];
    newMatrix[r] = [...newMatrix[r]];
    newMatrix[r][c] = val;
    set({ matrix: newMatrix, results: null });
  },

  randomizeMatrix: () => {
    const { rows, cols } = get();
    const newMatrix = Array(rows).fill(0).map(() =>
      Array(cols).fill(0).map(() => (Math.random() > 0.7 ? 1 : 0))
    );
    set({ matrix: newMatrix, results: null, activeMethod: null });
  },

  clearMatrix: () => {
    const { rows, cols } = get();
    set({ 
      matrix: Array(rows).fill(0).map(() => Array(cols).fill(0)),
      results: null,
      activeMethod: null 
    });
  },

  solveKing: async () => {
    set({ loading: true, activeMethod: 'king' });
    try {
      const { matrix } = get();
      const res = await runKing(matrix);
      set({ results: res, loading: false });
    } catch (e) {
      console.error(e);
      set({ loading: false });
    }
  },

  solveChaining: async () => {
    set({ loading: true, activeMethod: 'chaining' });
    try {
      const { matrix } = get();
      const chainRes = await runChaining(matrix);
      const analysisRes = await runAnalyze(matrix, chainRes.groups);
      set({ results: { ...chainRes, ...analysisRes }, loading: false });
    } catch (e) {
      console.error(e);
      set({ loading: false });
    }
  }
}));

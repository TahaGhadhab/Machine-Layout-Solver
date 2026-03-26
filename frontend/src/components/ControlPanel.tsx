import React from 'react';
import { useMatrixStore } from '../store/useMatrixStore';
import { RefreshCw, Play, Trash2 } from 'lucide-react';

export const ControlPanel: React.FC = () => {
  const { randomizeMatrix, clearMatrix, solveKing, solveChaining, loading } = useMatrixStore();

  return (
    <div className="glass-card p-6 flex flex-col gap-4">
      <h2 className="text-xl font-semibold text-slate-800 dark:text-slate-100">Controls</h2>
      
      <div className="flex gap-2">
        <button
          onClick={randomizeMatrix}
          className="flex-1 flex items-center justify-center gap-2 bg-slate-100 hover:bg-slate-200 dark:bg-slate-800 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-200 py-2 px-4 rounded-lg transition-colors text-sm font-medium"
        >
          <RefreshCw size={16} /> Randomize
        </button>
        <button
          onClick={clearMatrix}
          className="flex-1 flex items-center justify-center gap-2 bg-rose-50 hover:bg-rose-100 dark:bg-rose-900/20 dark:hover:bg-rose-900/40 text-rose-600 dark:text-rose-400 py-2 px-4 rounded-lg transition-colors text-sm font-medium"
        >
          <Trash2 size={16} /> Clear
        </button>
      </div>

      <div className="h-px bg-slate-200 dark:bg-slate-700 my-2" />
      
      <button
        onClick={solveKing}
        disabled={loading}
        className="w-full flex items-center justify-center gap-2 bg-gradient-to-r from-brand-600 to-brand-500 hover:from-brand-500 hover:to-brand-400 text-white py-3 px-4 rounded-lg shadow-md hover:shadow-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed font-medium"
      >
        <Play size={18} /> Solve with King's Method
      </button>

      <button
        onClick={solveChaining}
        disabled={loading}
        className="w-full flex items-center justify-center gap-2 bg-gradient-to-r from-cyan-600 to-cyan-500 hover:from-cyan-500 hover:to-cyan-400 text-white py-3 px-4 rounded-lg shadow-md hover:shadow-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed font-medium"
      >
        <Play size={18} /> Solve with Chaining Method
      </button>
    </div>
  );
};

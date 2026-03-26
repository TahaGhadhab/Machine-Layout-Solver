import React from 'react';
import { useMatrixStore } from '../store/useMatrixStore';
import { Plus, Minus } from 'lucide-react';

export const MatrixEditor: React.FC = () => {
  const { matrix, rows, cols, setMatrixSize, updateCell } = useMatrixStore();

  return (
    <div className="glass-card p-6 flex flex-col items-center">
      <h2 className="text-xl font-semibold mb-4 text-slate-800 dark:text-slate-100 text-center">Machine-Part Matrix</h2>
      
      <div className="flex gap-6 mb-6">
        <div className="flex items-center gap-2">
          <span className="text-sm text-slate-600 dark:text-slate-300">Parts</span>
          <button onClick={() => setMatrixSize(Math.max(2, rows - 1), cols)} className="p-1 rounded bg-slate-100 hover:bg-slate-200 dark:bg-slate-800 dark:hover:bg-slate-700">
            <Minus size={16} />
          </button>
          <span className="w-6 text-center">{rows}</span>
          <button onClick={() => setMatrixSize(Math.min(20, rows + 1), cols)} className="p-1 rounded bg-slate-100 hover:bg-slate-200 dark:bg-slate-800 dark:hover:bg-slate-700">
            <Plus size={16} />
          </button>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-sm text-slate-600 dark:text-slate-300">Machines</span>
          <button onClick={() => setMatrixSize(rows, Math.max(2, cols - 1))} className="p-1 rounded bg-slate-100 hover:bg-slate-200 dark:bg-slate-800 dark:hover:bg-slate-700">
            <Minus size={16} />
          </button>
          <span className="w-6 text-center">{cols}</span>
          <button onClick={() => setMatrixSize(rows, Math.min(20, cols + 1))} className="p-1 rounded bg-slate-100 hover:bg-slate-200 dark:bg-slate-800 dark:hover:bg-slate-700">
            <Plus size={16} />
          </button>
        </div>
      </div>

      <div className="overflow-auto max-w-full pb-4">
        <table className="border-collapse">
          <thead>
            <tr>
              <th className="p-2 border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-xs text-slate-500">P \ M</th>
              {Array.from({ length: cols }).map((_, c) => (
                <th key={c} className="p-2 min-w-10 border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-sm font-medium">M{c + 1}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {matrix.map((row, r) => (
              <tr key={r}>
                <td className="p-2 border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-sm font-medium">P{r + 1}</td>
                {row.map((val, c) => (
                  <td key={c} className="p-0 border border-slate-200 dark:border-slate-700 relative">
                    <button
                      className={`w-10 h-10 flex items-center justify-center text-sm transition-colors duration-200 ${val === 1 ? 'bg-brand-500 text-white font-bold' : 'bg-transparent text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800/50'}`}
                      onClick={() => updateCell(r, c, val === 1 ? 0 : 1)}
                    >
                      {val === 1 ? '1' : ''}
                    </button>
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

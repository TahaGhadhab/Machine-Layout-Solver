import React from 'react';

interface Props {
  matrix: number[][];
  rowIndices: number[];
  colIndices: number[];
}

export const MatrixGrid: React.FC<Props> = ({ matrix, rowIndices, colIndices }) => {
  if (!matrix || matrix.length === 0) return null;

  return (
    <div className="overflow-auto max-w-full">
      <table className="border-collapse mx-auto">
        <thead>
          <tr>
            <th className="p-2 border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-xs text-slate-500">P \ M</th>
            {colIndices.map((c) => (
              <th key={c} className="p-2 min-w-10 border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-sm font-medium">M{c + 1}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {matrix.map((row, r) => (
            <tr key={r}>
              <td className="p-2 border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-sm font-medium">P{rowIndices[r] + 1}</td>
              {row.map((val, c) => (
                <td key={c} className="p-0 border border-slate-200 dark:border-slate-700 relative">
                  <div className={`w-10 h-10 flex items-center justify-center text-sm ${val === 1 ? 'bg-brand-500 text-white font-bold' : 'bg-transparent text-slate-200 dark:text-slate-800'}`}>
                    {val === 1 ? '1' : ''}
                  </div>
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

import React from 'react';

interface Props {
  matrix: number[][];
}

export const TriangularSchema: React.FC<Props> = ({ matrix }) => {
  if (!matrix || matrix.length === 0) return null;
  const size = matrix.length;
  
  return (
    <div className="overflow-auto max-w-full p-4 flex justify-center">
      <table className="border-collapse">
        <tbody>
          <tr>
            <td className="w-10 h-10 border-0"></td>
            {Array.from({ length: size }).map((_, c) => (
              <td key={`h-${c}`} className="w-10 h-10 border-0 text-center text-xs font-semibold text-slate-500">M{c + 1}</td>
            ))}
          </tr>
          {Array.from({ length: size }).map((_, r) => (
            <tr key={r}>
              <td className="w-10 h-10 border-0 text-right pr-2 text-xs font-semibold text-slate-500">M{r + 1}</td>
              {Array.from({ length: size }).map((_, c) => {
                if (c <= r) {
                  return <td key={c} className="w-10 h-10 border-0"></td>;
                }
                const val = matrix[r][c];
                let bgClass = "bg-slate-100 dark:bg-slate-800/50";
                if (val >= 2) bgClass = "bg-rose-500 text-white"; // strong = red
                else if (val === 1) bgClass = "bg-amber-400 text-amber-900"; // weak = yellow
                
                return (
                  <td key={c} className={`w-10 h-10 border border-slate-200 dark:border-slate-700 text-center text-sm font-semibold transition-colors ${bgClass}`}>
                    {val > 0 ? val : ''}
                  </td>
                );
              })}
            </tr>
          ))}
        </tbody>
      </table>
      
      <div className="ml-8 flex flex-col justify-center gap-3 text-sm">
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 bg-rose-500 rounded-sm"></div>
          <span className="text-slate-600 dark:text-slate-400">Strong Link (&ge;2)</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 bg-amber-400 rounded-sm"></div>
          <span className="text-slate-600 dark:text-slate-400">Weak Link (1)</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 bg-slate-100 dark:bg-slate-800 rounded-sm border border-slate-200 dark:border-slate-700"></div>
          <span className="text-slate-600 dark:text-slate-400">No Link (0)</span>
        </div>
      </div>
    </div>
  );
};

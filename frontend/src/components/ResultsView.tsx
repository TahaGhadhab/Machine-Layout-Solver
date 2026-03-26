import React, { useState } from 'react';
import { useMatrixStore } from '../store/useMatrixStore';
import { MatrixGrid } from '../visualizations/MatrixGrid';
import { TriangularSchema } from '../visualizations/TriangularSchema';
import { GraphView } from '../visualizations/GraphView';

export const ResultsView: React.FC = () => {
  const { results, activeMethod, loading } = useMatrixStore();
  const [activeTab, setActiveTab] = useState<'matrix' | 'triangular' | 'graph'>('matrix');

  if (loading) {
    return (
      <div className="glass-card p-12 flex flex-col items-center justify-center animate-pulse min-h-[400px]">
        <div className="w-12 h-12 border-4 border-brand-500 border-t-transparent rounded-full animate-spin mb-4"></div>
        <p className="text-slate-500 dark:text-slate-400">Processing matrix...</p>
      </div>
    );
  }

  if (!results) {
    return (
      <div className="glass-card p-12 flex flex-col items-center justify-center text-center text-slate-500 dark:text-slate-400 min-h-[400px]">
        <div className="text-4xl mb-4 opacity-50">📊</div>
        <p className="text-lg font-medium text-slate-700 dark:text-slate-300">No results yet</p>
        <p className="text-sm">Run an algorithm to see the layout analysis here.</p>
      </div>
    );
  }

  return (
    <div className="glass-card p-6 flex flex-col h-full">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-xl font-semibold text-slate-800 dark:text-slate-100">
          Analysis Results ({activeMethod === 'king' ? "King's Method" : "Chaining Method"})
        </h2>
        {results.iterations !== undefined && (
          <span className="text-sm bg-brand-100 text-brand-700 dark:bg-brand-900/40 dark:text-brand-300 px-3 py-1 rounded-full border border-brand-200 dark:border-brand-800/50">
            Stable after {results.iterations} iterations
          </span>
        )}
      </div>

      <div className="flex border-b border-slate-200 dark:border-slate-700 mb-6 overflow-x-auto hide-scrollbar">
        <button
          className={`px-4 py-2 text-sm font-medium border-b-2 transition-colors whitespace-nowrap ${activeTab === 'matrix' ? 'border-brand-500 text-brand-600 dark:text-brand-400' : 'border-transparent text-slate-500 hover:text-slate-700 dark:hover:text-slate-300'}`}
          onClick={() => setActiveTab('matrix')}
        >
          Matrix View
        </button>
        {activeMethod === 'chaining' && (
          <>
            <button
              className={`px-4 py-2 text-sm font-medium border-b-2 transition-colors whitespace-nowrap ${activeTab === 'triangular' ? 'border-brand-500 text-brand-600 dark:text-brand-400' : 'border-transparent text-slate-500 hover:text-slate-700 dark:hover:text-slate-300'}`}
              onClick={() => setActiveTab('triangular')}
            >
              Triangular Schema
            </button>
            <button
              className={`px-4 py-2 text-sm font-medium border-b-2 transition-colors whitespace-nowrap ${activeTab === 'graph' ? 'border-brand-500 text-brand-600 dark:text-brand-400' : 'border-transparent text-slate-500 hover:text-slate-700 dark:hover:text-slate-300'}`}
              onClick={() => setActiveTab('graph')}
            >
              Graph View
            </button>
          </>
        )}
      </div>

      <div className="bg-slate-50/50 dark:bg-slate-900/50 rounded-xl p-4 flex-1 flex flex-col items-center justify-center border border-slate-100 dark:border-slate-800/50 overflow-hidden">
        {activeTab === 'matrix' && activeMethod === 'king' && (
          <MatrixGrid matrix={results.ordered_matrix} rowIndices={results.row_indices} colIndices={results.col_indices} />
        )}
        {activeTab === 'matrix' && activeMethod === 'chaining' && (
          <div className="w-full text-left">
             <div className="grid grid-cols-2 gap-4 mb-4">
                <div className="bg-white dark:bg-slate-800 p-4 rounded-lg shadow-sm border border-slate-100 dark:border-slate-700">
                  <h3 className="text-xs text-slate-500 uppercase font-semibold mb-2">Efficiency Score</h3>
                  <p className="text-3xl font-light text-brand-600 dark:text-brand-400">{((results.efficiency || 0) * 100).toFixed(1)}%</p>
                </div>
                <div className="bg-white dark:bg-slate-800 p-4 rounded-lg shadow-sm border border-slate-100 dark:border-slate-700">
                  <h3 className="text-xs text-slate-500 uppercase font-semibold mb-2">Crossing Flows</h3>
                  <p className="text-3xl font-light text-rose-500">{results.crossing_flows || 0}</p>
                </div>
             </div>
             
             <div className="bg-white dark:bg-slate-800 p-4 rounded-lg shadow-sm border border-slate-100 dark:border-slate-700 max-h-60 overflow-auto">
                <h3 className="text-sm font-semibold mb-2 text-slate-700 dark:text-slate-300">Machine Grouping</h3>
                <div className="flex gap-2 flex-wrap">
                  {Object.entries(results.groups || {}).map(([m, g]) => (
                    <div key={m} className={`px-3 py-1 rounded text-sm font-medium border bg-brand-50 dark:bg-brand-900/20 text-brand-700 dark:text-brand-300 border-brand-200 dark:border-brand-800`}>
                      M{parseInt(m) + 1} &rarr; Cell {g as React.ReactNode}
                    </div>
                  ))}
                </div>
             </div>
          </div>
        )}
        {activeTab === 'triangular' && activeMethod === 'chaining' && results.link_matrix && (
          <TriangularSchema matrix={results.link_matrix} />
        )}
        {activeTab === 'graph' && activeMethod === 'chaining' && results.link_matrix && results.groups && (
          <GraphView matrix={results.link_matrix} groups={results.groups} />
        )}
      </div>
    </div>
  );
};

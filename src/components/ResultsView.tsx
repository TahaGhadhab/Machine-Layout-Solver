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

  // Normalise field names
  // API returns: reordered_matrix / row_order / col_order
  // Old code expected: ordered_matrix / row_indices / col_indices
  const reorderedMatrix = results.reordered_matrix ?? results.ordered_matrix;
  const rowOrder        = results.row_order        ?? results.row_indices ?? [];
  const colOrder        = results.col_order        ?? results.col_indices ?? [];

  const efficiency      = results.efficiency ?? 0;
  const crossingFlows   = Array.isArray(results.crossing_flows)
    ? results.crossing_flows.length
    : (results.crossing_flows ?? 0);
  const exceptionalParts: number[] = results.exceptional_parts ?? [];
  const groups          = results.groups ?? {};
  const cellsSummary    = results.cells_summary ?? {};

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

      {/* Tabs */}
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

      {/* Tab content */}
      <div className="bg-slate-50/50 dark:bg-slate-900/50 rounded-xl p-4 flex-1 flex flex-col items-center justify-center border border-slate-100 dark:border-slate-800/50 overflow-hidden">

        {/* KING - Matrix View */}
        {activeTab === 'matrix' && activeMethod === 'king' && (
          <div className="w-full">
            <div className="grid grid-cols-3 gap-4 mb-4">
              <div className="bg-white dark:bg-slate-800 p-4 rounded-lg shadow-sm border border-slate-100 dark:border-slate-700">
                <h3 className="text-xs text-slate-500 uppercase font-semibold mb-2">Efficiency Score</h3>
                <p className="text-3xl font-light text-brand-600 dark:text-brand-400">
                  {(efficiency * 100).toFixed(1)}%
                </p>
              </div>
              <div className="bg-white dark:bg-slate-800 p-4 rounded-lg shadow-sm border border-slate-100 dark:border-slate-700">
                <h3 className="text-xs text-slate-500 uppercase font-semibold mb-2">Cells Detected</h3>
                <p className="text-3xl font-light text-emerald-500">
                  {Object.keys(cellsSummary).length}
                </p>
              </div>
              <div className="bg-white dark:bg-slate-800 p-4 rounded-lg shadow-sm border border-slate-100 dark:border-slate-700">
                <h3 className="text-xs text-slate-500 uppercase font-semibold mb-2">Exceptional Parts</h3>
                <p className="text-3xl font-light text-rose-500">
                  {exceptionalParts.length}
                </p>
              </div>
            </div>

            {reorderedMatrix ? (
              <div className="bg-white dark:bg-slate-800 p-4 rounded-lg shadow-sm border border-slate-100 dark:border-slate-700 mb-4 overflow-auto">
                <h3 className="text-sm font-semibold mb-3 text-slate-700 dark:text-slate-300">
                  Reordered Matrix
                  <span className="ml-2 text-xs font-normal text-slate-400">
                    (rows: machines in order {rowOrder.map((r: number) => `M${r + 1}`).join(' → ')})
                  </span>
                </h3>
                <MatrixGrid
                  matrix={reorderedMatrix}
                  rowIndices={rowOrder}
                  colIndices={colOrder}
                />
              </div>
            ) : (
              <p className="text-slate-400 text-sm">No reordered matrix returned.</p>
            )}

            <div className="bg-white dark:bg-slate-800 p-4 rounded-lg shadow-sm border border-slate-100 dark:border-slate-700 mb-4">
              <h3 className="text-sm font-semibold mb-2 text-slate-700 dark:text-slate-300">Machine Cells</h3>
              <div className="flex gap-2 flex-wrap">
                {Object.entries(groups).map(([m, g]) => (
                  <div
                    key={m}
                    className="px-3 py-1 rounded text-sm font-medium border bg-brand-50 dark:bg-brand-900/20 text-brand-700 dark:text-brand-300 border-brand-200 dark:border-brand-800"
                  >
                    M{parseInt(m) + 1} → Cell {g as React.ReactNode}
                  </div>
                ))}
              </div>
            </div>

            {exceptionalParts.length > 0 && (
              <div className="bg-white dark:bg-slate-800 p-4 rounded-lg shadow-sm border border-rose-100 dark:border-rose-900/40">
                <h3 className="text-sm font-semibold mb-2 text-rose-600 dark:text-rose-400">
                  Exceptional Parts (Hors Trame)
                </h3>
                <div className="flex gap-2 flex-wrap">
                  {exceptionalParts.map((p: number) => (
                    <div
                      key={p}
                      className="px-3 py-1 rounded text-sm font-medium border bg-rose-50 dark:bg-rose-900/20 text-rose-700 dark:text-rose-300 border-rose-200 dark:border-rose-800"
                    >
                      P{p + 1}
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {/* CHAINING - Matrix View */}
        {activeTab === 'matrix' && activeMethod === 'chaining' && (
          <div className="w-full text-left">
            <div className="grid grid-cols-2 gap-4 mb-4">
              <div className="bg-white dark:bg-slate-800 p-4 rounded-lg shadow-sm border border-slate-100 dark:border-slate-700">
                <h3 className="text-xs text-slate-500 uppercase font-semibold mb-2">Efficiency Score</h3>
                <p className="text-3xl font-light text-brand-600 dark:text-brand-400">
                  {(efficiency * 100).toFixed(1)}%
                </p>
              </div>
              <div className="bg-white dark:bg-slate-800 p-4 rounded-lg shadow-sm border border-slate-100 dark:border-slate-700">
                <h3 className="text-xs text-slate-500 uppercase font-semibold mb-2">Crossing Flows</h3>
                <p className="text-3xl font-light text-rose-500">{crossingFlows}</p>
              </div>
            </div>

            <div className="bg-white dark:bg-slate-800 p-4 rounded-lg shadow-sm border border-slate-100 dark:border-slate-700 max-h-60 overflow-auto">
              <h3 className="text-sm font-semibold mb-2 text-slate-700 dark:text-slate-300">Machine Grouping</h3>
              <div className="flex gap-2 flex-wrap">
                {Object.entries(groups).map(([m, g]) => (
                  <div
                    key={m}
                    className="px-3 py-1 rounded text-sm font-medium border bg-brand-50 dark:bg-brand-900/20 text-brand-700 dark:text-brand-300 border-brand-200 dark:border-brand-800"
                  >
                    M{parseInt(m) + 1} → Cell {g as React.ReactNode}
                  </div>
                ))}
              </div>
            </div>

            {exceptionalParts.length > 0 && (
              <div className="bg-white dark:bg-slate-800 p-4 rounded-lg shadow-sm border border-rose-100 dark:border-rose-900/40 mt-4">
                <h3 className="text-sm font-semibold mb-2 text-rose-600 dark:text-rose-400">
                  Exceptional Parts (Hors Trame)
                </h3>
                <div className="flex gap-2 flex-wrap">
                  {exceptionalParts.map((p: number) => (
                    <div
                      key={p}
                      className="px-3 py-1 rounded text-sm font-medium border bg-rose-50 dark:bg-rose-900/20 text-rose-700 dark:text-rose-300 border-rose-200 dark:border-rose-800"
                    >
                      P{p + 1}
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {/* Triangular schema */}
        {activeTab === 'triangular' && activeMethod === 'chaining' && results.link_matrix && (
          <TriangularSchema matrix={results.link_matrix} />
        )}

        {/* Graph view */}
        {activeTab === 'graph' && activeMethod === 'chaining' && results.link_matrix && groups && (
          <GraphView matrix={results.link_matrix} groups={groups} />
        )}
      </div>
    </div>
  );
};

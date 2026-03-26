import React from 'react';
import { MatrixEditor } from './components/MatrixEditor';
import { ControlPanel } from './components/ControlPanel';
import { ResultsView } from './components/ResultsView';

function App() {
  return (
    <div className="min-h-screen pt-8 pb-16 px-4 md:px-8">
      <div className="max-w-6xl mx-auto space-y-8 text-left">
        <header className="text-center mb-12">
          <h1 className="text-4xl md:text-5xl font-bold mb-4 tracking-tight">
            Machine Layout <span className="text-gradient">Solver</span>
          </h1>
          <p className="text-slate-600 dark:text-slate-400 max-w-2xl mx-auto text-lg">
            Solve cell formation problems using King's method and the Chaining method. 
            Identify machine cells, exceptional elements, and optimize your production flows.
          </p>
        </header>

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          <div className="lg:col-span-4 space-y-6">
            <ControlPanel />
          </div>
          <div className="lg:col-span-8">
            <MatrixEditor />
          </div>
        </div>

        <div className="mt-8">
          <ResultsView />
        </div>
      </div>
    </div>
  );
}

export default App;

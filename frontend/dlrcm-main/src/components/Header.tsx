import { Brain, Shield, TrendingUp, Settings } from 'lucide-react';
import { Navigation } from './Navigation';

export function Header() {
  return (
    <header className="bg-slate-900/95 backdrop-blur-sm border-b border-slate-800/60 sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="relative">
              <Brain className="w-8 h-8 text-blue-400" />
              <div className="absolute -top-1 -right-1 w-3 h-3 bg-green-400 rounded-full animate-pulse"></div>
            </div>
            <div>
              <h1 className="text-xl font-bold text-white">AI Risk Analyzer</h1>
              <p className="text-xs text-slate-400">Denial Prevention Intelligence</p>
            </div>
          </div>
          
          <Navigation />
        </div>
      </div>
    </header>
  );
}
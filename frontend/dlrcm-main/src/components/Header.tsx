import { Bell, User } from 'lucide-react';
import { Navigation } from './Navigation';
import { Logo } from './Logo';

export function Header() {
  return (
    <header className="bg-white shadow-sm border-b border-slate-200 sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <Logo size="lg" showStatusIndicator={true} />
            <div>
              <h1 className="text-2xl font-bold text-slate-900">MedTechAi Risk Analyzer</h1>
              <p className="text-sm text-slate-600 font-medium">Enterprise Healthcare Intelligence Platform</p>
            </div>
          </div>
          
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-3">
              {/* Status indicator */}
              <div className="flex items-center space-x-2 px-3 py-1 bg-emerald-50 text-emerald-700 rounded-full text-sm">
                <div className="w-2 h-2 bg-emerald-500 rounded-full animate-pulse"></div>
                <span className="font-medium">All Systems Operational</span>
              </div>
              
              {/* Notifications */}
              <button className="relative p-2 text-slate-600 hover:text-slate-900 hover:bg-slate-100 rounded-lg transition-colors">
                <Bell className="w-5 h-5" />
                <span className="absolute -top-1 -right-1 w-4 h-4 bg-red-500 text-white text-xs rounded-full flex items-center justify-center">3</span>
          </button>
              
              {/* User menu */}
              <button className="flex items-center space-x-2 p-2 text-slate-600 hover:text-slate-900 hover:bg-slate-100 rounded-lg transition-colors">
                <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-blue-600 rounded-full flex items-center justify-center">
                  <User className="w-4 h-4 text-white" />
                </div>
                <div className="text-left">
                  <div className="text-sm font-medium text-slate-900">Dr. Johnson</div>
                  <div className="text-xs text-slate-500">Administrator</div>
                </div>
              </button>
            </div>
            
            <Navigation />
          </div>
        </div>
      </div>
    </header>
  );
}
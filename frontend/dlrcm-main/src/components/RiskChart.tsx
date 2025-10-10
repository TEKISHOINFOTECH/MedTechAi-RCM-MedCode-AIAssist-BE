import { BarChart3 } from 'lucide-react';

export function RiskChart() {
  const data = [
    { month: 'Jan', denials: 15, approvals: 85 },
    { month: 'Feb', denials: 12, approvals: 88 },
    { month: 'Mar', denials: 18, approvals: 82 },
    { month: 'Apr', denials: 14, approvals: 86 },
    { month: 'May', denials: 10, approvals: 90 },
    { month: 'Jun', denials: 8, approvals: 92 }
  ];

  const maxValue = Math.max(...data.map(d => d.denials + d.approvals));

  return (
    <div className="glass-card p-6">
      <div className="flex items-center justify-between mb-8">
        <h3 className="text-xl font-bold text-slate-800 flex items-center space-x-3">
          <div className="p-2 rounded-xl bg-gradient-to-br from-blue-500/20 to-cyan-500/10 border border-blue-400/30">
            <BarChart3 className="w-5 h-5 text-blue-600" />
          </div>
          <span>Denial Trends</span>
        </h3>
        <div className="flex items-center space-x-6 text-sm">
          <div className="flex items-center space-x-2">
            <div className="w-3 h-3 bg-gradient-to-r from-red-400 to-red-500 rounded-full"></div>
            <span className="text-slate-700 font-medium">Denials</span>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-3 h-3 bg-gradient-to-r from-green-400 to-emerald-500 rounded-full"></div>
            <span className="text-slate-700 font-medium">Approvals</span>
          </div>
        </div>
      </div>

      <div className="flex items-end justify-between h-48 space-x-3">
        {data.map((item, index) => (
          <div key={index} className="flex flex-col items-center flex-1">
            <div className="flex flex-col items-center justify-end h-40 w-full space-y-1">
              <div
                className="w-full bg-green-500/80 rounded-t transition-all duration-700 hover:bg-green-500"
                style={{ height: `${(item.approvals / maxValue) * 160}px` }}
              ></div>
              <div
                className="w-full bg-red-500/80 rounded-b transition-all duration-700 hover:bg-red-500"
                style={{ height: `${(item.denials / maxValue) * 160}px` }}
              ></div>
            </div>
            <span className="text-xs text-slate-600 mt-2">{item.month}</span>
          </div>
        ))}
      </div>

      <div className="mt-8 grid grid-cols-3 gap-6 pt-6 border-t border-white/20">
        <div className="text-center">
          <p className="text-2xl font-bold text-slate-900">8.2%</p>
          <p className="text-xs text-slate-700 font-medium">Current Rate</p>
        </div>
        <div className="text-center">
          <p className="text-2xl font-bold text-emerald-600">-47%</p>
          <p className="text-xs text-slate-700 font-medium">vs Last Quarter</p>
        </div>
        <div className="text-center">
          <p className="text-2xl font-bold text-slate-900">$2.1M</p>
          <p className="text-xs text-slate-700 font-medium">Saved</p>
        </div>
      </div>
    </div>
  );
}
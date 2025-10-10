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
    <div className="bg-slate-800/50 backdrop-blur-sm rounded-xl border border-slate-700/50 p-6">
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-lg font-semibold text-white flex items-center space-x-2">
          <BarChart3 className="w-5 h-5 text-blue-400" />
          <span>Denial Trends</span>
        </h3>
        <div className="flex items-center space-x-4 text-sm">
          <div className="flex items-center space-x-2">
            <div className="w-3 h-3 bg-red-400 rounded-full"></div>
            <span className="text-slate-300">Denials</span>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-3 h-3 bg-green-400 rounded-full"></div>
            <span className="text-slate-300">Approvals</span>
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
            <span className="text-xs text-slate-400 mt-2">{item.month}</span>
          </div>
        ))}
      </div>

      <div className="mt-6 grid grid-cols-3 gap-4 pt-4 border-t border-slate-700/50">
        <div className="text-center">
          <p className="text-xl font-bold text-white">8.2%</p>
          <p className="text-xs text-slate-400">Current Rate</p>
        </div>
        <div className="text-center">
          <p className="text-xl font-bold text-green-400">-47%</p>
          <p className="text-xs text-slate-400">vs Last Quarter</p>
        </div>
        <div className="text-center">
          <p className="text-xl font-bold text-blue-400">$2.1M</p>
          <p className="text-xs text-slate-400">Saved</p>
        </div>
      </div>
    </div>
  );
}
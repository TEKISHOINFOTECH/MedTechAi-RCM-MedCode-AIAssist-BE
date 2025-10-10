import { AlertTriangle, CheckCircle, XCircle, TrendingUp } from 'lucide-react';

interface RiskCardProps {
  title: string;
  score: number;
  trend: 'up' | 'down' | 'stable';
  description: string;
  lastUpdated: string;
}

export function RiskCard({ title, score, trend, description, lastUpdated }: RiskCardProps) {
  const getRiskLevel = (score: number) => {
    if (score >= 80) return { level: 'high', color: 'red', icon: XCircle };
    if (score >= 50) return { level: 'medium', color: 'yellow', icon: AlertTriangle };
    return { level: 'low', color: 'green', icon: CheckCircle };
  };

  const risk = getRiskLevel(score);
  const Icon = risk.icon;

  const getTrendColor = () => {
    if (trend === 'up') return 'text-red-400';
    if (trend === 'down') return 'text-green-400';
    return 'text-slate-400';
  };

  return (
    <div className="bg-slate-800/50 backdrop-blur-sm rounded-xl border border-slate-700/50 p-6 hover:border-slate-600/50 transition-all duration-300 hover:shadow-lg hover:shadow-blue-500/10">
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center space-x-3">
          <Icon className={`w-5 h-5 text-${risk.color}-400`} />
          <h3 className="font-semibold text-white">{title}</h3>
        </div>
        <div className={`flex items-center space-x-1 ${getTrendColor()}`}>
          <TrendingUp className={`w-4 h-4 ${trend === 'down' ? 'rotate-180' : ''}`} />
          <span className="text-sm font-medium">{trend}</span>
        </div>
      </div>

      <div className="mb-4">
        <div className="flex items-end space-x-2 mb-2">
          <span className="text-3xl font-bold text-white">{score}</span>
          <span className="text-slate-400 text-sm mb-1">/ 100</span>
        </div>
        <div className="w-full bg-slate-700 rounded-full h-2">
          <div
            className={`h-2 rounded-full bg-gradient-to-r from-${risk.color}-400 to-${risk.color}-600 transition-all duration-700`}
            style={{ width: `${score}%` }}
          ></div>
        </div>
      </div>

      <p className="text-slate-300 text-sm mb-3">{description}</p>
      
      <div className="flex justify-between items-center text-xs text-slate-500">
        <span>Last updated: {lastUpdated}</span>
        <span className={`px-2 py-1 rounded-full bg-${risk.color}-500/20 text-${risk.color}-400 font-medium`}>
          {risk.level.toUpperCase()}
        </span>
      </div>
    </div>
  );
}
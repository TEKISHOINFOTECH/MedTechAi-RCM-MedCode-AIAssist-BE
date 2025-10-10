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
    if (score >= 50) return { level: 'medium', color: 'amber', icon: AlertTriangle };
    return { level: 'low', color: 'emerald', icon: CheckCircle };
  };

  const risk = getRiskLevel(score);
  const Icon = risk.icon;

  const getTrendColor = () => {
    if (trend === 'up') return 'text-red-600';
    if (trend === 'down') return 'text-emerald-600';
    return 'text-slate-400';
  };

  const getRiskColorClasses = (color: string) => {
    const colors = {
      red: {
        iconBg: 'text-red-600 bg-red-50',
        border: 'border-red-200',
        progress: 'bg-red-500',
        badge: 'bg-red-100 text-red-700 border-red-200'
      },
      amber: {
        iconBg: 'text-amber-600 bg-amber-50',
        border: 'border-amber-200',
        progress: 'bg-amber-500',
        badge: 'bg-amber-100 text-amber-700 border border-amber-200'
      },
      emerald: {
        iconBg: 'text-emerald-600 bg-emerald-50',
        border: 'border-emerald-200',
        progress: 'bg-emerald-500',
        badge: 'bg-emerald-200',
        badgeFull: 'bg-emerald-100 text-emerald-700 border border-emerald-200'
      }
    };
    return colors[color as keyof typeof colors] || colors.emerald;
  };

  const colorClasses = getRiskColorClasses(risk.color);

  return (
    <div className="enterprise-card enterprise-card-hover p-6 group">
      <div className="flex items-start justify-between mb-6">
        <div className="flex items-center space-x-3">
          <div className={`p-2 rounded-lg ${colorClasses.iconBg}`}>
            <Icon className="w-5 h-5" />
          </div>
          <h3 className="font-bold text-slate-900 text-lg">{title}</h3>
        </div>
        <div className={`flex items-center space-x-2 px-3 py-1 rounded-full text-xs font-medium ${getTrendColor()}`}>
          <TrendingUp className={`w-3 h-3 ${trend === 'down' ? 'rotate-180' : ''}`} />
          <span className="font-semibold">{trend}</span>
        </div>
      </div>

      <div className="mb-6">
        <div className="flex items-end space-x-2 mb-3">
          <span className={`text-4xl font-bold ${getRiskColorClasses(risk.color).iconBg.split(' ')[0]}`}>{score}</span>
          <span className="text-slate-500 text-sm mb-2">/ 100</span>
        </div>
        <div className="w-full bg-slate-200 rounded-full h-3 overflow-hidden">
          <div
            className={`h-3 rounded-full ${colorClasses.progress} transition-all duration-1000 ease-out`}
            style={{ width: `${score}%` }}
          >
            <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent animate-pulse"></div>
          </div>
        </div>
      </div>

      <p className="text-slate-600 text-sm mb-4 leading-relaxed">{description}</p>
      
      <div className="flex justify-between items-center">
        <span className="text-xs text-slate-500">Last updated: {lastUpdated}</span>
        <span className={`px-3 py-1 rounded-full font-bold text-xs border ${colorClasses.badgeFull}`}>
          {risk.level.toUpperCase()}
        </span>
      </div>
    </div>
  );
}
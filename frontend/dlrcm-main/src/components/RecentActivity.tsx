import { Clock, CheckCircle, XCircle, AlertTriangle } from 'lucide-react';

export function RecentActivity() {
  const activities = [
    {
      type: 'success',
      title: 'Claim #A24789 Approved',
      description: 'Cardiovascular procedure - AI confidence: 96%',
      time: '2 min ago',
      icon: CheckCircle,
      color: 'green'
    },
    {
      type: 'warning',
      title: 'High Risk Detected',
      description: 'Batch #1248 requires manual review',
      time: '8 min ago',
      icon: AlertTriangle,
      color: 'yellow'
    },
    {
      type: 'error',
      title: 'Claim #B31092 Denied',
      description: 'Insufficient documentation provided',
      time: '15 min ago',
      icon: XCircle,
      color: 'red'
    },
    {
      type: 'success',
      title: 'Model Update Complete',
      description: 'Risk assessment accuracy improved by 2.3%',
      time: '1 hour ago',
      icon: CheckCircle,
      color: 'green'
    },
    {
      type: 'info',
      title: 'Scheduled Analysis',
      description: 'Weekly pattern analysis initiated',
      time: '2 hours ago',
      icon: Clock,
      color: 'blue'
    }
  ];

  return (
    <div className="glass-card p-6">
      <h3 className="text-xl font-bold text-slate-800 mb-8 flex items-center space-x-3">
        <div className="p-2 rounded-xl bg-gradient-to-br from-blue-500/20 to-cyan-500/10 border border-blue-400/30">
          <Clock className="w-5 h-5 text-blue-600" />
        </div>
        <span>Recent Activity</span>
      </h3>

      <div className="space-y-4 max-h-96 overflow-y-auto custom-scrollbar">
        {activities.map((activity, index) => {
          const Icon = activity.icon;
          return (
            <div key={index} className="flex items-start space-x-4 p-4 rounded-xl hover:bg-white/10 transition-all duration-300 group">
              <div className={`p-2 rounded-lg bg-gradient-to-br from-${activity.color}-500/20 to-${activity.color}-600/10 border border-${activity.color}-400/30`}>
                <Icon className={`w-4 h-4 text-${activity.color}-400`} />
              </div>
              <div className="flex-1 min-w-0">
                <h4 className="text-sm font-bold text-slate-900 truncate mb-1">{activity.title}</h4>
                <p className="text-xs text-slate-700 mb-2 leading-relaxed">{activity.description}</p>
                <span className="text-xs text-slate-600 font-medium">{activity.time}</span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
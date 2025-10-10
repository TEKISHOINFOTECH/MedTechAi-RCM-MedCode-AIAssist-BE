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
    <div className="bg-slate-800/50 backdrop-blur-sm rounded-xl border border-slate-700/50 p-6">
      <h3 className="text-lg font-semibold text-white mb-6 flex items-center space-x-2">
        <Clock className="w-5 h-5 text-blue-400" />
        <span>Recent Activity</span>
      </h3>

      <div className="space-y-4 max-h-96 overflow-y-auto custom-scrollbar">
        {activities.map((activity, index) => {
          const Icon = activity.icon;
          return (
            <div key={index} className="flex items-start space-x-3 p-3 rounded-lg hover:bg-slate-700/30 transition-colors">
              <Icon className={`w-4 h-4 text-${activity.color}-400 mt-1 flex-shrink-0`} />
              <div className="flex-1 min-w-0">
                <h4 className="text-sm font-medium text-white truncate">{activity.title}</h4>
                <p className="text-xs text-slate-400 mt-1">{activity.description}</p>
                <span className="text-xs text-slate-500 mt-2 inline-block">{activity.time}</span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
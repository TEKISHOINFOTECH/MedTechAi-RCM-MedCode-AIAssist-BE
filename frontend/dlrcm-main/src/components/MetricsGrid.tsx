import { TrendingUp, TrendingDown, Users, DollarSign, Clock, AlertCircle } from 'lucide-react';

export function MetricsGrid() {
  const metrics = [
    {
      title: "Denial Rate",
      value: "12.4%",
      change: -2.3,
      icon: TrendingDown,
      color: "emerald",
      description: "Compared to last month"
    },
    {
      title: "Claims Processed",
      value: "2,847",
      change: 15.2,
      icon: Users,
      color: "blue",
      description: "This week"
    },
    {
      title: "Revenue at Risk",
      value: "$847K",
      change: -8.1,
      icon: DollarSign,
      color: "emerald",
      description: "Potential losses"
    },
    {
      title: "Avg Processing Time",
      value: "4.2 days",
      change: -12.5,
      icon: Clock,
      color: "emerald",
      description: "Reduction from baseline"
    },
    {
      title: "High Risk Claims",
      value: "89",
      change: 5.7,
      icon: AlertCircle,
      color: "red",
      description: "Require immediate attention"
    },
    {
      title: "AI Accuracy",
      value: "94.7%",
      change: 1.2,
      icon: TrendingUp,
      color: "emerald",
      description: "Model performance"
    }
  ];

  const getIconColor = (color: string) => {
    const colors = {
      emerald: 'text-emerald-600 bg-emerald-50',
      blue: 'text-blue-600 bg-blue-50',
      red: 'text-red-600 bg-red-50',
      amber: 'text-amber-600 bg-amber-50'
    };
    return colors[color as keyof typeof colors] || colors.blue;
  };

  const getChangeIndicator = (change: number) => {
    if (change > 0) return <TrendingUp className="w-3 h-3 text-emerald-600" />;
    if (change < 0) return <TrendingDown className="w-3 h-3 text-red-600" />;
    return null;
  };

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      {metrics.map((metric, index) => {
        const Icon = metric.icon;
        const isPositive = metric.change > 0;

        return (
          <div key={index} className="metric-card group">
            <div className="flex items-center justify-between mb-4">
              <div className={`p-3 rounded-lg ${getIconColor(metric.color)}`}>
                <Icon className="w-5 h-5" />
              </div>
              <div className={`flex items-center space-x-1 px-2 py-1 rounded-full text-xs font-medium ${
                isPositive ? 'bg-emerald-100 text-emerald-700' : 'bg-red-100 text-red-700'
              }`}>
                {getChangeIndicator(metric.change)}
                <span>{Math.abs(metric.change)}%</span>
              </div>
            </div>
            
            <div className="mb-2">
              <h3 className="text-2xl font-bold text-slate-900 mb-1">{metric.value}</h3>
              <p className="text-sm font-medium text-slate-700">{metric.title}</p>
            </div>
            
            <p className="text-xs text-slate-600">{metric.description}</p>
          </div>
        );
      })}
    </div>
  );
}
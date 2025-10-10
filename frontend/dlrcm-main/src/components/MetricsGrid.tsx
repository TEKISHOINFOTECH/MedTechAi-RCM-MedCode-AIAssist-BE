import { TrendingUp, TrendingDown, Users, DollarSign, Clock, AlertCircle } from 'lucide-react';

export function MetricsGrid() {
  const metrics = [
    {
      title: "Denial Rate",
      value: "12.4%",
      change: -2.3,
      icon: TrendingDown,
      color: "green"
    },
    {
      title: "Claims Processed",
      value: "2,847",
      change: 15.2,
      icon: Users,
      color: "blue"
    },
    {
      title: "Revenue at Risk",
      value: "$847K",
      change: -8.1,
      icon: DollarSign,
      color: "green"
    },
    {
      title: "Avg Processing Time",
      value: "4.2 days",
      change: -12.5,
      icon: Clock,
      color: "green"
    },
    {
      title: "High Risk Claims",
      value: "89",
      change: 5.7,
      icon: AlertCircle,
      color: "red"
    },
    {
      title: "AI Accuracy",
      value: "94.7%",
      change: 1.2,
      icon: TrendingUp,
      color: "green"
    }
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      {metrics.map((metric, index) => {
        const Icon = metric.icon;
        const isPositive = metric.change > 0;
        const changeColor = metric.color === 'red' 
          ? (isPositive ? 'text-red-400' : 'text-green-400')
          : (isPositive ? 'text-green-400' : 'text-red-400');

        return (
          <div key={index} className="bg-slate-800/50 backdrop-blur-sm rounded-xl border border-slate-700/50 p-6 hover:border-slate-600/50 transition-all duration-300">
            <div className="flex items-center justify-between mb-4">
              <Icon className={`w-5 h-5 text-${metric.color}-400`} />
              <span className={`text-sm font-medium ${changeColor} flex items-center space-x-1`}>
                {isPositive ? (
                  <TrendingUp className="w-3 h-3" />
                ) : (
                  <TrendingDown className="w-3 h-3" />
                )}
                <span>{Math.abs(metric.change)}%</span>
              </span>
            </div>
            
            <div className="mb-2">
              <h3 className="text-2xl font-bold text-white">{metric.value}</h3>
            </div>
            
            <p className="text-slate-400 text-sm">{metric.title}</p>
          </div>
        );
      })}
    </div>
  );
}
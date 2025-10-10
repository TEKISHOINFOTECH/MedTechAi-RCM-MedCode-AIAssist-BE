import { Lightbulb, Brain, Target, Zap } from 'lucide-react';

export function AIInsights() {
  const insights = [
    {
      icon: Lightbulb,
      title: "Pattern Detection",
      description: "AI identified 3 recurring denial patterns in cardiovascular claims",
      confidence: 94,
      action: "Review Documentation Standards"
    },
    {
      icon: Target,
      title: "Risk Prediction",
      description: "High probability of denial for upcoming submission batch #1247",
      confidence: 87,
      action: "Pre-validate Claims"
    },
    {
      icon: Zap,
      title: "Quick Win",
      description: "Implementing suggested code modifications could reduce denials by 23%",
      confidence: 92,
      action: "Apply Recommendations"
    }
  ];

  return (
    <div className="bg-slate-800/50 backdrop-blur-sm rounded-xl border border-slate-700/50 p-6">
      <div className="flex items-center space-x-3 mb-6">
        <div className="relative">
          <Brain className="w-6 h-6 text-purple-400" />
          <div className="absolute -top-1 -right-1 w-3 h-3 bg-purple-400 rounded-full animate-ping"></div>
        </div>
        <h3 className="text-lg font-semibold text-white">AI Insights</h3>
        <span className="px-2 py-1 bg-purple-500/20 text-purple-400 text-xs font-medium rounded-full">
          LIVE
        </span>
      </div>

      <div className="space-y-4">
        {insights.map((insight, index) => {
          const Icon = insight.icon;
          return (
            <div key={index} className="border border-slate-700/50 rounded-lg p-4 hover:border-slate-600/50 transition-all duration-200">
              <div className="flex items-start space-x-3">
                <Icon className="w-5 h-5 text-blue-400 mt-0.5" />
                <div className="flex-1">
                  <h4 className="font-medium text-white mb-1">{insight.title}</h4>
                  <p className="text-sm text-slate-300 mb-3">{insight.description}</p>
                  
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                      <span className="text-xs text-slate-400">Confidence:</span>
                      <div className="flex items-center space-x-1">
                        <div className="w-12 h-1.5 bg-slate-700 rounded-full overflow-hidden">
                          <div 
                            className="h-full bg-gradient-to-r from-green-400 to-green-500 transition-all duration-700"
                            style={{ width: `${insight.confidence}%` }}
                          ></div>
                        </div>
                        <span className="text-xs text-green-400 font-medium">{insight.confidence}%</span>
                      </div>
                    </div>
                    
                    <button className="text-xs bg-blue-600 hover:bg-blue-700 text-white px-3 py-1 rounded-full transition-colors">
                      {insight.action}
                    </button>
                  </div>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
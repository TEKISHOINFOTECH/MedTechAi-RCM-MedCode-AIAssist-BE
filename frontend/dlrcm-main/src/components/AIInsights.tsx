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
    <div className="glass-card p-6">
      <div className="flex items-center space-x-4 mb-8">
        <div className="relative ai-glow">
          <div className="absolute inset-0 bg-gradient-to-r from-purple-400 to-pink-500 rounded-xl blur-lg opacity-30 animate-glow-pulse"></div>
          <div className="relative bg-white/10 backdrop-blur-xl rounded-xl p-3 border border-white/20">
            <Brain className="w-6 h-6 text-gradient-purple" />
            <div className="absolute -top-1 -right-1 w-3 h-3 bg-gradient-to-r from-purple-400 to-pink-500 rounded-full animate-ping"></div>
          </div>
        </div>
        <h3 className="text-xl font-bold text-slate-800">AI Insights</h3>
        <span className="px-3 py-1 bg-gradient-to-r from-purple-500/20 to-pink-500/20 text-purple-400 text-xs font-bold rounded-full border border-purple-400/30">
          LIVE
        </span>
      </div>

      <div className="space-y-4">
        {insights.map((insight, index) => {
          const Icon = insight.icon;
          return (
            <div key={index} className="glass-card p-5 hover:bg-white/15 transition-all duration-300 group">
              <div className="flex items-start space-x-4">
                <div className="p-2 rounded-xl bg-gradient-to-br from-blue-500/20 to-cyan-500/10 border border-blue-400/30">
                  <Icon className="w-5 h-5 text-blue-400" />
                </div>
                <div className="flex-1">
                  <h4 className="font-bold text-slate-900 mb-2 text-lg">{insight.title}</h4>
                  <p className="text-sm text-slate-700 mb-4 leading-relaxed">{insight.description}</p>
                  
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                      <span className="text-xs text-slate-600 font-medium">Confidence:</span>
                      <div className="flex items-center space-x-2">
                        <div className="w-16 h-2 bg-white/20 rounded-full overflow-hidden">
                          <div 
                            className="h-full bg-gradient-to-r from-green-400 to-emerald-500 transition-all duration-1000 relative"
                            style={{ width: `${insight.confidence}%` }}
                          >
                            <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/30 to-transparent animate-shimmer"></div>
                          </div>
                        </div>
                        <span className="text-xs text-green-400 font-bold">{insight.confidence}%</span>
                      </div>
                    </div>
                    
                    <button className="text-xs glossy-button px-4 py-2 text-sm">
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
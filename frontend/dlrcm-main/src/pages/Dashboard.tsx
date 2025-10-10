import { RiskCard } from '../components/RiskCard';
import { AIInsights } from '../components/AIInsights';
import { MetricsGrid } from '../components/MetricsGrid';
import { RecentActivity } from '../components/RecentActivity';
import { RiskChart } from '../components/RiskChart';

export function Dashboard() {
  const riskData = [
    {
      title: "Prior Authorization",
      score: 23,
      trend: 'down' as const,
      description: "AI-optimized pre-auth processes reducing denial risk",
      lastUpdated: "2 mins ago"
    },
    {
      title: "Documentation Quality",
      score: 67,
      trend: 'stable' as const,
      description: "Medical coding accuracy needs improvement",
      lastUpdated: "5 mins ago"
    },
    {
      title: "Claims Processing",
      score: 34,
      trend: 'down' as const,
      description: "Streamlined workflow reducing processing errors",
      lastUpdated: "1 min ago"
    }
  ];

  return (
    <main className="max-w-7xl mx-auto px-6 py-8">
      {/* Hero Section */}
      <div className="mb-8">
        <div className="bg-gradient-to-r from-blue-600/20 to-purple-600/20 rounded-2xl border border-blue-500/30 p-8 mb-8">
          <h2 className="text-3xl font-bold text-white mb-2">
            AI-Powered Risk Intelligence
          </h2>
          <p className="text-slate-300 text-lg">
            Real-time denial prevention with advanced machine learning algorithms
          </p>
          <div className="flex items-center space-x-4 mt-4">
            <div className="flex items-center space-x-2 text-green-400">
              <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
              <span className="text-sm font-medium">AI Models Active</span>
            </div>
            <div className="text-slate-400 text-sm">|</div>
            <div className="text-slate-300 text-sm">
              Processing <span className="font-semibold text-blue-400">847 claims/hour</span>
            </div>
          </div>
        </div>
      </div>

      {/* Metrics Grid */}
      <div className="mb-8">
        <MetricsGrid />
      </div>

      {/* Risk Cards */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
        {riskData.map((risk, index) => (
          <RiskCard key={index} {...risk} />
        ))}
      </div>

      {/* Analytics Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
        <RiskChart />
        <AIInsights />
      </div>

      {/* Recent Activity */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div className="lg:col-span-2">
          <RecentActivity />
        </div>
        
        <div className="bg-slate-800/50 backdrop-blur-sm rounded-xl border border-slate-700/50 p-6">
          <h3 className="text-lg font-semibold text-white mb-4">Quick Actions</h3>
          <div className="space-y-3">
            <button className="w-full bg-blue-600 hover:bg-blue-700 text-white py-3 px-4 rounded-lg transition-colors text-left">
              Run Batch Analysis
            </button>
            <button className="w-full bg-purple-600 hover:bg-purple-700 text-white py-3 px-4 rounded-lg transition-colors text-left">
              Update AI Models
            </button>
            <button className="w-full bg-green-600 hover:bg-green-700 text-white py-3 px-4 rounded-lg transition-colors text-left">
              Generate Report
            </button>
            <button className="w-full bg-slate-600 hover:bg-slate-700 text-white py-3 px-4 rounded-lg transition-colors text-left">
              Export Data
            </button>
          </div>
        </div>
      </div>
    </main>
  );
}
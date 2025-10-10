import { RiskCard } from '../components/RiskCard';
import { AIInsights } from '../components/AIInsights';
import { MetricsGrid } from '../components/MetricsGrid';
import { RecentActivity } from '../components/RecentActivity';
import { RiskChart } from '../components/RiskChart';
import { Logo } from '../components/Logo';

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
    <div className="max-w-7xl mx-auto px-6 py-8">
      {/* Hero Section */}
      <div className="mb-12">
        <div className="enterprise-card p-10 mb-8">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-4xl font-bold text-slate-800 mb-4">
                AI Powered Risk Intelligence
              </h2>
              <p className="text-slate-700 text-xl mb-6 font-medium">
                Real-time denial prevention with advanced machine learning algorithms
              </p>
                <div className="flex items-center space-x-6">
                <div className="flex items-center space-x-3">
                  <div className="w-3 h-3 bg-emerald-500 rounded-full animate-pulse"></div>
                  <span className="text-slate-800 font-semibold">AI Models Active</span>
                </div>
                <div className="w-px h-6 bg-slate-300"></div>
                <div className="text-slate-700">
                  Processing <span className="font-bold text-slate-900">847 claims/hour</span>
                </div>
              </div>
            </div>
            
            <div className="hidden lg:flex lg:items-center lg:space-x-6">
              <Logo size="xl" />
              <div className="bg-gradient-to-br from-blue-50 to-blue-100 rounded-2xl p-8">
                <div className="text-6xl font-bold text-blue-600">94.7%</div>
                <div className="text-slate-600 font-medium">Overall Accuracy</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Metrics Grid */}
      <div className="mb-8">
        <div className="mb-6">
          <h3 className="text-2xl font-bold text-slate-900 mb-2">Key Performance Indicators</h3>
          <p className="text-slate-700">Real-time metrics and analytics for your healthcare operations</p>
        </div>
        <MetricsGrid />
      </div>

      {/* Risk Cards */}
      <div className="mb-8">
        <div className="mb-6">
          <h3 className="text-2xl font-bold text-slate-900 mb-2">Risk Assessment Dashboard</h3>
          <p className="text-slate-700">Comprehensive analysis of potential claim denial risks</p>
        </div>
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {riskData.map((risk, index) => (
            <RiskCard key={index} {...risk} />
          ))}
        </div>
      </div>

      {/* Analytics Section */}
      <div className="mb-8">
        <div className="mb-6">
          <h3 className="text-2xl font-bold text-slate-900 mb-2">Analytics & Insights</h3>
          <p className="text-slate-700">Advanced data visualization and trend analysis</p>
        </div>
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          <RiskChart />
          <AIInsights />
        </div>
      </div>

      {/* Bottom Section */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div className="lg:col-span-2">
          <RecentActivity />
        </div>
        
        <div className="enterprise-card p-6">
          <h3 className="text-xl font-bold text-slate-900 mb-6">Quick Actions</h3>
          <div className="space-y-4">
            <button className="w-full primary-button flex items-center space-x-3">
              <span>Run Batch Analysis</span>
            </button>
            <button className="-primary-button flex items-center space-x-3">
              <span>Update AI Models</span>
            </button>
            <button className="success-button flex items-center space-x-3">
              <span>Generate Report</span>
            </button>
            <button className="premium-button flex items-center space-x-3">
              <span>Export Data</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
import { useState, useEffect } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { FileText, AlertTriangle, CheckCircle, XCircle, Brain, TrendingUp, Filter, Search, ArrowLeft, Lightbulb, CreditCard as Edit } from 'lucide-react';
import type { Claim } from '../types/claim';

export function ClaimsReview() {
  const { fileId } = useParams();
  const navigate = useNavigate();
  const [claims, setClaims] = useState<Claim[]>([]);
  const [selectedClaim, setSelectedClaim] = useState<Claim | null>(null);
  const [filterRisk, setFilterRisk] = useState<'all' | 'low' | 'medium' | 'high'>('all');
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    // Simulate loading claims data
    const mockClaims: Claim[] = Array.from({ length: 10 }, (_, i) => ({
      id: `CLM-${String(i + 1).padStart(3, '0')}`,
      patientName: `Patient ${i + 1}`,
      patientId: `PAT${String(i + 1).padStart(4, '0')}`,
      dateOfService: new Date(2024, 0, i + 1).toISOString().split('T')[0],
      provider: `Dr. ${['Smith', 'Johnson', 'Williams', 'Brown', 'Jones'][i % 5]}`,
      totalAmount: Math.floor(Math.random() * 5000) + 500,
      riskScore: Math.floor(Math.random() * 100),
      status: ['pending', 'processing', 'verified', 'flagged'][Math.floor(Math.random() * 4)] as any,
      denialRisk: ['low', 'medium', 'high'][Math.floor(Math.random() * 3)] as any,
      icdCodes: [
        {
          code: `Z${String(Math.floor(Math.random() * 99)).padStart(2, '0')}.${Math.floor(Math.random() * 9)}`,
          description: 'Primary diagnosis code',
          isValid: Math.random() > 0.3,
          issues: Math.random() > 0.7 ? ['Code may be outdated', 'Missing specificity'] : undefined,
          suggestions: Math.random() > 0.7 ? ['Consider using more specific code', 'Verify with latest ICD-10 updates'] : undefined
        }
      ],
      cptCodes: [
        {
          code: `${Math.floor(Math.random() * 99999)}`,
          description: 'Primary procedure code',
          isValid: Math.random() > 0.2,
          issues: Math.random() > 0.8 ? ['Modifier may be required', 'Bundling rules apply'] : undefined,
          suggestions: Math.random() > 0.8 ? ['Add appropriate modifier', 'Check NCCI edits'] : undefined,
          modifiers: Math.random() > 0.5 ? ['26', 'TC'] : undefined
        }
      ],
      aiRecommendations: [
        {
          id: `REC-${i + 1}`,
          type: ['critical', 'warning', 'suggestion'][Math.floor(Math.random() * 3)] as any,
          category: ['coding', 'documentation', 'authorization', 'billing'][Math.floor(Math.random() * 4)] as any,
          title: 'Improve Documentation',
          description: 'Add supporting documentation for procedure complexity',
          impact: Math.floor(Math.random() * 30) + 10,
          actionItems: ['Obtain operative report', 'Include diagnostic images', 'Add physician notes'],
          priority: ['high', 'medium', 'low'][Math.floor(Math.random() * 3)] as any
        }
      ]
    }));

    setClaims(mockClaims);
  }, [fileId]);

  const filteredClaims = claims.filter(claim => {
    const matchesRisk = filterRisk === 'all' || claim.denialRisk === filterRisk;
    const matchesSearch = claim.patientName.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         claim.id.toLowerCase().includes(searchTerm.toLowerCase());
    return matchesRisk && matchesSearch;
  });

  const getRiskColor = (risk: string) => {
    switch (risk) {
      case 'high': return 'text-red-400 bg-red-500/20';
      case 'medium': return 'text-yellow-400 bg-yellow-500/20';
      case 'low': return 'text-green-400 bg-green-500/20';
      default: return 'text-slate-400 bg-slate-500/20';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'verified': return <CheckCircle className="w-4 h-4 text-green-400" />;
      case 'flagged': return <XCircle className="w-4 h-4 text-red-400" />;
      case 'processing': return <Brain className="w-4 h-4 text-blue-400 animate-pulse" />;
      default: return <AlertTriangle className="w-4 h-4 text-yellow-400" />;
    }
  };

  return (
    <main className="max-w-7xl mx-auto px-6 py-8">
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div className="flex items-center space-x-4">
          <Link 
            to="/upload" 
            className="flex items-center space-x-2 text-slate-400 hover:text-white transition-colors"
          >
            <ArrowLeft className="w-4 h-4" />
            <span>Back to Upload</span>
          </Link>
          <div>
            <h1 className="text-3xl font-bold text-white">Claims Review</h1>
            <p className="text-slate-300">AI-powered analysis of {claims.length} claims</p>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Claims List */}
        <div className="lg:col-span-2">
          {/* Filters */}
          <div className="bg-slate-800/50 backdrop-blur-sm rounded-xl border border-slate-700/50 p-4 mb-6">
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2">
                <Search className="w-4 h-4 text-slate-400" />
                <input
                  type="text"
                  placeholder="Search claims..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="bg-slate-700 border border-slate-600 rounded-lg px-3 py-2 text-white placeholder-slate-400 focus:outline-none focus:border-blue-500"
                />
              </div>
              
              <div className="flex items-center space-x-2">
                <Filter className="w-4 h-4 text-slate-400" />
                <select
                  value={filterRisk}
                  onChange={(e) => setFilterRisk(e.target.value as any)}
                  className="bg-slate-700 border border-slate-600 rounded-lg px-3 py-2 text-white focus:outline-none focus:border-blue-500"
                >
                  <option value="all">All Risk Levels</option>
                  <option value="high">High Risk</option>
                  <option value="medium">Medium Risk</option>
                  <option value="low">Low Risk</option>
                </select>
              </div>
            </div>
          </div>

          {/* Claims Grid */}
          <div className="space-y-4">
            {filteredClaims.map((claim) => (
              <div
                key={claim.id}
                onClick={() => setSelectedClaim(claim)}
                className={`bg-slate-800/50 backdrop-blur-sm rounded-xl border border-slate-700/50 p-6 cursor-pointer transition-all duration-200 hover:border-slate-600/50 ${
                  selectedClaim?.id === claim.id ? 'border-blue-500/50 bg-blue-500/5' : ''
                }`}
              >
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center space-x-3">
                    {getStatusIcon(claim.status)}
                    <div>
                      <h3 className="font-semibold text-white">{claim.id}</h3>
                      <p className="text-sm text-slate-400">{claim.patientName}</p>
                    </div>
                  </div>
                  
                  <div className="flex items-center space-x-3">
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${getRiskColor(claim.denialRisk)}`}>
                      {claim.denialRisk.toUpperCase()}
                    </span>
                    <span className="text-lg font-bold text-white">{claim.riskScore}%</span>
                  </div>
                </div>

                <div className="grid grid-cols-3 gap-4 text-sm">
                  <div>
                    <p className="text-slate-400">Provider</p>
                    <p className="text-white">{claim.provider}</p>
                  </div>
                  <div>
                    <p className="text-slate-400">Date of Service</p>
                    <p className="text-white">{claim.dateOfService}</p>
                  </div>
                  <div>
                    <p className="text-slate-400">Amount</p>
                    <p className="text-white">${claim.totalAmount.toLocaleString()}</p>
                  </div>
                </div>

                {/* Risk Score Bar */}
                <div className="mt-4">
                  <div className="w-full bg-slate-700 rounded-full h-2">
                    <div
                      className={`h-2 rounded-full transition-all duration-700 ${
                        claim.riskScore >= 70 ? 'bg-gradient-to-r from-red-400 to-red-600' :
                        claim.riskScore >= 40 ? 'bg-gradient-to-r from-yellow-400 to-yellow-600' :
                        'bg-gradient-to-r from-green-400 to-green-600'
                      }`}
                      style={{ width: `${claim.riskScore}%` }}
                    ></div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Claim Details */}
        <div className="lg:col-span-1">
          {selectedClaim ? (
            <div className="bg-slate-800/50 backdrop-blur-sm rounded-xl border border-slate-700/50 p-6 sticky top-8">
              <div className="flex items-center justify-between mb-6">
                <h3 className="text-lg font-semibold text-white">Claim Details</h3>
                <div className="flex items-center space-x-3">
                  <button
                    onClick={() => navigate(`/claims/edit/${selectedClaim.id}`)}
                    className="flex items-center space-x-2 px-4 py-2 bg-blue-500 hover:bg-blue-600 text-white rounded-lg transition-colors"
                  >
                    <Edit className="w-4 h-4" />
                    <span>Edit</span>
                  </button>
                  <span className={`px-3 py-1 rounded-full text-sm font-medium ${getRiskColor(selectedClaim.denialRisk)}`}>
                    {selectedClaim.denialRisk.toUpperCase()} RISK
                  </span>
                </div>
              </div>

              {/* Patient Info */}
              <div className="mb-6">
                <h4 className="font-medium text-white mb-2">Patient Information</h4>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-slate-400">Name:</span>
                    <span className="text-white">{selectedClaim.patientName}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-400">ID:</span>
                    <span className="text-white">{selectedClaim.patientId}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-400">Provider:</span>
                    <span className="text-white">{selectedClaim.provider}</span>
                  </div>
                </div>
              </div>

              {/* Codes Analysis */}
              <div className="mb-6">
                <h4 className="font-medium text-white mb-3">Code Analysis</h4>
                
                {/* ICD Codes */}
                <div className="mb-4">
                  <h5 className="text-sm font-medium text-slate-300 mb-2">ICD Codes</h5>
                  {selectedClaim.icdCodes.map((code, index) => (
                    <div key={index} className="border border-slate-700/50 rounded-lg p-3 mb-2">
                      <div className="flex items-center justify-between mb-2">
                        <span className="font-mono text-sm text-blue-400">{code.code}</span>
                        {code.isValid ? (
                          <CheckCircle className="w-4 h-4 text-green-400" />
                        ) : (
                          <XCircle className="w-4 h-4 text-red-400" />
                        )}
                      </div>
                      <p className="text-xs text-slate-400 mb-2">{code.description}</p>
                      {code.issues && (
                        <div className="text-xs text-red-400">
                          Issues: {code.issues.join(', ')}
                        </div>
                      )}
                    </div>
                  ))}
                </div>

                {/* CPT Codes */}
                <div>
                  <h5 className="text-sm font-medium text-slate-300 mb-2">CPT Codes</h5>
                  {selectedClaim.cptCodes.map((code, index) => (
                    <div key={index} className="border border-slate-700/50 rounded-lg p-3">
                      <div className="flex items-center justify-between mb-2">
                        <span className="font-mono text-sm text-green-400">{code.code}</span>
                        {code.isValid ? (
                          <CheckCircle className="w-4 h-4 text-green-400" />
                        ) : (
                          <XCircle className="w-4 h-4 text-red-400" />
                        )}
                      </div>
                      <p className="text-xs text-slate-400 mb-2">{code.description}</p>
                      {code.modifiers && (
                        <div className="text-xs text-blue-400 mb-1">
                          Modifiers: {code.modifiers.join(', ')}
                        </div>
                      )}
                      {code.issues && (
                        <div className="text-xs text-red-400">
                          Issues: {code.issues.join(', ')}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>

              {/* AI Recommendations */}
              <div>
                <h4 className="font-medium text-white mb-3 flex items-center space-x-2">
                  <Lightbulb className="w-4 h-4 text-yellow-400" />
                  <span>AI Recommendations</span>
                </h4>
                
                {selectedClaim.aiRecommendations.map((rec) => (
                  <div key={rec.id} className="border border-slate-700/50 rounded-lg p-4 mb-3">
                    <div className="flex items-center justify-between mb-2">
                      <h5 className="text-sm font-medium text-white">{rec.title}</h5>
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                        rec.type === 'critical' ? 'bg-red-500/20 text-red-400' :
                        rec.type === 'warning' ? 'bg-yellow-500/20 text-yellow-400' :
                        'bg-blue-500/20 text-blue-400'
                      }`}>
                        {rec.type.toUpperCase()}
                      </span>
                    </div>
                    
                    <p className="text-xs text-slate-400 mb-3">{rec.description}</p>
                    
                    <div className="flex items-center justify-between mb-3">
                      <span className="text-xs text-slate-400">Impact:</span>
                      <span className="text-xs text-green-400 font-medium">-{rec.impact}% denial risk</span>
                    </div>
                    
                    <div>
                      <p className="text-xs text-slate-400 mb-2">Action Items:</p>
                      <ul className="text-xs text-slate-300 space-y-1">
                        {rec.actionItems.map((item, index) => (
                          <li key={index} className="flex items-start space-x-2">
                            <span className="text-blue-400">•</span>
                            <span>{item}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ) : (
            <div className="bg-slate-800/50 backdrop-blur-sm rounded-xl border border-slate-700/50 p-6 text-center">
              <FileText className="w-12 h-12 text-slate-400 mx-auto mb-4" />
              <p className="text-slate-400">Select a claim to view detailed analysis</p>
            </div>
          )}
        </div>
      </div>
    </main>
  );
}
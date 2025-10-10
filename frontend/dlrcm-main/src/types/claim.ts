export interface Claim {
  id: string;
  patientName: string;
  patientId: string;
  dateOfService: string;
  provider: string;
  icdCodes: ICDCode[];
  cptCodes: CPTCode[];
  totalAmount: number;
  riskScore: number;
  status: 'pending' | 'processing' | 'verified' | 'flagged';
  aiRecommendations: Recommendation[];
  denialRisk: 'low' | 'medium' | 'high';
}

export interface ICDCode {
  code: string;
  description: string;
  isValid: boolean;
  issues?: string[];
  suggestions?: string[];
}

export interface CPTCode {
  code: string;
  description: string;
  isValid: boolean;
  issues?: string[];
  suggestions?: string[];
  modifiers?: string[];
}

export interface Recommendation {
  id: string;
  type: 'critical' | 'warning' | 'suggestion';
  category: 'coding' | 'documentation' | 'authorization' | 'billing';
  title: string;
  description: string;
  impact: number; // Percentage reduction in denial risk
  actionItems: string[];
  priority: 'high' | 'medium' | 'low';
}

export interface EDIFile {
  id: string;
  fileName: string;
  uploadDate: string;
  totalClaims: number;
  processedClaims: number;
  status: 'uploading' | 'processing' | 'completed' | 'error';
  overallRiskScore: number;
  estimatedSavings: number;
}
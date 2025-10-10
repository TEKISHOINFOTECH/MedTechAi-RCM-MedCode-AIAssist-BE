import { useState, useEffect, useRef, useCallback } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { ArrowLeft, Save, FileCode, Download, Search, Plus, X, Upload, Sparkles, Loader2 } from 'lucide-react';
import type { Claim } from '../types/claim';
import { parseClaimSubmissionFile } from '../utils/parseClaimSubmission';
import { createClient } from '@supabase/supabase-js';

// Initialize Supabase client with fallback values for development
const supabaseUrl = import.meta.env.VITE_SUPABASE_URL || 'https://placeholder.supabase.co';
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY || 'placeholder-anon-key';

const supabase = createClient(supabaseUrl, supabaseAnonKey);

interface ICDCodeOption {
  code: string;
  description: string;
  confidence?: number;
  rationale?: string;
}

interface CPTCodeOption {
  code: string;
  description: string;
  category: string;
  confidence?: number;
  rationale?: string;
}

interface PatientHistory {
  date: string;
  diagnosis: string;
  icdCode: string;
  provider: string;
}

export function ClaimEdit() {
  const { claimId } = useParams();
  const navigate = useNavigate();

  const [claim, setClaim] = useState<Claim | null>(null);
  const [clinicalNotes, setClinicalNotes] = useState('');
  const [selectedICDs, setSelectedICDs] = useState<ICDCodeOption[]>([]);
  const [selectedCPTs, setSelectedCPTs] = useState<CPTCodeOption[]>([]);
  const [icdSearchTerm, setIcdSearchTerm] = useState('');
  const [showXMLPreview, setShowXMLPreview] = useState(false);
  const [generatedXML, setGeneratedXML] = useState('');
  const [aiSuggestedICDs, setAiSuggestedICDs] = useState<ICDCodeOption[]>([]);
  const [aiSuggestedCPTs, setAiSuggestedCPTs] = useState<CPTCodeOption[]>([]);
  const [isLoadingSuggestions, setIsLoadingSuggestions] = useState(false);
  const [isLoadingCPTSuggestions, setIsLoadingCPTSuggestions] = useState(false);
  const [showUploadSection, setShowUploadSection] = useState(true);
  const [isImprovingNotes, setIsImprovingNotes] = useState(false);
  const [improvedSoapNotes, setImprovedSoapNotes] = useState('');
  const debounceTimer = useRef<number | null>(null);

  const availableICDCodes: ICDCodeOption[] = [
    { code: 'E11.9', description: 'Type 2 diabetes mellitus without complications' },
    { code: 'I12.0', description: 'Hypertensive chronic kidney disease with stage 5 chronic kidney disease or end stage renal disease' },
    { code: 'J44.0', description: 'Chronic obstructive pulmonary disease with acute lower respiratory infection' },
    { code: 'M79.3', description: 'Panniculitis, unspecified' },
    { code: 'R50.9', description: 'Fever, unspecified' },
    { code: 'J45.909', description: 'Unspecified asthma, uncomplicated' },
    { code: 'K21.9', description: 'Gastro-esophageal reflux disease without esophagitis' },
    { code: 'E78.5', description: 'Hyperlipidemia, unspecified' },
    { code: 'M25.561', description: 'Pain in right knee' },
    { code: 'R51.9', description: 'Headache, unspecified' }
  ];

  const cptCodesForICD: { [key: string]: CPTCodeOption[] } = {
    'E11.9': [
      { code: '99213', description: 'Office or other outpatient visit, established patient, low to moderate complexity', category: 'Evaluation & Management' },
      { code: '82947', description: 'Glucose; quantitative, blood', category: 'Laboratory' },
      { code: '83036', description: 'Hemoglobin; glycosylated (A1C)', category: 'Laboratory' }
    ],
    'I12.0': [
      { code: '99214', description: 'Office visit, established patient, moderate complexity', category: 'Evaluation & Management' },
      { code: '93000', description: 'Electrocardiogram, complete', category: 'Cardiovascular' },
      { code: '80053', description: 'Comprehensive metabolic panel', category: 'Laboratory' }
    ],
    'J44.0': [
      { code: '94060', description: 'Spirometry before and after bronchodilator', category: 'Pulmonary' },
      { code: '94640', description: 'Aerosol or vapor inhalation treatment', category: 'Pulmonary' },
      { code: '71045', description: 'Chest X-ray', category: 'Radiology' }
    ],
    'default': [
      { code: '99213', description: 'Office visit, established patient, low to moderate complexity', category: 'Evaluation & Management' },
      { code: '99214', description: 'Office visit, established patient, moderate complexity', category: 'Evaluation & Management' },
      { code: '99215', description: 'Office visit, established patient, high complexity', category: 'Evaluation & Management' }
    ]
  };

  const patientHistory: PatientHistory[] = [
    { date: '2024-08-15', diagnosis: 'Type 2 Diabetes Mellitus', icdCode: 'E11.9', provider: 'Dr. Smith' },
    { date: '2024-06-20', diagnosis: 'Hypertensive chronic kidney disease with stage 5 chronic kidney disease or end stage renal disease', icdCode: 'I12.0', provider: 'Dr. Johnson' },
    { date: '2024-03-10', diagnosis: 'Annual Physical Examination', icdCode: 'Z00.00', provider: 'Dr. Smith' },
    { date: '2023-11-05', diagnosis: 'Acute Bronchitis', icdCode: 'J20.9', provider: 'Dr. Williams' }
  ];

  useEffect(() => {
    const mockClaim: Claim = {
      id: claimId || 'CLM-001',
      patientName: 'Patient 1',
      patientId: 'PAT0001',
      dateOfService: '2024-01-01',
      provider: 'Dr. Smith',
      totalAmount: 1500,
      riskScore: 45,
      status: 'pending',
      denialRisk: 'medium',
      icdCodes: [
        {
          code: 'E11.9',
          description: 'Type 2 diabetes mellitus without complications',
          isValid: true
        }
      ],
      cptCodes: [
        {
          code: '99213',
          description: 'Office visit',
          isValid: true
        }
      ],
      aiRecommendations: []
    };

    setClaim(mockClaim);
    setSelectedICDs(mockClaim.icdCodes.map(icd => ({ code: icd.code, description: icd.description })));
  }, [claimId]);

  const fetchAISuggestions = useCallback(async (notes: string) => {
    if (!notes || notes.trim().length < 20) {
      setAiSuggestedICDs([]);
      return;
    }

    // Check if Supabase is properly configured
    if (!import.meta.env.VITE_SUPABASE_URL || !import.meta.env.VITE_SUPABASE_ANON_KEY) {
      console.warn('Supabase not configured - AI suggestions disabled');
      setAiSuggestedICDs([]);
      return;
    }

    setIsLoadingSuggestions(true);
    try {
      const apiUrl = `${import.meta.env.VITE_SUPABASE_URL}/functions/v1/suggest-icd-codes`;
      const response = await fetch(apiUrl, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${import.meta.env.VITE_SUPABASE_ANON_KEY}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          clinicalNotes: notes,
          patientHistory: patientHistory
        }),
      });

      if (response.ok) {
        const data = await response.json();
        setAiSuggestedICDs(data.suggestions || []);
      } else {
        console.error('Failed to fetch AI suggestions');
        setAiSuggestedICDs([]);
      }
    } catch (error) {
      console.error('Error fetching AI suggestions:', error);
      setAiSuggestedICDs([]);
    } finally {
      setIsLoadingSuggestions(false);
    }
  }, []);

  const handleClinicalNotesChange = (notes: string) => {
    setClinicalNotes(notes);

    if (debounceTimer.current) {
      clearTimeout(debounceTimer.current);
    }

    debounceTimer.current = window.setTimeout(() => {
      fetchAISuggestions(notes);
    }, 1500);
  };

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    try {
      const content = await file.text();
      const parsed = parseClaimSubmissionFile(content);

      if (parsed.claimNumber) {
        setClaim(prev => prev ? { ...prev, id: parsed.claimNumber } : prev);
      }
      if (parsed.patientName) {
        setClaim(prev => prev ? { ...prev, patientName: parsed.patientName } : prev);
      }
      if (parsed.patientId) {
        setClaim(prev => prev ? { ...prev, patientId: parsed.patientId } : prev);
      }
      if (parsed.dateOfService) {
        setClaim(prev => prev ? { ...prev, dateOfService: parsed.dateOfService } : prev);
      }
      if (parsed.provider) {
        setClaim(prev => prev ? { ...prev, provider: parsed.provider } : prev);
      }
      if (parsed.totalAmount) {
        setClaim(prev => prev ? { ...prev, totalAmount: parsed.totalAmount } : prev);
      }
      if (parsed.clinicalNotes) {
        setClinicalNotes(parsed.clinicalNotes);
        fetchAISuggestions(parsed.clinicalNotes);
      }

      setShowUploadSection(false);
    } catch (error) {
      console.error('Error parsing file:', error);
      alert('Failed to parse file. Please check the format.');
    }
  };

  const improveClinicalNotes = async () => {
    if (!clinicalNotes || clinicalNotes.trim().length < 10) {
      alert('Please enter clinical notes before improving');
      return;
    }

    // Check if Supabase is properly configured
    if (!import.meta.env.VITE_SUPABASE_URL || !import.meta.env.VITE_SUPABASE_ANON_KEY) {
      alert('AI features are not configured. Please set up Supabase environment variables to use this feature.');
      return;
    }

    setIsImprovingNotes(true);
    try {
      const apiUrl = `${import.meta.env.VITE_SUPABASE_URL}/functions/v1/improve-clinical-notes`;
      const response = await fetch(apiUrl, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${import.meta.env.VITE_SUPABASE_ANON_KEY}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          clinicalNotes: clinicalNotes
        }),
      });

      if (response.ok) {
        const data = await response.json();
        setImprovedSoapNotes(data.improvedNotes || '');
        fetchAISuggestions(data.improvedNotes || clinicalNotes);
      } else {
        console.error('Failed to improve clinical notes');
        alert('Failed to improve notes. Please try again.');
      }
    } catch (error) {
      console.error('Error improving notes:', error);
      alert('Error improving notes. Please try again.');
    } finally {
      setIsImprovingNotes(false);
    }
  };

  const getSuggestedCPTCodes = (): CPTCodeOption[] => {
    const suggested: CPTCodeOption[] = [];
    const addedCodes = new Set<string>();

    selectedICDs.forEach(icd => {
      const codes = cptCodesForICD[icd.code] || cptCodesForICD['default'];
      codes.forEach(code => {
        if (!addedCodes.has(code.code)) {
          suggested.push(code);
          addedCodes.add(code.code);
        }
      });
    });

    if (suggested.length === 0) {
      return cptCodesForICD['default'];
    }

    return suggested;
  };

  const fetchCPTSuggestions = useCallback(async (icdCodes: ICDCodeOption[]) => {
    if (!icdCodes || icdCodes.length === 0) {
      setAiSuggestedCPTs([]);
      return;
    }

    // Check if Supabase is properly configured
    if (!import.meta.env.VITE_SUPABASE_URL || !import.meta.env.VITE_SUPABASE_ANON_KEY) {
      console.warn('Supabase not configured - CPT suggestions disabled');
      setAiSuggestedCPTs([]);
      return;
    }

    setIsLoadingCPTSuggestions(true);
    try {
      const apiUrl = `${import.meta.env.VITE_SUPABASE_URL}/functions/v1/suggest-cpt-codes`;
      const response = await fetch(apiUrl, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${import.meta.env.VITE_SUPABASE_ANON_KEY}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          icdCodes: icdCodes,
          patientHistory: patientHistory,
          clinicalNotes: clinicalNotes
        }),
      });

      if (response.ok) {
        const data = await response.json();
        setAiSuggestedCPTs(data.suggestions || []);
      } else {
        console.error('Failed to fetch CPT suggestions');
        setAiSuggestedCPTs([]);
      }
    } catch (error) {
      console.error('Error fetching CPT suggestions:', error);
      setAiSuggestedCPTs([]);
    } finally {
      setIsLoadingCPTSuggestions(false);
    }
  }, [clinicalNotes, patientHistory]);

  const addICD = (icd: ICDCodeOption) => {
    if (!selectedICDs.find(i => i.code === icd.code)) {
      const newICDs = [...selectedICDs, icd];
      setSelectedICDs(newICDs);
      fetchCPTSuggestions(newICDs);
    }
  };

  const removeICD = (code: string) => {
    const newICDs = selectedICDs.filter(i => i.code !== code);
    setSelectedICDs(newICDs);
    fetchCPTSuggestions(newICDs);
  };

  const addCPT = (cpt: CPTCodeOption) => {
    if (!selectedCPTs.find(c => c.code === cpt.code)) {
      setSelectedCPTs([...selectedCPTs, cpt]);
    }
  };

  const removeCPT = (code: string) => {
    setSelectedCPTs(selectedCPTs.filter(c => c.code !== code));
  };

  const generateXML = () => {
    const xml = `<?xml version="1.0" encoding="UTF-8"?>
<Claim xmlns="http://www.eclaimlink.ae/DHCLAIM.xsd">
  <Header>
    <TransactionDate>${new Date().toISOString().split('T')[0]}</TransactionDate>
    <ClaimID>${claim?.id}</ClaimID>
    <ProviderID>${claim?.provider}</ProviderID>
    <PayerID>DHPAYER001</PayerID>
  </Header>

  <Patient>
    <PatientID>${claim?.patientId}</PatientID>
    <PatientName>${claim?.patientName}</PatientName>
    <DateOfBirth>1980-01-01</DateOfBirth>
    <Gender>M</Gender>
    <EmiratesID>784-1234-1234567-1</EmiratesID>
  </Patient>

  <Provider>
    <ProviderName>${claim?.provider}</ProviderName>
    <ProviderLicense>DHA-12345</ProviderLicense>
    <Facility>
      <FacilityName>Medical Center</FacilityName>
      <FacilityLicense>DHA-FAC-001</FacilityLicense>
    </Facility>
  </Provider>

  <ServiceDetails>
    <DateOfService>${claim?.dateOfService}</DateOfService>
    <EncounterType>Outpatient</EncounterType>
    <ClinicalNotes><![CDATA[${improvedSoapNotes}]]></ClinicalNotes>
  </ServiceDetails>

  <Diagnosis>
${selectedICDs.map((icd, index) => `    <DiagnosisCode sequence="${index + 1}">
      <Code>${icd.code}</Code>
      <Description>${icd.description}</Description>
      <Type>${index === 0 ? 'Primary' : 'Secondary'}</Type>
    </DiagnosisCode>`).join('\n')}
  </Diagnosis>

  <Services>
${selectedCPTs.map((cpt, index) => `    <Service sequence="${index + 1}">
      <ServiceCode>${cpt.code}</ServiceCode>
      <ServiceDescription>${cpt.description}</ServiceDescription>
      <Quantity>1</Quantity>
      <UnitPrice>${(claim?.totalAmount || 0) / selectedCPTs.length}</UnitPrice>
      <TotalAmount>${(claim?.totalAmount || 0) / selectedCPTs.length}</TotalAmount>
      <Category>${cpt.category}</Category>
    </Service>`).join('\n')}
  </Services>

  <PatientHistory>
${patientHistory.map((history, index) => `    <HistoricalDiagnosis sequence="${index + 1}">
      <Date>${history.date}</Date>
      <DiagnosisCode>${history.icdCode}</DiagnosisCode>
      <Diagnosis>${history.diagnosis}</Diagnosis>
      <Provider>${history.provider}</Provider>
    </HistoricalDiagnosis>`).join('\n')}
  </PatientHistory>

  <Financial>
    <GrossAmount>${claim?.totalAmount}</GrossAmount>
    <NetAmount>${claim?.totalAmount}</NetAmount>
    <PatientShare>0</PatientShare>
    <Currency>AED</Currency>
  </Financial>
</Claim>`;

    setGeneratedXML(xml);
    setShowXMLPreview(true);
  };

  const handleSave = () => {
    generateXML();
  };

  const downloadXML = () => {
    const blob = new Blob([generatedXML], { type: 'application/xml' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `claim-${claim?.id}-${Date.now()}.xml`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const filteredICDs = availableICDCodes.filter(icd =>
    icd.code.toLowerCase().includes(icdSearchTerm.toLowerCase()) ||
    icd.description.toLowerCase().includes(icdSearchTerm.toLowerCase())
  );

  if (!claim) {
    return <div className="text-white p-8">Loading...</div>;
  }

  return (
    <main className="max-w-7xl mx-auto px-6 py-8">
      <div className="flex items-center justify-between mb-8">
        <div className="flex items-center space-x-4">
          <Link
            to="/claims"
            className="flex items-center space-x-2 text-slate-400 hover:text-white transition-colors"
          >
            <ArrowLeft className="w-4 h-4" />
            <span>Back to Claims</span>
          </Link>
          <div>
            <h1 className="text-3xl font-bold text-white">Edit Claim: {claim.id}</h1>
            <p className="text-slate-300">{claim.patientName} - {claim.dateOfService}</p>
          </div>
        </div>

        <div className="flex items-center space-x-3">
          {showXMLPreview && (
            <button
              onClick={downloadXML}
              className="flex items-center space-x-2 px-4 py-2 bg-green-500 hover:bg-green-600 text-white rounded-lg transition-colors"
            >
              <Download className="w-4 h-4" />
              <span>Download XML</span>
            </button>
          )}
          <button
            onClick={handleSave}
            className="flex items-center space-x-2 px-4 py-2 bg-blue-500 hover:bg-blue-600 text-white rounded-lg transition-colors"
          >
            <Save className="w-4 h-4" />
            <span>Save & Generate XML</span>
          </button>
        </div>
      </div>

      

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-6">
          <div className="bg-slate-800/50 backdrop-blur-sm rounded-xl border border-slate-700/50 p-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-semibold text-white">Clinical Notes & Observations</h2>
              <button
                onClick={improveClinicalNotes}
                disabled={isImprovingNotes || !clinicalNotes}
                className="flex items-center space-x-2 px-4 py-2 bg-gradient-to-r from-green-500 to-teal-500 hover:from-green-600 hover:to-teal-600 text-white rounded-lg transition-colors text-sm disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isImprovingNotes ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin" />
                    <span>Improving with SOAP...</span>
                  </>
                ) : (
                  <>
                    <Sparkles className="w-4 h-4" />
                    <span>Improve with SOAP Format</span>
                  </>
                )}
              </button>
            </div>
            <textarea
              value={clinicalNotes}
              onChange={(e) => handleClinicalNotesChange(e.target.value)}
              placeholder="Enter detailed clinical observations, patient symptoms, examination findings, treatment plan, and medical notes..."
              className="w-full h-64 bg-slate-700 border border-slate-600 rounded-lg px-4 py-3 text-white placeholder-slate-400 focus:outline-none focus:border-blue-500 resize-none"
            />
            <div className="mt-2 text-xs text-slate-400">
              Click "Improve with SOAP Format" to restructure notes into professional Subjective, Objective, Assessment, Plan format
            </div>
            {isLoadingSuggestions && (
              <div className="flex items-center space-x-2 mt-3 text-blue-400">
                <Loader2 className="w-4 h-4 animate-spin" />
                <span className="text-sm">AI is analyzing clinical notes...</span>
              </div>
            )}
          </div>

          {improvedSoapNotes && (
            <div className="bg-gradient-to-br from-teal-900/30 to-green-900/30 backdrop-blur-sm rounded-xl border border-teal-500/30 p-6">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-xl font-semibold text-white flex items-center space-x-2">
                  <Sparkles className="w-5 h-5 text-teal-400" />
                  <span>Improved SOAP Format Notes</span>
                </h2>
                <button
                  onClick={() => setImprovedSoapNotes('')}
                  className="text-slate-400 hover:text-white transition-colors"
                  title="Close improved notes panel"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>

              <textarea
                value={improvedSoapNotes}
                onChange={(e) => setImprovedSoapNotes(e.target.value)}
                className="w-full h-96 bg-slate-800/50 border border-teal-500/30 rounded-lg px-4 py-3 text-white placeholder-slate-400 focus:outline-none focus:border-teal-500 resize-none font-mono text-sm leading-relaxed"
                placeholder="Improved SOAP notes will appear here..."
              />

              <div className="mt-4 grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="bg-slate-800/50 rounded-lg p-4 border border-blue-500/30">
                  <h3 className="text-sm font-semibold text-blue-400 mb-2 flex items-center space-x-1">
                    <span>Selected ICD-10 Codes</span>
                    <span className="text-xs text-slate-400">({selectedICDs.length})</span>
                  </h3>
                  {selectedICDs.length === 0 ? (
                    <p className="text-xs text-slate-400">No ICD codes selected yet</p>
                  ) : (
                    <div className="space-y-2 max-h-40 overflow-y-auto">
                      {selectedICDs.map((icd) => (
                        <div key={icd.code} className="text-xs">
                          <span className="font-mono text-blue-300">{icd.code}</span>
                          <span className="text-slate-300"> - {icd.description}</span>
                        </div>
                      ))}
                    </div>
                  )}
                </div>

                <div className="bg-slate-800/50 rounded-lg p-4 border border-green-500/30">
                  <h3 className="text-sm font-semibold text-green-400 mb-2 flex items-center space-x-1">
                    <span>Selected CPT Codes</span>
                    <span className="text-xs text-slate-400">({selectedCPTs.length})</span>
                  </h3>
                  {selectedCPTs.length === 0 ? (
                    <p className="text-xs text-slate-400">No CPT codes selected yet</p>
                  ) : (
                    <div className="space-y-2 max-h-40 overflow-y-auto">
                      {selectedCPTs.map((cpt) => (
                        <div key={cpt.code} className="text-xs">
                          <span className="font-mono text-green-300">{cpt.code}</span>
                          <span className="text-slate-300"> - {cpt.description}</span>
                          {cpt.category && (
                            <span className="text-slate-500 ml-1">({cpt.category})</span>
                          )}
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </div>

              <div className="mt-3 text-xs text-teal-300">
                These notes have been restructured into SOAP format. You can edit them or close this panel. The original notes remain unchanged above.
              </div>
            </div>
          )}

          <div className="bg-slate-800/50 backdrop-blur-sm rounded-xl border border-slate-700/50 p-6">
            <h2 className="text-xl font-semibold text-white mb-4">Selected ICD Codes</h2>
            <div className="space-y-2 mb-4">
              {selectedICDs.length === 0 ? (
                <p className="text-slate-400 text-sm">No ICD codes selected. Select from the panel on the right.</p>
              ) : (
                selectedICDs.map((icd) => (
                  <div key={icd.code} className="flex items-center justify-between bg-slate-700/50 rounded-lg p-3">
                    <div>
                      <span className="font-mono text-sm text-blue-400">{icd.code}</span>
                      <p className="text-sm text-slate-300">{icd.description}</p>
                    </div>
                    <button
                      onClick={() => removeICD(icd.code)}
                      className="text-red-400 hover:text-red-300 transition-colors"
                    >
                      <X className="w-4 h-4" />
                    </button>
                  </div>
                ))
              )}
            </div>
          </div>

          <div className="bg-slate-800/50 backdrop-blur-sm rounded-xl border border-slate-700/50 p-6">
            <h2 className="text-xl font-semibold text-white mb-4">CPT Codes</h2>

            {selectedCPTs.length > 0 && (
              <div className="mb-4">
                <h3 className="text-sm font-medium text-slate-300 mb-2">Selected CPT Codes</h3>
                {selectedCPTs.map((cpt) => (
                  <div key={cpt.code} className="flex items-center justify-between bg-slate-700/50 rounded-lg p-3 mb-2">
                    <div>
                      <div className="flex items-center space-x-2">
                        <span className="font-mono text-sm text-green-400">{cpt.code}</span>
                        <span className="text-xs px-2 py-0.5 bg-blue-500/20 text-blue-400 rounded-full">{cpt.category}</span>
                      </div>
                      <p className="text-sm text-slate-300">{cpt.description}</p>
                    </div>
                    <button
                      onClick={() => removeCPT(cpt.code)}
                      className="text-red-400 hover:text-red-300 transition-colors"
                    >
                      <X className="w-4 h-4" />
                    </button>
                  </div>
                ))}
              </div>
            )}

            {isLoadingCPTSuggestions && (
              <div className="flex items-center space-x-2 mb-4 text-blue-400">
                <Loader2 className="w-4 h-4 animate-spin" />
                <span className="text-sm">AI is analyzing and suggesting CPT codes...</span>
              </div>
            )}

            {aiSuggestedCPTs.length > 0 && (
              <div className="mb-4">
                <h3 className="text-sm font-medium text-slate-300 mb-2 flex items-center space-x-2">
                  <Sparkles className="w-4 h-4 text-green-400" />
                  <span>AI Suggested CPT Codes (Based on ICD & Patient History)</span>
                </h3>
                <div className="space-y-2">
                  {aiSuggestedCPTs.map((cpt, index) => (
                    <div
                      key={`ai-cpt-${cpt.code}-${index}`}
                      className="flex items-center justify-between bg-gradient-to-r from-green-900/30 to-blue-900/30 border border-green-500/20 rounded-lg p-3 hover:border-green-500/40 transition-colors cursor-pointer"
                      onClick={() => addCPT(cpt)}
                    >
                      <div className="flex-1">
                        <div className="flex items-center space-x-2 mb-1">
                          <span className="font-mono text-sm text-green-400 font-semibold">{cpt.code}</span>
                          <span className="text-xs px-2 py-0.5 bg-blue-500/30 text-blue-300 rounded-full">{cpt.category}</span>
                          {cpt.confidence && (
                            <span className="text-xs px-2 py-0.5 bg-green-500/20 text-green-400 rounded-full">
                              {cpt.confidence}% confidence
                            </span>
                          )}
                        </div>
                        <p className="text-sm text-white mb-1">{cpt.description}</p>
                        {cpt.rationale && (
                          <p className="text-xs text-slate-400 italic">{cpt.rationale}</p>
                        )}
                      </div>
                      <Plus className="w-4 h-4 text-green-400 ml-2" />
                    </div>
                  ))}
                </div>
              </div>
            )}

            {!isLoadingCPTSuggestions && aiSuggestedCPTs.length === 0 && selectedICDs.length === 0 && (
              <p className="text-slate-400 text-sm text-center py-4">
                Select ICD codes to get AI-powered CPT suggestions
              </p>
            )}
          </div>

          {showXMLPreview && (
            <div className="bg-slate-800/50 backdrop-blur-sm rounded-xl border border-slate-700/50 p-6">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-xl font-semibold text-white flex items-center space-x-2">
                  <FileCode className="w-5 h-5" />
                  <span>Generated XML Preview</span>
                </h2>
                <button
                  onClick={() => setShowXMLPreview(false)}
                  className="text-slate-400 hover:text-white transition-colors"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>
              <div className="bg-slate-900 rounded-lg p-4 overflow-x-auto">
                <pre className="text-sm text-green-400 font-mono">{generatedXML}</pre>
              </div>
            </div>
          )}
        </div>

        <div className="space-y-6">
          {aiSuggestedICDs.length > 0 && (
            <div className="bg-gradient-to-br from-blue-900/50 to-purple-900/50 backdrop-blur-sm rounded-xl border border-blue-500/30 p-6">
              <h2 className="text-xl font-semibold text-white mb-4 flex items-center space-x-2">
                <Sparkles className="w-5 h-5 text-blue-400" />
                <span>AI Suggested ICD Codes</span>
              </h2>
              <p className="text-slate-300 text-sm mb-4">Based on your clinical notes</p>

              <div className="space-y-3 max-h-96 overflow-y-auto">
                {aiSuggestedICDs.map((icd, index) => (
                  <div
                    key={`ai-${icd.code}-${index}`}
                    onClick={() => addICD(icd)}
                    className="bg-slate-800/50 rounded-lg p-3 hover:bg-slate-700/50 transition-colors cursor-pointer border border-blue-500/20"
                  >
                    <div className="flex items-center justify-between mb-2">
                      <span className="font-mono text-sm text-blue-400 font-semibold">{icd.code}</span>
                      <div className="flex items-center space-x-2">
                        {icd.confidence && (
                          <span className="text-xs px-2 py-0.5 bg-green-500/20 text-green-400 rounded-full">
                            {icd.confidence}% confidence
                          </span>
                        )}
                        <Plus className="w-4 h-4 text-blue-400" />
                      </div>
                    </div>
                    <p className="text-sm text-white mb-2">{icd.description}</p>
                    {icd.rationale && (
                      <p className="text-xs text-slate-400 italic">{icd.rationale}</p>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}



          <div className="bg-slate-800/50 backdrop-blur-sm rounded-xl border border-slate-700/50 p-6">
            <h2 className="text-xl font-semibold text-white mb-4">Patient Historical Ailments</h2>
            <div className="space-y-3">
              {patientHistory.map((history, index) => (
                <div key={index} className="border border-slate-700/50 rounded-lg p-3">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-xs text-slate-400">{history.date}</span>
                    <span className="font-mono text-xs text-blue-400">{history.icdCode}</span>
                  </div>
                  <p className="text-sm text-white font-medium mb-1">{history.diagnosis}</p>
                  <p className="text-xs text-slate-400">{history.provider}</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </main>
  );
}

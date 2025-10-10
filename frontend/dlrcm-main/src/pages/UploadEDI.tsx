import { useState, useCallback } from 'react';
import { Upload, FileText, CheckCircle, AlertTriangle, Brain, Zap } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import type { EDIFile } from '../types/claim';

export function UploadEDI() {
  const [dragActive, setDragActive] = useState(false);
  const [uploadedFiles, setUploadedFiles] = useState<EDIFile[]>([]);
  const [isProcessing, setIsProcessing] = useState(false);
  const navigate = useNavigate();

  const handleDrag = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFiles(e.dataTransfer.files);
    }
  }, []);

  const handleFiles = (files: FileList) => {
    Array.from(files).forEach(file => {
      if (file.name.endsWith('.edi') || file.name.endsWith('.x12') || file.name.endsWith('.txt')) {
        processFile(file);
      }
    });
  };

  const processFile = async (file: File) => {
    setIsProcessing(true);
    
    const newFile: EDIFile = {
      id: Math.random().toString(36).substr(2, 9),
      fileName: file.name,
      uploadDate: new Date().toISOString(),
      totalClaims: 10, // Simulated
      processedClaims: 0,
      status: 'processing',
      overallRiskScore: 0,
      estimatedSavings: 0
    };

    setUploadedFiles(prev => [...prev, newFile]);

    // Simulate processing
    for (let i = 0; i <= 10; i++) {
      await new Promise(resolve => setTimeout(resolve, 500));
      setUploadedFiles(prev => 
        prev.map(f => 
          f.id === newFile.id 
            ? { 
                ...f, 
                processedClaims: i,
                overallRiskScore: Math.floor(Math.random() * 40) + 20,
                estimatedSavings: Math.floor(Math.random() * 50000) + 10000
              }
            : f
        )
      );
    }

    setUploadedFiles(prev => 
      prev.map(f => 
        f.id === newFile.id 
          ? { ...f, status: 'completed' as const }
          : f
      )
    );
    
    setIsProcessing(false);
  };

  const viewClaims = (fileId: string) => {
    navigate(`/claims/${fileId}`);
  };

  return (
    <main className="max-w-7xl mx-auto px-6 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-white mb-2">EDI File Upload & Processing</h1>
        <p className="text-slate-300">Upload your EDI files for AI-powered claim analysis and denial risk assessment</p>
      </div>

      {/* Upload Area */}
      <div className="mb-8">
        <div
          className={`relative border-2 border-dashed rounded-2xl p-12 text-center transition-all duration-300 ${
            dragActive
              ? 'border-blue-400 bg-blue-500/10'
              : 'border-slate-600 hover:border-slate-500 bg-slate-800/30'
          }`}
          onDragEnter={handleDrag}
          onDragLeave={handleDrag}
          onDragOver={handleDrag}
          onDrop={handleDrop}
        >
          <div className="flex flex-col items-center space-y-4">
            <div className="relative">
              <Upload className="w-16 h-16 text-blue-400" />
              {isProcessing && (
                <div className="absolute -top-2 -right-2">
                  <Brain className="w-6 h-6 text-purple-400 animate-pulse" />
                </div>
              )}
            </div>
            
            <div>
              <h3 className="text-xl font-semibold text-white mb-2">
                Drop your EDI files here
              </h3>
              <p className="text-slate-400 mb-4">
                Supports .edi, .x12, and .txt formats
              </p>
              <input
                type="file"
                multiple
                accept=".edi,.x12,.txt"
                onChange={(e) => e.target.files && handleFiles(e.target.files)}
                className="hidden"
                id="file-upload"
              />
              <label
                htmlFor="file-upload"
                className="inline-flex items-center space-x-2 bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-lg cursor-pointer transition-colors"
              >
                <FileText className="w-4 h-4" />
                <span>Browse Files</span>
              </label>
            </div>
          </div>
        </div>
      </div>

      {/* AI Processing Features */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div className="bg-slate-800/50 backdrop-blur-sm rounded-xl border border-slate-700/50 p-6">
          <div className="flex items-center space-x-3 mb-4">
            <Brain className="w-6 h-6 text-purple-400" />
            <h3 className="font-semibold text-white">AI Code Validation</h3>
          </div>
          <p className="text-slate-300 text-sm">
            Advanced AI validates ICD-10 and CPT codes against current standards and identifies potential issues
          </p>
        </div>

        <div className="bg-slate-800/50 backdrop-blur-sm rounded-xl border border-slate-700/50 p-6">
          <div className="flex items-center space-x-3 mb-4">
            <AlertTriangle className="w-6 h-6 text-amber-400" />
            <h3 className="font-semibold text-white">Risk Assessment</h3>
          </div>
          <p className="text-slate-300 text-sm">
            Real-time denial risk scoring based on historical patterns and claim characteristics
          </p>
        </div>

        <div className="bg-slate-800/50 backdrop-blur-sm rounded-xl border border-slate-700/50 p-6">
          <div className="flex items-center space-x-3 mb-4">
            <Zap className="w-6 h-6 text-green-400" />
            <h3 className="font-semibold text-white">Smart Recommendations</h3>
          </div>
          <p className="text-slate-300 text-sm">
            Actionable insights and recommendations to reduce denial rates and improve approval chances
          </p>
        </div>
      </div>

      {/* Uploaded Files */}
      {uploadedFiles.length > 0 && (
        <div className="bg-slate-800/50 backdrop-blur-sm rounded-xl border border-slate-700/50 p-6">
          <h3 className="text-lg font-semibold text-white mb-6">Processing Status</h3>
          
          <div className="space-y-4">
            {uploadedFiles.map((file) => (
              <div key={file.id} className="border border-slate-700/50 rounded-lg p-4">
                <div className="flex items-center justify-between mb-3">
                  <div className="flex items-center space-x-3">
                    <FileText className="w-5 h-5 text-blue-400" />
                    <span className="font-medium text-white">{file.fileName}</span>
                    {file.status === 'completed' && (
                      <CheckCircle className="w-4 h-4 text-green-400" />
                    )}
                  </div>
                  
                  <div className="flex items-center space-x-4">
                    <span className="text-sm text-slate-400">
                      {file.processedClaims}/{file.totalClaims} claims
                    </span>
                    {file.status === 'completed' && (
                      <button
                        onClick={() => viewClaims(file.id)}
                        className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg text-sm transition-colors"
                      >
                        View Claims
                      </button>
                    )}
                  </div>
                </div>

                {/* Progress Bar */}
                <div className="w-full bg-slate-700 rounded-full h-2 mb-3">
                  <div
                    className="h-2 rounded-full bg-gradient-to-r from-blue-400 to-blue-600 transition-all duration-500"
                    style={{ width: `${(file.processedClaims / file.totalClaims) * 100}%` }}
                  ></div>
                </div>

                {/* Results */}
                {file.status === 'completed' && (
                  <div className="grid grid-cols-3 gap-4 text-center">
                    <div>
                      <p className="text-lg font-bold text-white">{file.overallRiskScore}%</p>
                      <p className="text-xs text-slate-400">Avg Risk Score</p>
                    </div>
                    <div>
                      <p className="text-lg font-bold text-green-400">${file.estimatedSavings.toLocaleString()}</p>
                      <p className="text-xs text-slate-400">Est. Savings</p>
                    </div>
                    <div>
                      <p className="text-lg font-bold text-blue-400">{file.totalClaims}</p>
                      <p className="text-xs text-slate-400">Total Claims</p>
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
    </main>
  );
}
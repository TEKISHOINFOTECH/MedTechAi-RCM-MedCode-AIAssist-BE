"""
MedTechAI RCM - Medical Code Validation Streamlit App
Professional UI for medical code upload, validation, and analysis
"""
import streamlit as st
import pandas as pd
import json
import time
from datetime import datetime
from pathlib import Path
import io

# Page configuration
st.set_page_config(
    page_title="MedTechAI RCM - Medical Code Validation",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for professional styling
st.markdown("""
<style>
    /* Main container styling */
    .main {
        padding: 2rem;
    }
    
    /* Header styling */
    .header-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    .header-title {
        color: white;
        font-size: 2.5rem;
        font-weight: 700;
        margin: 0;
        text-align: center;
    }
    
    .header-subtitle {
        color: rgba(255, 255, 255, 0.9);
        font-size: 1.1rem;
        margin-top: 0.5rem;
        text-align: center;
    }
    
    /* Upload box styling */
    .upload-box {
        border: 2px dashed #667eea;
        border-radius: 10px;
        padding: 3rem;
        text-align: center;
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.05) 0%, rgba(118, 75, 162, 0.05) 100%);
        margin: 2rem 0;
        transition: all 0.3s ease;
    }
    
    .upload-box:hover {
        border-color: #764ba2;
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);
    }
    
    /* Card styling */
    .info-card {
        background: white;
        border-radius: 10px;
        padding: 1.5rem;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        margin-bottom: 1rem;
        border-left: 4px solid #667eea;
    }
    
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
        padding: 1.5rem;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    .metric-value {
        font-size: 2.5rem;
        font-weight: 700;
        margin: 0.5rem 0;
    }
    
    .metric-label {
        font-size: 0.9rem;
        opacity: 0.9;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    /* Status badges */
    .status-badge {
        padding: 0.4rem 1rem;
        border-radius: 20px;
        font-weight: 600;
        display: inline-block;
        margin: 0.2rem;
    }
    
    .status-approved {
        background: #10b981;
        color: white;
    }
    
    .status-review {
        background: #f59e0b;
        color: white;
    }
    
    .status-rejected {
        background: #ef4444;
        color: white;
    }
    
    /* Progress bar */
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
    }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.6rem 2rem;
        border-radius: 5px;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(102, 126, 234, 0.3);
    }
    
    /* Expander styling */
    .streamlit-expanderHeader {
        background: #f8f9fa;
        border-radius: 5px;
        font-weight: 600;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        padding: 1rem 2rem;
        font-weight: 600;
    }
    
    /* File uploader */
    .uploadedFile {
        border: 1px solid #e5e7eb;
        border-radius: 5px;
        padding: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'uploaded_files' not in st.session_state:
    st.session_state.uploaded_files = []
if 'processing_results' not in st.session_state:
    st.session_state.processing_results = None
if 'validation_history' not in st.session_state:
    st.session_state.validation_history = []

def render_header():
    """Render the application header"""
    st.markdown("""
    <div class="header-container">
        <h1 class="header-title">🏥 MedTechAI RCM</h1>
        <p class="header-subtitle">AI-Powered Medical Code Validation & Claim Analysis</p>
    </div>
    """, unsafe_allow_html=True)

def render_sidebar():
    """Render the sidebar with settings and information"""
    with st.sidebar:
        st.image("https://via.placeholder.com/200x80/667eea/ffffff?text=MedTechAI", use_container_width=True)
        
        st.markdown("---")
        
        st.subheader("⚙️ Settings")
        
        # Processing mode
        processing_mode = st.selectbox(
            "Processing Mode",
            ["Parallel (Faster)", "Sequential (Detailed)"],
            help="Choose between parallel execution for speed or sequential for detailed analysis"
        )
        
        # Clinical setting
        clinical_setting = st.selectbox(
            "Clinical Setting",
            ["Outpatient", "Inpatient", "Emergency Department", "Urgent Care", "Ambulatory Surgery"],
            help="Select the clinical setting for context-aware validation"
        )
        
        # Specialty
        specialty = st.selectbox(
            "Medical Specialty",
            ["General Practice", "Cardiology", "Orthopedics", "Neurology", "Oncology", 
             "Pediatrics", "Surgery", "Internal Medicine", "Other"],
            help="Medical specialty for specialized coding rules"
        )
        
        # Payer type
        payer_type = st.selectbox(
            "Payer Type",
            ["Commercial", "Medicare", "Medicaid", "Private", "Workers Comp", "Other"],
            help="Insurance payer type for coverage-specific validation"
        )
        
        # Confidence threshold
        confidence_threshold = st.slider(
            "Confidence Threshold",
            min_value=0.0,
            max_value=1.0,
            value=0.85,
            step=0.05,
            help="Minimum confidence for automatic approval"
        )
        
        st.markdown("---")
        
        # Statistics
        st.subheader("📊 Session Statistics")
        st.metric("Files Processed", len(st.session_state.validation_history))
        st.metric("Total Validations", len(st.session_state.validation_history))
        
        if st.session_state.validation_history:
            approved = sum(1 for v in st.session_state.validation_history if v.get('approved', False))
            st.metric("Approval Rate", f"{(approved/len(st.session_state.validation_history)*100):.1f}%")
        
        st.markdown("---")
        
        # Help
        with st.expander("ℹ️ Help & Info"):
            st.markdown("""
            **Supported File Formats:**
            - EDI/X12 files (*.edi, *.x12)
            - HL7 messages (*.hl7)
            - CSV files (*.csv)
            - PDF documents (*.pdf)
            - Text files (*.txt)
            
            **Features:**
            - AI-powered code validation
            - Real-time denial risk assessment
            - RAG-enhanced medical coding guidelines
            - Parallel/sequential processing
            - Comprehensive validation reports
            """)
        
        # Store settings in session state
        st.session_state.settings = {
            'processing_mode': 'parallel' if 'Parallel' in processing_mode else 'sequential',
            'clinical_setting': clinical_setting,
            'specialty': specialty,
            'payer_type': payer_type,
            'confidence_threshold': confidence_threshold
        }

def render_upload_section():
    """Render the file upload section"""
    st.markdown("## 📤 EDI File Upload & Processing")
    st.markdown("Upload your EDI files for AI-powered claim analysis and denial risk assessment")
    
    # Create tabs for different input methods
    tab1, tab2, tab3 = st.tabs(["📁 File Upload", "✍️ Manual Entry", "📋 Batch Upload"])
    
    with tab1:
        st.markdown('<div class="upload-box">', unsafe_allow_html=True)
        
        uploaded_files = st.file_uploader(
            "Drop your files here or click to browse",
            type=['edi', 'x12', 'hl7', 'csv', 'pdf', 'txt'],
            accept_multiple_files=True,
            help="Supported formats: EDI, HL7, CSV, PDF, TXT"
        )
        
        if uploaded_files:
            st.success(f"✅ {len(uploaded_files)} file(s) uploaded successfully!")
            
            # Display uploaded files
            for idx, file in enumerate(uploaded_files):
                col1, col2, col3 = st.columns([3, 1, 1])
                with col1:
                    st.text(f"📄 {file.name}")
                with col2:
                    st.text(f"{file.size / 1024:.1f} KB")
                with col3:
                    st.text(file.type if file.type else "Unknown")
            
            st.session_state.uploaded_files = uploaded_files
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with tab2:
        st.markdown("### Enter Clinical Notes Manually")
        
        clinical_notes = st.text_area(
            "Clinical Notes (SOAP Format)",
            height=300,
            placeholder="""Example:

CHIEF COMPLAINT: Chest pain

SUBJECTIVE:
67-year-old male presents with severe substernal chest pain...

OBJECTIVE:
Vitals: BP 156/92, HR 98, RR 22, O2 Sat 94%
ECG: ST elevation in leads II, III, aVF

ASSESSMENT:
1. Acute ST-elevation myocardial infarction (STEMI), inferior wall
2. Hypertension, uncontrolled

PLAN:
1. Activate cath lab for emergent cardiac catheterization
2. Aspirin 325mg, Plavix 600mg loading dose
...
""",
            help="Enter clinical documentation for AI analysis"
        )
        
        # Manual code entry
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**ICD-10 Codes**")
            manual_icd = st.text_area(
                "Enter ICD codes (one per line)",
                height=150,
                placeholder="I21.19\nI10\nE78.5",
                help="Enter diagnosis codes for validation"
            )
        
        with col2:
            st.markdown("**CPT/HCPCS Codes**")
            manual_cpt = st.text_area(
                "Enter CPT codes (one per line)",
                height=150,
                placeholder="99285\n93458\n93000",
                help="Enter procedure codes for validation"
            )
        
        if clinical_notes or manual_icd or manual_cpt:
            st.session_state.manual_entry = {
                'clinical_notes': clinical_notes,
                'manual_icd': [code.strip() for code in manual_icd.split('\n') if code.strip()],
                'manual_cpt': [code.strip() for code in manual_cpt.split('\n') if code.strip()]
            }
    
    with tab3:
        st.markdown("### Batch Upload")
        st.info("📦 Upload multiple claim files for batch processing")
        
        batch_folder = st.text_input(
            "Folder Path",
            placeholder="/path/to/claims/folder",
            help="Enter the path to folder containing claim files"
        )
        
        if batch_folder:
            st.warning("⚠️ Batch processing will be available after backend integration")

def process_files_mock(files, settings):
    """Mock processing function - will be replaced with actual API calls"""
    time.sleep(2)  # Simulate processing
    
    # Generate mock results
    results = {
        'metadata': {
            'pipeline_version': '2.0-enhanced',
            'execution_mode': settings['processing_mode'],
            'processing_time_seconds': 12.5,
            'timestamp': datetime.now().isoformat()
        },
        'stages': {
            'parsing': {
                'status': 'success',
                'files_parsed': len(files),
                'total_rows': len(files) * 5
            },
            'rag_retrieval': {
                'status': 'success',
                'documents_retrieved': 8,
                'relevance_scores': [0.92, 0.88, 0.85, 0.81, 0.78, 0.75, 0.72, 0.68]
            },
            'code_generation': {
                'status': 'success',
                'icd_codes_generated': 4,
                'cpt_codes_generated': 6,
                'avg_icd_confidence': 0.94,
                'avg_cpt_confidence': 0.89
            },
            'validation': {
                'status': 'success',
                'overall_accuracy': 0.92,
                'denial_risk': 0.18,
                'discrepancies': 2
            }
        },
        'ai_suggested_codes': {
            'icd': [
                {'code': 'I21.19', 'description': 'STEMI involving other coronary artery of inferior wall', 'confidence': 0.96},
                {'code': 'I10', 'description': 'Essential hypertension', 'confidence': 0.94},
                {'code': 'E78.5', 'description': 'Hyperlipidemia, unspecified', 'confidence': 0.91}
            ],
            'cpt': [
                {'code': '99285', 'description': 'Emergency department visit, high complexity', 'probability': 0.95},
                {'code': '93458', 'description': 'Catheter placement in coronary artery', 'probability': 0.92},
                {'code': '93000', 'description': 'Electrocardiogram, routine ECG', 'probability': 0.98},
                {'code': '83036', 'description': 'Hemoglobin; glycosylated (A1C)', 'probability': 0.88}
            ]
        },
        'validation_details': {
            'exact_matches': 3,
            'partial_matches': 1,
            'missing_codes': 1,
            'incorrect_codes': 0,
            'discrepancies': [
                {
                    'type': 'missing_modifier',
                    'code': '93458',
                    'severity': 'medium',
                    'issue': 'Missing modifier 26 for professional component',
                    'resolution': 'Add modifier 26 if only interpretation performed',
                    'financial_impact': '$250'
                },
                {
                    'type': 'specificity',
                    'code': 'I21.19',
                    'severity': 'low',
                    'issue': 'Could specify laterality if documented',
                    'resolution': 'Review documentation for right/left specification',
                    'financial_impact': '$0'
                }
            ]
        },
        'executive_summary': {
            'claim_status': 'clean',
            'overall_confidence': 0.92,
            'estimated_revenue': '$2,450',
            'revenue_at_risk': '$250',
            'denial_probability': 0.18,
            'key_findings': [
                'High confidence match on primary diagnosis codes',
                'Minor modifier discrepancy on cardiac catheterization',
                'All codes supported by documentation',
                'Compliance check passed'
            ]
        },
        'priority_actions': [
            {
                'priority': 'P1',
                'action': 'Add modifier 26 to CPT 93458',
                'impact': 'medium',
                'effort': 'minutes',
                'owner': 'Medical Coder'
            },
            {
                'priority': 'P2',
                'action': 'Verify documentation supports all ICD codes',
                'impact': 'low',
                'effort': 'minutes',
                'owner': 'Physician'
            }
        ],
        'final_decision': {
            'approved': True,
            'confidence': 0.92,
            'denial_risk': 0.18,
            'recommendation': 'Approve for submission after addressing P1 action',
            'requires_manual_review': False
        }
    }
    
    return results

def render_processing_section():
    """Render the processing and results section"""
    st.markdown("## 🔄 Processing & Validation")
    
    # Check if we have files or manual entry
    has_files = len(st.session_state.get('uploaded_files', [])) > 0
    has_manual = 'manual_entry' in st.session_state and st.session_state.manual_entry.get('clinical_notes')
    
    if not has_files and not has_manual:
        st.info("👆 Please upload files or enter clinical notes manually to begin processing")
        return
    
    # Processing controls
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("🚀 Process & Validate", use_container_width=True):
            with st.spinner("🔄 Processing files and validating codes..."):
                # Progress bar
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                stages = [
                    "Parsing documents...",
                    "Retrieving medical guidelines...",
                    "Generating ICD codes...",
                    "Generating CPT codes...",
                    "Validating codes...",
                    "Checking compliance...",
                    "Generating summary..."
                ]
                
                for i, stage in enumerate(stages):
                    status_text.text(stage)
                    progress_bar.progress((i + 1) / len(stages))
                    time.sleep(0.3)
                
                # Process files (mock for now)
                files = st.session_state.get('uploaded_files', [])
                settings = st.session_state.get('settings', {})
                results = process_files_mock(files, settings)
                
                st.session_state.processing_results = results
                st.session_state.validation_history.append(results)
                
                status_text.empty()
                progress_bar.empty()
                st.success("✅ Processing complete!")
    
    with col2:
        if st.button("📊 View Report", use_container_width=True):
            st.info("Report viewing will be available after processing")
    
    with col3:
        if st.button("💾 Export Results", use_container_width=True):
            if st.session_state.processing_results:
                # Create downloadable JSON
                json_str = json.dumps(st.session_state.processing_results, indent=2)
                st.download_button(
                    "📥 Download JSON",
                    json_str,
                    file_name=f"validation_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json"
                )
            else:
                st.warning("No results to export")
    
    with col4:
        if st.button("🔄 Reset", use_container_width=True):
            st.session_state.uploaded_files = []
            st.session_state.processing_results = None
            if 'manual_entry' in st.session_state:
                del st.session_state.manual_entry
            st.rerun()

def render_results_section():
    """Render the results and analytics section"""
    if not st.session_state.processing_results:
        return
    
    results = st.session_state.processing_results
    
    st.markdown("---")
    st.markdown("## 📈 Validation Results")
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-label">Overall Confidence</div>
            <div class="metric-value">{:.0%}</div>
        </div>
        """.format(results['final_decision']['confidence']), unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-label">Denial Risk</div>
            <div class="metric-value">{:.0%}</div>
        </div>
        """.format(results['final_decision']['denial_risk']), unsafe_allow_html=True)
    
    with col3:
        revenue = results['executive_summary']['estimated_revenue']
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Estimated Revenue</div>
            <div class="metric-value">{revenue}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        risk_revenue = results['executive_summary']['revenue_at_risk']
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Revenue at Risk</div>
            <div class="metric-value">{risk_revenue}</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Decision status
    decision = results['final_decision']
    status_class = 'status-approved' if decision['approved'] else 'status-review'
    status_text = '✅ APPROVED' if decision['approved'] else '⚠️ REQUIRES REVIEW'
    
    st.markdown(f"""
    <div class="info-card">
        <h3>Decision Status</h3>
        <span class="status-badge {status_class}">{status_text}</span>
        <p style="margin-top: 1rem;"><strong>Recommendation:</strong> {decision['recommendation']}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Tabs for detailed results
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🎯 AI Suggested Codes",
        "⚠️ Discrepancies",
        "📋 Priority Actions",
        "📊 Key Findings",
        "🔍 Detailed Analysis"
    ])
    
    with tab1:
        render_suggested_codes(results['ai_suggested_codes'])
    
    with tab2:
        render_discrepancies(results['validation_details']['discrepancies'])
    
    with tab3:
        render_priority_actions(results['priority_actions'])
    
    with tab4:
        render_key_findings(results['executive_summary']['key_findings'])
    
    with tab5:
        render_detailed_analysis(results)

def render_suggested_codes(codes):
    """Render AI suggested codes"""
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### ICD-10 Diagnosis Codes")
        icd_df = pd.DataFrame(codes['icd'])
        icd_df['confidence'] = icd_df['confidence'].apply(lambda x: f"{x:.0%}")
        st.dataframe(icd_df, use_container_width=True, hide_index=True)
    
    with col2:
        st.markdown("### CPT/HCPCS Procedure Codes")
        cpt_df = pd.DataFrame(codes['cpt'])
        cpt_df['probability'] = cpt_df['probability'].apply(lambda x: f"{x:.0%}")
        st.dataframe(cpt_df, use_container_width=True, hide_index=True)

def render_discrepancies(discrepancies):
    """Render code discrepancies"""
    if not discrepancies:
        st.success("✅ No discrepancies found!")
        return
    
    for disc in discrepancies:
        severity_color = {
            'critical': '🔴',
            'high': '🟠',
            'medium': '🟡',
            'low': '🟢'
        }.get(disc['severity'], '⚪')
        
        with st.expander(f"{severity_color} {disc['type'].replace('_', ' ').title()} - {disc['code']}"):
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.markdown(f"**Issue:** {disc['issue']}")
                st.markdown(f"**Resolution:** {disc['resolution']}")
            
            with col2:
                st.metric("Financial Impact", disc['financial_impact'])
                st.metric("Severity", disc['severity'].upper())

def render_priority_actions(actions):
    """Render priority actions"""
    for action in actions:
        priority_color = {
            'P0': '🔴',
            'P1': '🟠',
            'P2': '🟡',
            'P3': '🟢'
        }.get(action['priority'], '⚪')
        
        st.markdown(f"""
        <div class="info-card">
            <h4>{priority_color} {action['priority']} - {action['action']}</h4>
            <p><strong>Owner:</strong> {action['owner']} | <strong>Impact:</strong> {action['impact']} | <strong>Effort:</strong> {action['effort']}</p>
        </div>
        """, unsafe_allow_html=True)

def render_key_findings(findings):
    """Render key findings"""
    for finding in findings:
        st.markdown(f"✓ {finding}")

def render_detailed_analysis(results):
    """Render detailed analysis"""
    st.markdown("### Pipeline Execution Details")
    
    # Metadata
    meta = results['metadata']
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Pipeline Version", meta['pipeline_version'])
    with col2:
        st.metric("Execution Mode", meta['execution_mode'].title())
    with col3:
        st.metric("Processing Time", f"{meta['processing_time_seconds']:.2f}s")
    
    # Stage details
    st.markdown("### Stage Results")
    for stage_name, stage_data in results['stages'].items():
        with st.expander(f"📍 {stage_name.replace('_', ' ').title()}"):
            st.json(stage_data)

def render_history():
    """Render validation history"""
    if not st.session_state.validation_history:
        return
    
    st.markdown("---")
    st.markdown("## 📚 Validation History")
    
    history_data = []
    for idx, result in enumerate(reversed(st.session_state.validation_history)):
        history_data.append({
            'ID': f"VAL-{len(st.session_state.validation_history) - idx:04d}",
            'Timestamp': result['metadata']['timestamp'][:19],
            'Confidence': f"{result['final_decision']['confidence']:.0%}",
            'Denial Risk': f"{result['final_decision']['denial_risk']:.0%}",
            'Status': '✅ Approved' if result['final_decision']['approved'] else '⚠️ Review',
            'Revenue': result['executive_summary']['estimated_revenue']
        })
    
    df = pd.DataFrame(history_data)
    st.dataframe(df, use_container_width=True, hide_index=True)

def main():
    """Main application"""
    render_header()
    render_sidebar()
    render_upload_section()
    render_processing_section()
    render_results_section()
    render_history()
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #6b7280; padding: 2rem;">
        <p>MedTechAI RCM - Medical Code Validation Platform v2.0</p>
        <p style="font-size: 0.9rem;">© 2024 MedTechAI. All rights reserved. | Powered by AI & RAG Technology</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()


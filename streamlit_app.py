import streamlit as st
import json
from groq import Groq
import PyPDF2
import matplotlib.pyplot as plt
from fpdf import FPDF
import io
from datetime import datetime

# Get API key
api_key = st.secrets["GROQ_API_KEY"]

# Initialize Groq
client = Groq(api_key=api_key)

# Page config
st.set_page_config(
    page_title="Clinical Intelligence Assistant",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom styling
st.markdown("""
<style>
    * {
        margin: 0;
        padding: 0;
    }
    
    html, body, [data-testid="stAppViewContainer"] {
        background-color: #1a2a4a !important;
        color: #ffffff !important;
    }
    
    [data-testid="stMainBlockContainer"] {
        background-color: #1a2a4a !important;
        padding-left: 2rem !important;
        padding-right: 2rem !important;
    }
    
    [data-testid="stSidebar"] {
        background-color: #0f1823 !important;
        border-right: 2px solid #2d5a8c !important;
    }
    
    [data-testid="stSidebar"] {
        color: #ffffff !important;
    }
    
    [data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] h4,
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] span,
    [data-testid="stSidebar"] div {
        color: #ffffff !important;
    }
    
    h1 {
        color: #ffffff !important;
        font-weight: 700 !important;
        font-size: 2.5rem !important;
        margin-bottom: 0.5rem !important;
    }
    
    h2 {
        color: #ffffff !important;
        font-size: 1.3rem !important;
        font-weight: 700 !important;
        padding-bottom: 0.75rem !important;
        border-bottom: 3px solid #2d5a8c !important;
        margin-top: 1.5rem !important;
        margin-bottom: 1rem !important;
    }
    
    p {
        color: #ffffff !important;
    }
    
    .patient-card {
        background: #ffffff !important;
        padding: 2rem;
        border-radius: 0.75rem;
        margin-bottom: 1.5rem;
        border-top: 5px solid #2d5a8c;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
    }
    
    .patient-info {
        text-align: center;
    }
    
    .patient-label {
        font-size: 0.875rem;
        color: #2d5a8c !important;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 0.5rem;
        font-weight: 600;
    }
    
    .patient-value {
        font-size: 1.75rem;
        font-weight: 700;
        color: #1a2a4a !important;
    }
    
    .risk-score-card {
        background: linear-gradient(135deg, #2d5a8c 0%, #1e3f5a 100%);
        padding: 2rem;
        border-radius: 0.75rem;
        margin-bottom: 1.5rem;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
        border: 2px solid #5ba3d0;
    }
    
    .risk-score-label {
        font-size: 0.875rem;
        color: #9bc5e6;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 0.5rem;
        font-weight: 600;
    }
    
    .risk-score-value {
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }
    
    .risk-high {
        color: #ff6b6b;
    }
    
    .risk-medium {
        color: #ffd93d;
    }
    
    .risk-low {
        color: #51cf66;
    }
    
    .clinical-summary {
        background: #ffffff !important;
        border-left: 5px solid #2d5a8c;
        padding: 1.5rem;
        border-radius: 0.5rem;
        color: #1a2a4a !important;
        line-height: 1.8;
        font-size: 1rem;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
    }
    
    .medications-section {
        border-left: none !important;
        padding: 0 !important;
        background: transparent !important;
        box-shadow: none !important;
        margin-bottom: 0 !important;
    }
    
    .med-item {
        padding: 0.5rem 0;
        border-bottom: none;
        font-weight: 500;
        color: #ffffff !important;
    }
    
    .med-item:last-child {
        border-bottom: none;
    }
    
    .risk-item {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        padding: 0.75rem 0;
        color: #ffffff !important;
        border-bottom: 1px solid #2d5a8c;
        font-weight: 500;
        font-size: 0.95rem;
    }
    
    .risk-item:last-child {
        border-bottom: none;
    }
    
    .risk-dot {
        width: 12px;
        height: 12px;
        border-radius: 50%;
        flex-shrink: 0;
    }
    
    .risk-dot-high {
        background-color: #ff6b6b;
    }
    
    .risk-dot-low {
        background-color: #51cf66;
    }
    
    .steps-list li {
        padding: 0.75rem 0;
        color: #ffffff !important;
        padding-left: 1.5rem;
        position: relative;
        font-weight: 500;
        font-size: 0.95rem;
    }
    
    .steps-list li:before {
        content: "→";
        position: absolute;
        left: 0;
        color: #5ba3d0;
        font-weight: bold;
        font-size: 1.2rem;
    }
    
    .vital-item {
        padding: 0.75rem 0;
        display: flex;
        justify-content: space-between;
        border-bottom: 1px solid #2d5a8c;
        color: #ffffff !important;
    }
    
    .vital-item:last-child {
        border-bottom: none;
    }
    
    .vital-label {
        color: #9bc5e6 !important;
        font-weight: 500;
    }
    
    .vital-value {
        color: #ffffff !important;
        font-weight: 700;
    }
    
    .vital-critical {
        color: #ff6b6b !important;
    }
    
    .confidence-value {
        font-size: 2.5rem;
        font-weight: 700;
        color: #5ba3d0 !important;
        margin-bottom: 1rem;
    }
    
    .confidence-bar {
        height: 10px;
        background: #0f1823;
        border-radius: 5px;
        overflow: hidden;
        margin-bottom: 0.5rem;
        border: 1px solid #2d5a8c;
    }
    
    .confidence-fill {
        height: 100%;
        background: linear-gradient(90deg, #5ba3d0 0%, #2d5a8c 100%);
        border-radius: 4px;
    }
    
    .success-msg {
        background: #1a5f3f;
        border-left: 5px solid #51cf66;
        padding: 1rem;
        border-radius: 0.5rem;
        color: #51cf66 !important;
        margin-bottom: 1rem;
        font-weight: 600;
    }
    
    .critical-alert {
        background: #5f1a1a;
        border-left: 5px solid #ff6b6b;
        padding: 1rem;
        border-radius: 0.5rem;
        color: #ff6b6b !important;
        margin-bottom: 1rem;
        font-weight: 600;
    }
    
    .warning-alert {
        background: #5f4a1a;
        border-left: 5px solid #ffd93d;
        padding: 1rem;
        border-radius: 0.5rem;
        color: #ffd93d !important;
        margin-bottom: 1rem;
        font-weight: 600;
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #2d5a8c 0%, #1e3f5a 100%) !important;
        color: white !important;
        border: none;
        border-radius: 0.5rem;
        padding: 0.875rem 2rem;
        font-weight: 700 !important;
        width: 100%;
        font-size: 1rem;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #5ba3d0 0%, #2d5a8c 100%) !important;
        box-shadow: 0 4px 12px rgba(93, 163, 208, 0.4);
    }
    
    [data-testid="stRadio"] {
        color: #ffffff !important;
    }
    
    [data-testid="stRadio"] label {
        color: #ffffff !important;
    }
    
    [data-testid="stRadio"] span {
        color: #ffffff !important;
    }
    
    [data-testid="stTextArea"] textarea {
        background-color: #0f1823 !important;
        color: #ffffff !important;
        border: 2px solid #2d5a8c !important;
    }
    
    hr {
        border-color: #2d5a8c !important;
    }
    
    .footer {
        text-align: center;
        padding: 2rem 0;
        border-top: 2px solid #2d5a8c;
        color: #9bc5e6;
        font-size: 0.875rem;
        margin-top: 3rem;
    }
    
    [data-testid="stExpander"] {
        background-color: #0f1823 !important;
        border: 1px solid #2d5a8c !important;
    }
    
    [data-testid="stExpander"] button {
        color: #ffffff !important;
    }
    
    [data-testid="stExpander"] button span {
        color: #ffffff !important;
    }
    
</style>
""", unsafe_allow_html=True)

# ============================================================================
# CLINICAL DECISION SUPPORT FUNCTIONS
# ============================================================================

def calculate_risk_score(patient_data):
    """Calculate overall risk score (0-1)"""
    risk_points = 0
    max_points = 0
    
    # Check vital signs
    vitals = patient_data.get("vital_signs", {})
    if vitals:
        bp = vitals.get("blood_pressure", "")
        hr = vitals.get("heart_rate", "")
        temp = vitals.get("temperature", "")
        
        # Parse BP
        if bp and "/" in str(bp):
            try:
                systolic = int(bp.split("/")[0])
                if systolic > 180 or systolic < 90:
                    risk_points += 2
            except:
                pass
        
        # Parse HR
        if hr:
            try:
                hr_val = int(''.join(filter(str.isdigit, str(hr))))
                if hr_val > 120 or hr_val < 60:
                    risk_points += 1.5
            except:
                pass
    
    max_points += 3.5
    
    # Check risk flags
    risk_flags = patient_data.get("risk_flags", [])
    if risk_flags:
        risk_points += len(risk_flags) * 1.5
    max_points += 10
    
    # Check medications (polypharmacy)
    meds = patient_data.get("medications", [])
    if len(meds) > 5:
        risk_points += 1
    max_points += 1
    
    # Normalize to 0-1
    if max_points > 0:
        score = min(risk_points / max_points, 1.0)
    else:
        score = 0
    
    return score

def get_risk_level(score):
    """Convert risk score to level"""
    if score >= 0.7:
        return "🔴 HIGH", "risk-high"
    elif score >= 0.4:
        return "🟠 MEDIUM", "risk-medium"
    else:
        return "🟢 LOW", "risk-low"

def check_critical_values(patient_data):
    """Check for critical vital signs"""
    alerts = []
    vitals = patient_data.get("vital_signs", {})
    
    if vitals:
        bp = vitals.get("blood_pressure", "")
        hr = vitals.get("heart_rate", "")
        temp = vitals.get("temperature", "")
        
        # Critical BP
        if bp and "/" in str(bp):
            try:
                sys_val = int(bp.split("/")[0])
                dia_val = int(bp.split("/")[1])
                if sys_val > 180 or dia_val > 120:
                    alerts.append("⚠️ CRITICAL: Blood Pressure elevated (>180/120)")
                elif sys_val < 90 or dia_val < 60:
                    alerts.append("⚠️ CRITICAL: Blood Pressure low (<90/60) - Hypotension")
            except:
                pass
        
        # Critical HR
        if hr:
            try:
                hr_val = int(''.join(filter(str.isdigit, str(hr))))
                if hr_val > 120:
                    alerts.append("⚠️ CRITICAL: Heart Rate elevated (>120 bpm) - Tachycardia")
                elif hr_val < 60:
                    alerts.append("⚠️ CRITICAL: Heart Rate low (<60 bpm) - Bradycardia")
            except:
                pass
        
        # Critical Temperature
        if temp:
            try:
                temp_val = float(''.join(filter(lambda x: x.isdigit() or x == '.', str(temp))))
                if temp_val > 39.5:
                    alerts.append("⚠️ CRITICAL: High Fever (>39.5°C/103.1°F)")
                elif temp_val < 36:
                    alerts.append("⚠️ CRITICAL: Hypothermia (<36°C/96.8°F)")
            except:
                pass
    
    return alerts

def check_drug_interactions(medications):
    """Check for common drug interactions"""
    interactions = []
    
    # Common interaction pairs
    interaction_database = {
        ("metformin", "contrast"): "Metformin + Contrast: Risk of renal impairment",
        ("warfarin", "aspirin"): "Warfarin + Aspirin: Increased bleeding risk",
        ("lisinopril", "potassium"): "ACE Inhibitor + Potassium: Hyperkalemia risk",
        ("nsaid", "lisinopril"): "NSAID + ACE Inhibitor: Renal impairment risk",
        ("statin", "fibrate"): "Statin + Fibrate: Myopathy risk",
    }
    
    med_lower = [med.lower() for med in medications]
    
    for (drug1, drug2), warning in interaction_database.items():
        if any(drug1 in med for med in med_lower) and any(drug2 in med for med in med_lower):
            interactions.append(f"⚠️ {warning}")
    
    return interactions

def create_vital_chart(vital_signs):
    """Create a chart of vital signs"""
    fig, ax = plt.subplots(figsize=(10, 4))
    fig.patch.set_facecolor('#1a2a4a')
    ax.set_facecolor('#0f1823')
    
    vitals_display = []
    values = []
    colors = []
    
    if vital_signs.get("blood_pressure"):
        vitals_display.append("BP (Systolic)")
        try:
            sys = int(vital_signs["blood_pressure"].split("/")[0])
            values.append(sys)
            colors.append('#5ba3d0' if sys < 140 else '#ff6b6b')
        except:
            pass
    
    if vital_signs.get("heart_rate"):
        vitals_display.append("HR (bpm)")
        try:
            hr = int(''.join(filter(str.isdigit, str(vital_signs["heart_rate"]))))
            values.append(hr)
            colors.append('#5ba3d0' if 60 <= hr <= 100 else '#ff6b6b')
        except:
            pass
    
    if vitals_display:
        bars = ax.bar(vitals_display, values, color=colors, edgecolor='#2d5a8c', linewidth=2)
        ax.set_ylabel('Value', color='#ffffff', fontweight='bold')
        ax.tick_params(colors='#ffffff')
        ax.spines['bottom'].set_color('#2d5a8c')
        ax.spines['left'].set_color('#2d5a8c')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        
        return fig
    
    return None

def generate_pdf_report(patient_data, risk_level, critical_alerts, drug_interactions):
    """Generate PDF report"""
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.set_text_color(45, 90, 140)
    pdf.cell(0, 10, "Clinical Intelligence Report", ln=True, align="C")
    
    pdf.set_font("Arial", "", 10)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 5, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}", ln=True, align="C")
    
    pdf.ln(5)
    
    # Patient Info
    pdf.set_font("Arial", "B", 12)
    pdf.set_text_color(45, 90, 140)
    pdf.cell(0, 8, "PATIENT SUMMARY", ln=True)
    
    pdf.set_font("Arial", "", 10)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 6, f"Name: {patient_data.get('patient_name', 'N/A')}", ln=True)
    pdf.cell(0, 6, f"Age: {patient_data.get('age', 'N/A')}", ln=True)
    pdf.cell(0, 6, f"Gender: {patient_data.get('gender', 'N/A')}", ln=True)
    
    pdf.ln(3)
    
    # Risk Score
    pdf.set_font("Arial", "B", 12)
    pdf.set_text_color(45, 90, 140)
    pdf.cell(0, 8, "RISK ASSESSMENT", ln=True)
    
    pdf.set_font("Arial", "", 10)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 6, f"Risk Level: {risk_level[0]}", ln=True)
    
    pdf.ln(3)
    
    # Critical Alerts
    if critical_alerts:
        pdf.set_font("Arial", "B", 12)
        pdf.set_text_color(255, 107, 107)
        pdf.cell(0, 8, "CRITICAL ALERTS", ln=True)
        
        pdf.set_font("Arial", "", 10)
        pdf.set_text_color(0, 0, 0)
        for alert in critical_alerts:
            pdf.multi_cell(0, 6, f"• {alert}")
        
        pdf.ln(3)
    
    # Drug Interactions
    if drug_interactions:
        pdf.set_font("Arial", "B", 12)
        pdf.set_text_color(255, 217, 61)
        pdf.cell(0, 8, "DRUG INTERACTIONS", ln=True)
        
        pdf.set_font("Arial", "", 10)
        pdf.set_text_color(0, 0, 0)
        for interaction in drug_interactions:
            pdf.multi_cell(0, 6, f"• {interaction}")
        
        pdf.ln(3)
    
    # Clinical Summary
    pdf.set_font("Arial", "B", 12)
    pdf.set_text_color(45, 90, 140)
    pdf.cell(0, 8, "CLINICAL SUMMARY", ln=True)
    
    pdf.set_font("Arial", "", 10)
    pdf.set_text_color(0, 0, 0)
    summary = patient_data.get("clinical_summary", "N/A")
    pdf.multi_cell(0, 6, summary)
    
    pdf.ln(3)
    
    # Medications
    pdf.set_font("Arial", "B", 12)
    pdf.set_text_color(45, 90, 140)
    pdf.cell(0, 8, "CURRENT MEDICATIONS", ln=True)
    
    pdf.set_font("Arial", "", 10)
    pdf.set_text_color(0, 0, 0)
    meds = patient_data.get("medications", [])
    if meds:
        for med in meds:
            pdf.cell(0, 6, f"• {med}", ln=True)
    else:
        pdf.cell(0, 6, "No medications recorded", ln=True)
    
    pdf.ln(3)
    
    # Risk Flags
    pdf.set_font("Arial", "B", 12)
    pdf.set_text_color(45, 90, 140)
    pdf.cell(0, 8, "IDENTIFIED RISKS", ln=True)
    
    pdf.set_font("Arial", "", 10)
    pdf.set_text_color(0, 0, 0)
    risks = patient_data.get("risk_flags", [])
    if risks:
        for risk in risks:
            pdf.multi_cell(0, 6, f"• {risk}")
    else:
        pdf.cell(0, 6, "No significant risks identified", ln=True)
    
    pdf.ln(3)
    
    # Next Steps
    pdf.set_font("Arial", "B", 12)
    pdf.set_text_color(45, 90, 140)
    pdf.cell(0, 8, "RECOMMENDED NEXT STEPS", ln=True)
    
    pdf.set_font("Arial", "", 10)
    pdf.set_text_color(0, 0, 0)
    steps = patient_data.get("recommended_next_steps", [])
    if steps:
        for step in steps:
            pdf.multi_cell(0, 6, f"• {step}")
    else:
        pdf.cell(0, 6, "Continue standard monitoring", ln=True)
    
    return pdf.output(dest='S').encode('latin-1')

# Function to extract text from PDF
def extract_text_from_pdf(pdf_file):
    try:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
        return text
    except Exception as e:
        st.error(f"Error reading PDF: {str(e)}")
        return ""

# Sidebar
with st.sidebar:
    st.markdown("### Clinical Intelligence Assistant")
    st.divider()
    
    st.markdown("### About")
    st.markdown("""
    Advanced clinical document analysis with:
    
    **Features:**
    - AI-powered extraction
    - Risk scoring (Low/Medium/High)
    - Critical value alerts
    - Drug interaction checking
    - Vital signs visualization
    - Professional PDF export
    
    **Supported formats:**
    - Text (paste directly)
    - PDF files
    """)
    
    st.divider()
    st.markdown("**Status:** Online")
    st.markdown("**Model:** Llama 3.3 70B")

# Header
st.markdown("# Clinical Intelligence Assistant")
st.markdown("Extract patient information and identify clinical risks from documents.")
st.divider()

# Main layout
col_input, col_results = st.columns([1, 1.2], gap="large")

with col_input:
    st.markdown("## 1. Input Document")
    
    # Input method selection - HORIZONTAL
    input_type = st.radio(
        "Choose input method:",
        ["Paste Text", "Upload PDF"],
        label_visibility="collapsed",
        horizontal=True
    )
    
    document_text = ""
    
    # Handle different input types
    if input_type == "Paste Text":
        document_text = st.text_area(
            "Paste clinical document:",
            height=350,
            placeholder="Paste the clinical document here...",
            label_visibility="collapsed"
        )
    
    elif input_type == "Upload PDF":
        pdf_file = st.file_uploader("Upload PDF file", type=['pdf'], label_visibility="collapsed")
        if pdf_file:
            with st.spinner("Extracting text from PDF..."):
                document_text = extract_text_from_pdf(pdf_file)
                if document_text:
                    st.success("PDF text extracted successfully")
    
    st.markdown("")
    
    # Analyze button
    if st.button("Analyze Document", use_container_width=True):
        if not document_text.strip():
            st.error("Please provide a document to analyze")
        else:
            with st.spinner("Processing..."):
                try:
                    # Build message for Groq
                    messages = [
                        {
                            "role": "user",
                            "content": f"""Extract structured clinical information from this document. Return ONLY valid JSON, no markdown formatting.

{{
    "patient_name": "name or 'Not specified'",
    "age": "age or 'Not specified'",
    "gender": "gender or 'Not specified'",
    "chief_complaint": "main complaint",
    "medications": ["med1", "med2"],
    "past_medical_history": ["condition1", "condition2"],
    "vital_signs": {{
        "blood_pressure": "value",
        "heart_rate": "value",
        "temperature": "value"
    }},
    "clinical_summary": "brief summary including current medications and their purpose",
    "risk_flags": ["risk1", "risk2"],
    "recommended_next_steps": ["step1", "step2"],
    "confidence_score": 0.85
}}

Document:
{document_text}"""
                        }
                    ]
                    
                    # Call Groq API
                    response = client.chat.completions.create(
                        model="llama-3.3-70b-versatile",
                        max_tokens=1500,
                        messages=messages
                    )
                    
                    # Parse response
                    response_text = response.choices[0].message.content.strip()
                    
                    # Clean up markdown formatting
                    clean_text = response_text
                    if clean_text.startswith("```"):
                        parts = clean_text.split("```")
                        if len(parts) >= 2:
                            clean_text = parts[1]
                        if clean_text.startswith("json"):
                            clean_text = clean_text[4:]
                    
                    clean_text = clean_text.strip()
                    
                    # Parse JSON
                    try:
                        patient_data = json.loads(clean_text)
                    except json.JSONDecodeError as e:
                        st.error("Could not parse response")
                        st.code(response_text)
                        st.stop()
                    
                    # ===== CALCULATE CLINICAL SCORES & ALERTS =====
                    risk_score = calculate_risk_score(patient_data)
                    risk_level = get_risk_level(risk_score)
                    critical_alerts = check_critical_values(patient_data)
                    drug_interactions = check_drug_interactions(patient_data.get("medications", []))
                    pdf_report = generate_pdf_report(patient_data, risk_level, critical_alerts, drug_interactions)
                    
                    # Display results
                    with col_results:
                        st.markdown('<div class="success-msg">✓ Analysis complete</div>', unsafe_allow_html=True)
                        
                        # RISK SCORE CARD
                        risk_color_class = risk_level[1]
                        st.markdown(f"""
                        <div class="risk-score-card">
                            <div class="risk-score-label">Overall Risk Score</div>
                            <div class="risk-score-value {risk_color_class}">{risk_level[0]}</div>
                            <div style="font-size: 0.875rem; color: #9bc5e6;">({risk_score:.0%} Risk)</div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # CRITICAL ALERTS
                        if critical_alerts:
                            for alert in critical_alerts:
                                st.markdown(f'<div class="critical-alert">{alert}</div>', unsafe_allow_html=True)
                        
                        # DRUG INTERACTIONS
                        if drug_interactions:
                            for interaction in drug_interactions:
                                st.markdown(f'<div class="warning-alert">{interaction}</div>', unsafe_allow_html=True)
                        
                        # Patient info
                        st.markdown("## 2. Patient Summary")
                        name = patient_data.get("patient_name", "N/A")
                        age = patient_data.get("age", "N/A")
                        gender = patient_data.get("gender", "N/A")
                        
                        st.markdown(f"""
                        <div class="patient-card">
                            <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 2rem;">
                                <div class="patient-info">
                                    <div class="patient-label">Name</div>
                                    <div class="patient-value">{name}</div>
                                </div>
                                <div class="patient-info">
                                    <div class="patient-label">Age</div>
                                    <div class="patient-value">{age}</div>
                                </div>
                                <div class="patient-info">
                                    <div class="patient-label">Gender</div>
                                    <div class="patient-value">{gender}</div>
                                </div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Clinical summary
                        st.markdown("## 3. Clinical Summary")
                        summary = patient_data.get("clinical_summary", "No summary")
                        st.markdown(f'<div class="clinical-summary">{summary}</div>', unsafe_allow_html=True)
                        
                        # Current medications
                        st.markdown("## 4. Current Medications")
                        medications = patient_data.get("medications", [])
                        if medications and len(medications) > 0:
                            st.markdown('<div class="medications-section">', unsafe_allow_html=True)
                            for med in medications:
                                st.markdown(f'<div class="med-item">• {med}</div>', unsafe_allow_html=True)
                            st.markdown('</div>', unsafe_allow_html=True)
                        else:
                            st.markdown('<div class="medications-section"><div class="med-item">No medications recorded</div></div>', unsafe_allow_html=True)
                        
                        # Risk flags and next steps
                        col_risks, col_steps = st.columns([1, 1])
                        
                        with col_risks:
                            st.markdown("## 5. Risk Flags")
                            risk_flags = patient_data.get("risk_flags", [])
                            if risk_flags and len(risk_flags) > 0:
                                for risk in risk_flags:
                                    st.markdown(f'<div class="risk-item"><span class="risk-dot risk-dot-high"></span> {risk}</div>', unsafe_allow_html=True)
                            else:
                                st.markdown('<div class="risk-item"><span class="risk-dot risk-dot-low"></span> No critical risks</div>', unsafe_allow_html=True)
                        
                        with col_steps:
                            st.markdown("## 6. Next Steps")
                            next_steps = patient_data.get("recommended_next_steps", [])
                            if next_steps and len(next_steps) > 0:
                                st.markdown('<ul class="steps-list">', unsafe_allow_html=True)
                                for step in next_steps:
                                    st.markdown(f'<li>{step}</li>', unsafe_allow_html=True)
                                st.markdown('</ul>', unsafe_allow_html=True)
                            else:
                                st.markdown('<p style="color: #9bc5e6;">No specific recommendations</p>', unsafe_allow_html=True)
                        
                        # Vital signs
                        st.markdown("## 7. Vital Signs")
                        vitals = patient_data.get("vital_signs", {})
                        bp = vitals.get("blood_pressure", "N/A") if vitals else "N/A"
                        hr = vitals.get("heart_rate", "N/A") if vitals else "N/A"
                        temp = vitals.get("temperature", "N/A") if vitals else "N/A"
                        
                        # Check if critical
                        bp_critical = False
                        if bp != "N/A" and "/" in str(bp):
                            try:
                                sys = int(str(bp).split("/")[0])
                                bp_critical = sys > 180 or sys < 90
                            except:
                                pass
                        
                        bp_class = "vital-critical" if bp_critical else ""
                        
                        st.markdown(f"""
                        <div>
                            <div class="vital-item">
                                <span class="vital-label">Blood Pressure</span>
                                <span class="vital-value {bp_class}">{bp}</span>
                            </div>
                            <div class="vital-item">
                                <span class="vital-label">Heart Rate</span>
                                <span class="vital-value">{hr}</span>
                            </div>
                            <div class="vital-item">
                                <span class="vital-label">Temperature</span>
                                <span class="vital-value">{temp}</span>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Vital Signs Chart
                        if vitals:
                            chart = create_vital_chart(vitals)
                            if chart:
                                st.pyplot(chart, use_container_width=True)
                        
                        # Confidence
                        st.markdown("## 8. Confidence")
                        confidence = patient_data.get("confidence_score", 0)
                        confidence_pct = int(confidence * 100)
                        
                        st.markdown(f"""
                        <div style="text-align: center;">
                            <div class="confidence-value">{confidence_pct}%</div>
                            <div class="confidence-bar">
                                <div class="confidence-fill" style="width: {confidence_pct}%;"></div>
                            </div>
                            <div style="font-size: 0.875rem; color: #9bc5e6;">Analysis Confidence</div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Export Options
                        st.markdown("## 9. Export Report")
                        col_export1, col_export2 = st.columns(2)
                        
                        with col_export1:
                            st.download_button(
                                label="📄 Download PDF Report",
                                data=pdf_report,
                                file_name=f"clinical_report_{patient_data.get('patient_name', 'patient').replace(' ', '_')}.pdf",
                                mime="application/pdf"
                            )
                        
                        with col_export2:
                            st.download_button(
                                label="📋 Download JSON",
                                data=json.dumps(patient_data, indent=2),
                                file_name=f"clinical_data_{patient_data.get('patient_name', 'patient').replace(' ', '_')}.json",
                                mime="application/json"
                            )
                        
                        # Raw JSON
                        with st.expander("View Raw JSON"):
                            st.json(patient_data)
                
                except Exception as e:
                    st.error(f"Error: {str(e)}")

st.markdown('<div class="footer">Clinical Intelligence Assistant | Groq API | Advanced Risk Assessment</div>', unsafe_allow_html=True)
import streamlit as st
import json
from groq import Groq
import PyPDF2
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from io import BytesIO
from datetime import datetime

api_key = st.secrets["GROQ_API_KEY"]
client = Groq(api_key=api_key)

st.set_page_config(
    page_title="Clinical Intelligence Assistant",
    layout="wide",
    initial_sidebar_state="expanded"
)

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
    
    .risk-card-high {
        background: linear-gradient(135deg, #ff6b6b 0%, #ff5252 100%);
        padding: 2rem;
        border-radius: 0.75rem;
        margin-bottom: 1.5rem;
        border-left: 8px solid #ff0000;
        box-shadow: 0 4px 12px rgba(255, 107, 107, 0.4);
    }
    
    .risk-card-medium {
        background: linear-gradient(135deg, #ffd93d 0%, #ffb700 100%);
        padding: 2rem;
        border-radius: 0.75rem;
        margin-bottom: 1.5rem;
        border-left: 8px solid #ff9800;
        box-shadow: 0 4px 12px rgba(255, 215, 61, 0.4);
    }
    
    .risk-card-low {
        background: linear-gradient(135deg, #51cf66 0%, #37b24d 100%);
        padding: 2rem;
        border-radius: 0.75rem;
        margin-bottom: 1.5rem;
        border-left: 8px solid #2f9e44;
        box-shadow: 0 4px 12px rgba(81, 207, 102, 0.4);
    }
    
    .risk-score-number {
        font-size: 3.5rem;
        font-weight: 700;
        color: #ffffff;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    
    .risk-score-label {
        font-size: 1.1rem;
        font-weight: 600;
        color: #ffffff;
        text-align: center;
        margin-bottom: 1rem;
    }
    
    .risk-description {
        font-size: 0.95rem;
        color: #ffffff;
        line-height: 1.6;
        margin-top: 1rem;
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
    
    .risk-high {
        background-color: #ff6b6b;
    }
    
    .risk-low {
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
    
    button {
        background: #2563eb !important;
        color: #ffffff !important;
        border: none !important;
    }
    
    button:hover {
        background: #1d4ed8 !important;
    }
    
    .stButton > button {
        background: #2563eb !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 0.5rem !important;
        padding: 0.875rem 2rem !important;
        font-weight: 700 !important;
        width: 100% !important;
        font-size: 1rem !important;
        transition: all 0.3s ease !important;
    }
    
    .stButton > button:hover {
        background: #1d4ed8 !important;
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.4) !important;
    }
    
    .stButton > button span {
        color: #ffffff !important;
    }
    
    [data-testid="stFileUploadDropzone"] button {
        background: #2563eb !important;
        color: #ffffff !important;
    }
    
    [data-testid="stDownloadButton"] button {
        background: #2563eb !important;
        color: #ffffff !important;
    }
    
    [data-testid="stRadio"] label,
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
    
    .timeline {
        margin: 1rem 0;
    }
    
    .timeline-item {
        display: flex;
        margin-bottom: 1.2rem;
        position: relative;
        padding-left: 2.5rem;
    }
    
    .timeline-marker {
        position: absolute;
        left: 0;
        top: 0;
        width: 24px;
        height: 24px;
        border-radius: 50%;
        background: #2d5a8c;
        border: 3px solid #5ba3d0;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 0.7rem;
        font-weight: bold;
        color: #ffffff;
    }
    
    .timeline-content {
        flex: 1;
    }
    
    .timeline-time {
        font-weight: 700;
        color: #5ba3d0;
        margin-bottom: 0.3rem;
        font-size: 0.95rem;
    }
    
    .timeline-description {
        color: #ffffff;
        font-size: 0.9rem;
        line-height: 1.5;
    }
    
    .timeline-container-high {
        background: transparent;
        border-left: none;
        padding: 0;
        border-radius: 0.5rem;
        margin-top: 1rem;
    }
    
    .timeline-container-medium {
        background: transparent;
        border-left: none;
        padding: 0;
        border-radius: 0.5rem;
        margin-top: 1rem;
    }
    
    .timeline-container-low {
        background: transparent;
        border-left: none;
        padding: 0;
        border-radius: 0.5rem;
        margin-top: 1rem;
    }
</style>
""", unsafe_allow_html=True)

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

def calculate_risk_score(patient_data):
    score = 0
    risk_factors = patient_data.get('risk_flags', [])
    
    critical_keywords = ['acute', 'severe', 'emergency', 'sepsis', 'stroke', 'infarction', 'hemorrhage', 'critical']
    high_keywords = ['hypertension', 'diabetes', 'heart disease', 'elevated', 'abnormal']
    
    for risk in risk_factors:
        risk_lower = risk.lower()
        if any(keyword in risk_lower for keyword in critical_keywords):
            score += 3
        elif any(keyword in risk_lower for keyword in high_keywords):
            score += 1.5
        else:
            score += 1
    
    try:
        age = int(str(patient_data.get('age', '0')).split()[0]) if patient_data.get('age') else 0
        if age > 70:
            score += 1
        elif age > 60:
            score += 0.5
    except:
        pass
    
    return min(round(score, 1), 10)

def get_risk_level(score):
    if score >= 7:
        return "HIGH", "#ff6b6b"
    elif score >= 4:
        return "MEDIUM", "#ffd93d"
    else:
        return "LOW", "#51cf66"

def get_followup_timeline(risk_level, patient_data):
    """Generate follow-up timeline based on risk level"""
    if risk_level == "HIGH":
        return [
            ("Day 1 (TODAY)", "Schedule specialist consultation immediately"),
            ("Day 1", "Order urgent labs if not already done"),
            ("Day 3", "Initial follow-up call from care team"),
            ("Day 7", "First specialist appointment"),
            ("Day 14", "Medication effectiveness review"),
            ("Day 30", "Comprehensive reassessment")
        ]
    elif risk_level == "MEDIUM":
        return [
            ("Day 1-3", "Schedule specialist consultation"),
            ("Day 7", "Initial labs review"),
            ("Day 14", "First follow-up appointment"),
            ("Day 30", "Medication adjustment if needed"),
            ("Day 60", "Progress evaluation"),
            ("Day 90", "Comprehensive reassessment")
        ]
    else:  # LOW
        return [
            ("Week 1", "Schedule routine follow-up"),
            ("Week 2", "Initial check-in"),
            ("Week 4", "Primary care visit"),
            ("Week 8", "Medication effectiveness review"),
            ("Week 12", "Progress evaluation"),
            ("Month 6", "Routine reassessment")
        ]

def generate_pdf_report(patient_data, risk_score, risk_level):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.5*inch, bottomMargin=0.5*inch)
    elements = []
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#2d5a8c'),
        spaceAfter=12,
        alignment=1
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#2d5a8c'),
        spaceAfter=10,
        spaceBefore=10
    )
    
    elements.append(Paragraph("Clinical Intelligence Report", title_style))
    elements.append(Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
    elements.append(Spacer(1, 0.3*inch))
    
    elements.append(Paragraph("Risk Stratification", heading_style))
    elements.append(Paragraph(f"Risk Score: {risk_score}/10 ({risk_level})", styles['Normal']))
    elements.append(Spacer(1, 0.2*inch))
    
    elements.append(Paragraph("Patient Information", heading_style))
    patient_info = [
        ['Name', patient_data.get('patient_name', 'N/A')],
        ['Age', patient_data.get('age', 'N/A')],
        ['Gender', patient_data.get('gender', 'N/A')]
    ]
    patient_table = Table(patient_info, colWidths=[2*inch, 4*inch])
    patient_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e8f0f7')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey)
    ]))
    elements.append(patient_table)
    elements.append(Spacer(1, 0.2*inch))
    
    elements.append(Paragraph("Chief Complaint", heading_style))
    chief_complaint = patient_data.get('chief_complaint', 'N/A')
    elements.append(Paragraph(str(chief_complaint), styles['Normal']))
    elements.append(Spacer(1, 0.2*inch))
    
    elements.append(Paragraph("Clinical Summary", heading_style))
    clinical_summary = patient_data.get('clinical_summary', 'N/A')
    elements.append(Paragraph(str(clinical_summary), styles['Normal']))
    elements.append(Spacer(1, 0.2*inch))
    
    elements.append(Paragraph("Current Medications", heading_style))
    medications = patient_data.get('medications', [])
    if medications:
        for med in medications:
            elements.append(Paragraph(f"• {str(med)}", styles['Normal']))
    else:
        elements.append(Paragraph("No medications recorded", styles['Normal']))
    elements.append(Spacer(1, 0.2*inch))
    
    elements.append(Paragraph("Vital Signs", heading_style))
    vitals = patient_data.get('vital_signs', {})
    vital_data = [
        ['Blood Pressure', str(vitals.get('blood_pressure', 'N/A'))],
        ['Heart Rate', str(vitals.get('heart_rate', 'N/A'))],
        ['Temperature', str(vitals.get('temperature', 'N/A'))]
    ]
    vital_table = Table(vital_data, colWidths=[2*inch, 4*inch])
    vital_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e8f0f7')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey)
    ]))
    elements.append(vital_table)
    elements.append(Spacer(1, 0.2*inch))
    
    elements.append(Paragraph("Risk Flags", heading_style))
    risk_flags = patient_data.get('risk_flags', [])
    if risk_flags:
        for risk in risk_flags:
            elements.append(Paragraph(f"⚠ {str(risk)}", styles['Normal']))
    else:
        elements.append(Paragraph("No critical risks identified", styles['Normal']))
    elements.append(Spacer(1, 0.2*inch))
    
    elements.append(Paragraph("Recommended Next Steps", heading_style))
    next_steps = patient_data.get('recommended_next_steps', [])
    if next_steps:
        for step in next_steps:
            elements.append(Paragraph(f"→ {str(step)}", styles['Normal']))
    else:
        elements.append(Paragraph("No specific recommendations", styles['Normal']))
    elements.append(Spacer(1, 0.2*inch))
    
    elements.append(Paragraph("Confidence Score", heading_style))
    confidence = patient_data.get('confidence_score', 0)
    confidence_pct = int(confidence * 100)
    elements.append(Paragraph(f"{confidence_pct}% - Analysis Confidence", styles['Normal']))
    
    doc.build(elements)
    buffer.seek(0)
    return buffer

with st.sidebar:
    st.markdown("### Clinical Intelligence Assistant")
    st.divider()
    
    st.markdown("### About")
    st.markdown("""
    This tool extracts structured clinical data from documents using Groq AI.
    
    **Supported formats:**
    - Text (paste directly)
    - PDF files
    
    **What it does:**
    - Extracts patient information
    - Identifies risk flags
    - Summarizes clinical findings
    - Lists current medications
    - Provides risk stratification
    - Provides confidence scoring
    - Generates follow-up timelines
    """)
    
    st.divider()
    st.markdown("**Status:** Online")
    st.markdown("**Model:** Llama 3.3 70B")

st.markdown("# Clinical Intelligence Assistant")
st.markdown("Extract patient information and identify clinical risks from documents.")
st.divider()

col_input, col_results = st.columns([1, 1.2], gap="large")

with col_input:
    st.markdown("## Input Document")
    
    input_type = st.radio(
        "Choose input method:",
        ["Paste Text", "Upload PDF"],
        label_visibility="collapsed",
        horizontal=True
    )
    
    document_text = ""
    
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
    
    if st.button("Analyze Document", use_container_width=True):
        if not document_text.strip():
            st.error("Please provide a document to analyze")
        else:
            with st.spinner("Processing..."):
                try:
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
                    
                    response = client.chat.completions.create(
                        model="llama-3.3-70b-versatile",
                        max_tokens=1500,
                        messages=messages
                    )
                    
                    response_text = response.choices[0].message.content.strip()
                    
                    clean_text = response_text
                    if clean_text.startswith("```"):
                        parts = clean_text.split("```")
                        if len(parts) >= 2:
                            clean_text = parts[1]
                        if clean_text.startswith("json"):
                            clean_text = clean_text[4:]
                    
                    clean_text = clean_text.strip()
                    
                    try:
                        patient_data = json.loads(clean_text)
                    except json.JSONDecodeError as e:
                        st.error("Could not parse response")
                        st.code(response_text)
                        st.stop()
                    
                    risk_score = calculate_risk_score(patient_data)
                    risk_level, risk_color = get_risk_level(risk_score)
                    
                    st.markdown('<div class="success-msg">✓ Analysis complete</div>', unsafe_allow_html=True)
                    
                    st.markdown("")
                    
                    st.markdown("## Risk Stratification")
                    if risk_level == "HIGH":
                        st.markdown(f"""
                        <div class="risk-card-high">
                            <div class="risk-score-number">{risk_score}/10</div>
                            <div class="risk-score-label">🚨 HIGH RISK PATIENT</div>
                            <div class="risk-description">
                                <strong>Requires immediate clinical review and intervention.</strong><br><br>
                                This patient presents with multiple risk factors that warrant urgent attention. 
                                Schedule specialist consultation and consider escalation protocols.
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                    elif risk_level == "MEDIUM":
                        st.markdown(f"""
                        <div class="risk-card-medium">
                            <div class="risk-score-number">{risk_score}/10</div>
                            <div class="risk-score-label">⚠️ MEDIUM RISK PATIENT</div>
                            <div class="risk-description">
                                <strong>Schedule specialist consultation within 1-2 weeks.</strong><br><br>
                                This patient has several risk factors that need careful monitoring. 
                                Implement structured follow-up plan and regular check-ins.
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown(f"""
                        <div class="risk-card-low">
                            <div class="risk-score-number">{risk_score}/10</div>
                            <div class="risk-score-label">✓ LOW RISK PATIENT</div>
                            <div class="risk-description">
                                <strong>Routine follow-up and preventive care recommended.</strong><br><br>
                                This patient is stable with minimal acute risk factors. 
                                Continue regular monitoring and maintain current treatment plan.
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    st.markdown("")
                    st.markdown("## Follow-up Timeline")
                    timeline = get_followup_timeline(risk_level, patient_data)
                    
                    if risk_level == "HIGH":
                        timeline_class = "timeline-container-high"
                    elif risk_level == "MEDIUM":
                        timeline_class = "timeline-container-medium"
                    else:
                        timeline_class = "timeline-container-low"
                    
                    st.markdown(f'<div class="{timeline_class}">', unsafe_allow_html=True)
                    st.markdown('<div class="timeline">', unsafe_allow_html=True)
                    
                    for idx, (time, action) in enumerate(timeline, 1):
                        st.markdown(f'''
                        <div class="timeline-item">
                            <div class="timeline-marker">{idx}</div>
                            <div class="timeline-content">
                                <div class="timeline-time">{time}</div>
                                <div class="timeline-description">{action}</div>
                            </div>
                        </div>
                        ''', unsafe_allow_html=True)
                    
                    st.markdown('</div>', unsafe_allow_html=True)
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                    with col_results:
                        pdf_buffer = generate_pdf_report(patient_data, risk_score, risk_level)
                        patient_name = patient_data.get('patient_name', 'Report').replace(" ", "_")
                        st.download_button(
                            label="📥 Download Report (PDF)",
                            data=pdf_buffer,
                            file_name=f"Clinical_Report_{patient_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                            mime="application/pdf",
                            use_container_width=True
                        )
                        
                        st.markdown("")
                        
                        st.markdown("## Patient Summary")
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
                        
                        st.markdown("## Clinical Summary")
                        summary = patient_data.get("clinical_summary", "No summary")
                        st.markdown(f'<div class="clinical-summary">{summary}</div>', unsafe_allow_html=True)
                        
                        st.markdown("## Current Medications")
                        medications = patient_data.get("medications", [])
                        if medications and len(medications) > 0:
                            st.markdown('<div class="medications-section">', unsafe_allow_html=True)
                            for med in medications:
                                st.markdown(f'<div class="med-item">• {med}</div>', unsafe_allow_html=True)
                            st.markdown('</div>', unsafe_allow_html=True)
                        else:
                            st.markdown('<div class="medications-section"><div class="med-item">No medications recorded</div></div>', unsafe_allow_html=True)
                        
                        col_risks, col_steps = st.columns([1, 1])
                        
                        with col_risks:
                            st.markdown("## Risk Flags")
                            risk_flags = patient_data.get("risk_flags", [])
                            if risk_flags and len(risk_flags) > 0:
                                for risk in risk_flags:
                                    st.markdown(f'<div class="risk-item"><span class="risk-dot risk-high"></span> {risk}</div>', unsafe_allow_html=True)
                            else:
                                st.markdown('<div class="risk-item"><span class="risk-dot risk-low"></span> No critical risks</div>', unsafe_allow_html=True)
                        
                        with col_steps:
                            st.markdown("## Next Steps")
                            next_steps = patient_data.get("recommended_next_steps", [])
                            if next_steps and len(next_steps) > 0:
                                st.markdown('<ul class="steps-list">', unsafe_allow_html=True)
                                for step in next_steps:
                                    st.markdown(f'<li>{step}</li>', unsafe_allow_html=True)
                                st.markdown('</ul>', unsafe_allow_html=True)
                            else:
                                st.markdown('<p style="color: #9bc5e6;">No specific recommendations</p>', unsafe_allow_html=True)
                        
                        st.markdown("## Vital Signs")
                        vitals = patient_data.get("vital_signs", {})
                        bp = vitals.get("blood_pressure", "N/A") if vitals else "N/A"
                        hr = vitals.get("heart_rate", "N/A") if vitals else "N/A"
                        temp = vitals.get("temperature", "N/A") if vitals else "N/A"
                        
                        st.markdown(f"""
                        <div>
                            <div class="vital-item">
                                <span class="vital-label">Blood Pressure</span>
                                <span class="vital-value">{bp}</span>
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
                        
                        st.markdown("## Confidence")
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
                        
                        with st.expander("View JSON"):
                            st.json(patient_data)
                
                except Exception as e:
                    st.error(f"Error: {str(e)}")

st.markdown('<div class="footer">Clinical Intelligence Assistant | Groq AI</div>', unsafe_allow_html=True)
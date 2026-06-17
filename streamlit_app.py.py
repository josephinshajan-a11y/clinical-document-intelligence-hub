import streamlit as st
import json
from groq import Groq
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get API key from Streamlit secrets (for hosted) or .env (for local)
if "GROQ_API_KEY" in st.secrets:
    api_key = st.secrets["GROQ_API_KEY"]
else:
    api_key = os.getenv("GROQ_API_KEY")

# Initialize Groq - using OpenAI-compatible API
client = Groq(api_key=api_key)

# Page config
st.set_page_config(
    page_title="Clinical Intelligence Assistant",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom styling - Dark Blue & White Theme with BRIGHT VISIBLE TEXT
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
    
    /* Sidebar text - BRIGHT WHITE */
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
    
    /* Main headings - BRIGHT WHITE AND BOLD */
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
    
    /* Patient card - white background */
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
    
    /* Clinical summary */
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
    
    /* Risk items */
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
    
    /* Steps list */
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
    
    /* Vital signs */
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
    
    /* Confidence */
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
    
    /* Success message */
    .success-msg {
        background: #1a5f3f;
        border-left: 5px solid #51cf66;
        padding: 1rem;
        border-radius: 0.5rem;
        color: #51cf66 !important;
        margin-bottom: 1rem;
        font-weight: 600;
    }
    
    /* Button */
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
    
    /* Radio buttons */
    [data-testid="stRadio"] {
        color: #ffffff !important;
    }
    
    [data-testid="stRadio"] label {
        color: #ffffff !important;
    }
    
    [data-testid="stRadio"] span {
        color: #ffffff !important;
    }
    
    /* Text areas and inputs */
    [data-testid="stTextArea"] textarea {
        background-color: #0f1823 !important;
        color: #ffffff !important;
        border: 2px solid #2d5a8c !important;
    }
    
    /* Divider */
    hr {
        border-color: #2d5a8c !important;
    }
    
    /* Footer */
    .footer {
        text-align: center;
        padding: 2rem 0;
        border-top: 2px solid #2d5a8c;
        color: #9bc5e6;
        font-size: 0.875rem;
        margin-top: 3rem;
    }
    
    /* Expander */
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

# Sidebar - info and navigation
with st.sidebar:
    st.markdown("### Clinical Intelligence Assistant")
    st.divider()
    
    st.markdown("### About")
    st.markdown("""
    This tool extracts structured clinical data from unstructured documents using Groq AI.
    
    **What it does:**
    - Extracts patient information
    - Identifies risk flags
    - Summarizes clinical findings
    - Provides confidence scoring
    """)
    
    st.divider()
    st.markdown("**Status:** Online")
    st.markdown("**Model:** Llama 3.3 70B")

# Header
st.markdown("# Clinical Intelligence Assistant")
st.markdown("Extract patient information and identify clinical risks from documents.")
st.divider()

# Main layout - input on left, results on right
col_input, col_results = st.columns([1, 1.2], gap="large")

with col_input:
    st.markdown("## 1. Input Document")
    
    # Radio button for input method
    input_type = st.radio(
        "Choose input method:",
        ["Paste Text", "Upload File"],
        label_visibility="collapsed",
        horizontal=True
    )
    
    # Get document text based on input method
    if input_type == "Paste Text":
        document_text = st.text_area(
            "Paste clinical document:",
            height=350,
            placeholder="Paste the clinical document here...",
            label_visibility="collapsed"
        )
    else:
        # Handle file upload
        uploaded_file = st.file_uploader("Upload text file", type=['txt'], label_visibility="collapsed")
        if uploaded_file:
            document_text = uploaded_file.read().decode('utf-8')
        else:
            document_text = ""
    
    st.markdown("")
    # Button to trigger analysis
    if st.button("Analyze Document", use_container_width=True):
        # Validate input
        if not document_text.strip():
            st.error("Please provide a document to analyze")
        else:
            # Process the document
            with st.spinner("Processing..."):
                try:
                    # Call Groq API to extract clinical data
                    response = client.chat.completions.create(
                        model="llama-3.3-70b-versatile",
                        max_tokens=1500,
                        messages=[
                            {
                                "role": "user",
                                "content": f"""Extract structured clinical information from this document. Return ONLY valid JSON, no markdown formatting, no code blocks.

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
    "clinical_summary": "brief summary",
    "risk_flags": ["risk1", "risk2"],
    "recommended_next_steps": ["step1", "step2"],
    "confidence_score": 0.85
}}

Document:
{document_text}"""
                            }
                        ]
                    )
                    
                    # Parse the response
                    response_text = response.choices[0].message.content.strip()
                    
                    # Clean up response - remove markdown code blocks
                    clean_text = response_text
                    if clean_text.startswith("```"):
                        parts = clean_text.split("```")
                        if len(parts) >= 2:
                            clean_text = parts[1]
                        if clean_text.startswith("json"):
                            clean_text = clean_text[4:]
                    
                    clean_text = clean_text.strip()
                    
                    # Try to parse JSON
                    try:
                        patient_data = json.loads(clean_text)
                    except json.JSONDecodeError as e:
                        st.error("Could not parse response")
                        st.code(response_text)
                        st.stop()
                    
                    # Display results in right column
                    with col_results:
                        st.markdown('<div class="success-msg">✓ Analysis complete</div>', unsafe_allow_html=True)
                        
                        # Patient info card
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
                        
                        # Risk flags and next steps in two columns
                        col_risks, col_steps = st.columns([1, 1])
                        
                        with col_risks:
                            st.markdown("## 4. Risk Flags")
                            risk_flags = patient_data.get("risk_flags", [])
                            if risk_flags and len(risk_flags) > 0:
                                for risk in risk_flags:
                                    st.markdown(f'<div class="risk-item"><span class="risk-dot risk-high"></span> {risk}</div>', unsafe_allow_html=True)
                            else:
                                st.markdown('<div class="risk-item"><span class="risk-dot risk-low"></span> No critical risks</div>', unsafe_allow_html=True)
                        
                        with col_steps:
                            st.markdown("## 5. Next Steps")
                            next_steps = patient_data.get("recommended_next_steps", [])
                            if next_steps and len(next_steps) > 0:
                                st.markdown('<ul class="steps-list">', unsafe_allow_html=True)
                                for step in next_steps:
                                    st.markdown(f'<li>{step}</li>', unsafe_allow_html=True)
                                st.markdown('</ul>', unsafe_allow_html=True)
                            else:
                                st.markdown('<p style="color: #9bc5e6;">No specific recommendations</p>', unsafe_allow_html=True)
                        
                        # Vital signs
                        st.markdown("## 6. Vital Signs")
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
                        
                        # Confidence score
                        st.markdown("## 7. Confidence")
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
                        
                        # Show raw JSON if needed
                        with st.expander("View JSON"):
                            st.json(patient_data)
                
                except Exception as e:
                    st.error(f"Error: {str(e)}")

st.markdown('<div class="footer">Clinical Intelligence Assistant | Groq API</div>', unsafe_allow_html=True)
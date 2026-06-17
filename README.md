# Clinical Document Intelligence Hub

**What**: A tool that reads clinical documents and pulls out patient information, scores how serious the case is, and suggests when they should follow up.

**Why**: Doctors and nurses waste hours reading the same patient documents over and over. This saves that time and catches risky cases that might get missed.

## The Approach

We read a clinical note and extract the important parts: patient name, medications, vital signs, what the doctors flagged as concerns. Then we score how serious the case is based on keywords (chest pain + diabetes + smoking = risky). Finally we suggest follow-up timing based on that score. The whole thing takes 5-10 seconds.

## What We Used

- **AI**: Llama 3.3 70B language model via Groq API (free tier available)
- **Website**: Streamlit (simple, deploys free to Streamlit Cloud)
- **PDF Reading**: PyPDF2 for text, OCR for scanned images
- **Reports**: ReportLab to generate downloadable PDFs
- **Code**: Python 3.10+

## Setup & Usage

**Live (no setup needed)**: https://josephin-clinical-ai-demo-2026.streamlit.app/

**Local setup**:
git clone https://github.com/josephinshajan-a11y/clinical-document-intelligence-hub.git

cd clinical-document-intelligence-hub

python -m venv venv && source venv/bin/activate

pip install -r requirements.txt

echo "GROQ_API_KEY=your_key_from_console.groq.com" > .env

streamlit run streamlit_app.py

**How to use**: Paste a clinical note or upload a PDF → Click "Analyze Document" → See the risk score, medications, problems, and follow-up plan → Download the PDF.

## Example: Marcus Thompson (52M, Chest Pain)

**Input Document**:
PATIENT: Marcus Thompson, 52-year-old male

COMPLAINT: Acute chest pain for 2 hours, radiating to left arm
HISTORY: Type 2 Diabetes, Hypertension, Obesity (BMI 32), former smoker (quit 2015)

VITALS: BP 162/96, HR 96, Temp 37.2°C

MEDICATIONS: Metformin 1000mg twice daily, Lisinopril 20mg daily,

Atorvastatin 80mg daily, Aspirin 325mg daily

ASSESSMENT: Rule out acute coronary syndrome

PLAN: EKG, troponin, cardiology consultation, ICU monitoring

**What We Extract**:

- Patient: Marcus Thompson, 52M
- Risk Score: **7.5/10 - HIGH RISK** (urgent specialist needed)
- Medications: Metformin, Lisinopril, Atorvastatin, Aspirin
- Risk Flags: Acute chest pain, diabetes, high BP (uncontrolled), obesity, smoking history
- Follow-up: Day 1 - cardiology consult + labs, Day 3 - care team check-in, Day 7 - specialist appointment, Day 14 - med review, Day 30 - reassessment
- Confidence: 94%

## Risk Scoring

We look at keywords in the document: "stroke", "sepsis", "acute" = +3 points each. "Diabetes", "hypertension" = +1.5 points each. Other concerns = +1 point. Age over 70 = +1 extra point. Then we classify: ≥7 is HIGH RISK (urgent), 4-7 is MEDIUM (soon), <4 is LOW (routine).

## Our Assumptions

- Input documents have real clinical information (not random text)
- Users will review the AI's output before using it (it's a starting point, not final truth)
- Keyword scoring is good enough for a proof of concept (better systems exist but take more time to build)
- Users understand this is a demo, not approved for actual patient care
- Clinicians will always make the final decision, not the AI

## Contributing

Found a bug? Open an issue on GitHub. Think the risk scoring is wrong? Let us know - those thresholds can be adjusted. Want to add code? Fork the repo and send a pull request.

## Important Note

This is a demonstration only. Before using in a hospital you'd need: doctor validation, regulatory approval, ethics board sign-off, proper insurance, and HIPAA compliance. The AI's output is a recommendation to review, not a clinical decision.

---
  
**GitHub**: https://github.com/josephinshajan-a11y/clinical-document-intelligence-hub  
**Live App**: https://josephin-clinical-ai-demo-2026.streamlit.app/

